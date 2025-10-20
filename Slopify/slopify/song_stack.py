from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy
)
from constructs import Construct

class SongStack(Stack):

    def __init__(self, scope: Construct, id: str, core, artist_stack, genre_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Table
        self.song_table = dynamodb.Table(
            self, "SongTable",
            table_name="Songs",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambdas
        self.lambda_get_songs = _lambda.Function(
            self, "GetSongsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="get_all.get_all",
            environment={'TABLE_NAME': self.song_table.table_name}
        )

        self.lambda_create_song = _lambda.Function(
            self, "CreateSongHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="create.handle",
            environment={
                'SONG_TABLE': self.song_table.table_name,
                'ARTIST_TABLE': artist_stack.artist_table.table_name,
                'ARTIST_SONGS': artist_stack.artist_songs.table_name,
                'GENRE_TABLE': genre_stack.genre_content.table_name,
                'CLOUDFRONT_URL': core.distribution.domain_name,
                'BUCKET_NAME': core.bucket.bucket_name
            }
        )

        self.lambda_get_details = _lambda.Function(
            self, "GetSongDetailsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="get_details.handle",
            environment={
                'SONG_TABLE': self.song_table.table_name,
            }
        )

        # Grants
        self.song_table.grant_read_data(self.lambda_get_songs)
        self.song_table.grant_read_write_data(self.lambda_create_song)
        self.song_table.grant_read_data(self.lambda_get_details)
        artist_stack.artist_table.grant_read_data(self.lambda_create_song)
        artist_stack.artist_songs.grant_read_write_data(self.lambda_create_song)
        genre_stack.genre_content.grant_read_write_data(self.lambda_create_song)
        core.bucket.grant_read_write(self.lambda_create_song)