from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy
)
from constructs import Construct

class AlbumStack(Stack):

    def __init__(self, scope: Construct, id: str, song_stack, genre_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Table
        self.album_table = dynamodb.Table(
            self, "AlbumTable",
            table_name="Album",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,  # Auto delete on stack destroy
        )

        self.album_table.add_global_secondary_index(
            index_name="ArtistIndex",
            partition_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.album_songs_table = dynamodb.Table(
            self, "AlbumSongsTable",
            table_name="AlbumSongs",
            partition_key=dynamodb.Attribute(name="albumId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
        )

        #Lambdas
        self.lambda_create_album = _lambda.Function(
            self, "CreateAlbumHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/album"),
            handler="create.handle",
            environment={
                "GENRE_CONTENT_TABLE": genre_stack.genre_content.table_name,
                "ALBUMS_TABLE": self.album_table.table_name,
                "ALBUM_SONGS_TABLE": self.album_songs_table.table_name,
                "SONG_TABLE": song_stack.song_table.table_name
            }
        )

        genre_stack.genres_table.grant_read_write_data(self.lambda_create_album)
        genre_stack.genre_content.grant_read_write_data(self.lambda_create_album)
        self.album_table.grant_read_write_data(self.lambda_create_album)
        self.album_songs_table.grant_read_write_data(self.lambda_create_album)
        song_stack.song_table.grant_read_data(self.lambda_create_album)