from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_apigateway as apigw,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_iam as iam
)
from constructs import Construct

class SlopifyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #S3
        bucket = s3.Bucket(
            self, "SlopifyBucket",
            bucket_name="slopify-bucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        #Dynamo

        #User Table
        user_table = dynamodb.Table(
            self, "UserTable",
            table_name="User",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #Song Table
        song_table = dynamodb.Table(
            self, "SongTable",
            table_name="Song",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #Artist Table
        artist_table = dynamodb.Table(
            self, "ArtistTable",
            table_name="Artist",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #ArtistSongs Table
        artist_songs = dynamodb.Table(
            self, "ArtistSongsTable",
            table_name="ArtistSongs",
            partition_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #GSI for reverse lookup: get artists for song
        artist_songs.add_global_secondary_index(
            index_name="SongIdIndex",
            partition_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING)
        )

        #GenreContent Table
        genre_content = dynamodb.Table(
            self, "GenreContentTable",
            table_name="GenreContent",
            partition_key=dynamodb.Attribute(name="genreName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #Album Table
        album_table = dynamodb.Table(
            self, "AlbumTable",
            table_name="Album",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #ArtistAlbums Table
        artist_albums = dynamodb.Table(
            self, "ArtistAlbumsTable",
            table_name="ArtistAlbums",
            partition_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="albumId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        artist_albums.add_global_secondary_index(
            index_name="AlbumIdIndex",
            partition_key=dynamodb.Attribute(name="albumId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING)
        )

        #AlbumSongs Table
        album_songs = dynamodb.Table(
            self, "AlbumSongsTable",
            table_name="AlbumSongs",
            partition_key=dynamodb.Attribute(name="albumId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        album_songs.add_global_secondary_index(
            index_name="SongIdIndex",
            partition_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="albumId", type=dynamodb.AttributeType.STRING)
        )

        #UserSubscriptions Table
        user_subs = dynamodb.Table(
            self, "UserSubscriptionsTable",
            table_name="UserSubscriptions",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #ContentSubscribers Table
        content_subs = dynamodb.Table(
            self, "ContentSubscribersTable",
            table_name="ContentSubscribers",
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #Api stuff

        api = apigw.RestApi(self, "SlopifyApi",
            rest_api_name="Slopify API",
            description="Super cool API"
        )

        #Song lambdas
        
        get_songs_lambda = _lambda.Function(
            self, "GetSongsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            environment={'TABLE_NAME': song_table.table_name},
            handler="get_all.get_all"
        )

        create_song_lambda = _lambda.Function(
            self, "CreateSongHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="create.handle",
            environment={
                'SONG_TABLE': song_table.table_name,
                'ARTIST_TABLE': artist_table.table_name,
                'ARTIST_SONGS': artist_songs.table_name
            }
        )

        #Song API

        api_songs = api.root.add_resource("songs")
        api_songs.add_method("GET", apigw.LambdaIntegration(get_songs_lambda))
        api_songs.add_method("POST", apigw.LambdaIntegration(create_song_lambda))

        #Song table lambdas

        song_table.grant_read_data(get_songs_lambda)
        song_table.grant_read_write_data(create_song_lambda)
        
        bucket.grant_read_write(create_song_lambda)