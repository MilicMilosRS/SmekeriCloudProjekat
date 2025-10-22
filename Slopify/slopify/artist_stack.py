from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy
)
from constructs import Construct

class ArtistStack(Stack):

    def __init__(self, scope: Construct, id: str, core, genre_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Tables
        self.artist_table = dynamodb.Table(
            self, "ArtistTable",
            table_name="Artists",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.artist_songs = dynamodb.Table(
            self, "ArtistSongsTable",
            table_name="ArtistsSongs",
            partition_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.artist_songs.add_global_secondary_index(
            index_name="SongIdIndex",
            partition_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING)
        )

        # Lambda
        self.lambda_create_artist = _lambda.Function(
            self, "CreateArtistHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/artist"),
            handler="create.handle",
            environment={
                'ARTIST_TABLE': self.artist_table.table_name,
                'GENRE_TABLE': genre_stack.genre_content.table_name,
            }
        )

        self.lambda_get_all_artists = _lambda.Function(
            self, "GetAllArtistsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/artist"),
            handler="get_all.handle",
            environment={
                'ARTIST_TABLE': self.artist_table.table_name,
            }
        )

        self.lambda_get_artist_details = _lambda.Function(
            self, "GetArtistDetailsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/artist"),
            handler="get_details.handle",
            environment={
                'ARTIST_TABLE': self.artist_table.table_name,
                'GENRE_TABLE': genre_stack.genre_content.table_name,
                'ARTIST_SONGS_TABLE': self.artist_songs.table_name
            }
        )

        self.artist_table.grant_read_write_data(self.lambda_create_artist)
        self.artist_table.grant_read_data(self.lambda_get_artist_details)
        self.artist_table.grant_read_data(self.lambda_get_all_artists)
        self.artist_songs.grant_read_data(self.lambda_get_artist_details)

        genre_stack.genre_content.grant_read_data(self.lambda_get_artist_details)
        genre_stack.genre_content.grant_read_write_data(self.lambda_create_artist)