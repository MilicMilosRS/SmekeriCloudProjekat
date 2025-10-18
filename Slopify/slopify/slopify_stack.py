from aws_cdk import (
    Duration,
    Stack,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_apigateway as apigw,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cognito as cognito
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

        #CloudFront
        distribution = cloudfront.Distribution(
            self, "SlopifyDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object=None  # optional
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

        #GSI for reverse lookup: 
        genre_content.add_global_secondary_index(
            index_name="ContentTypeIndex",
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="genreName", type=dynamodb.AttributeType.STRING)
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

        user_subs.add_global_secondary_index(
            index_name="ContentIdIndex",
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
        )

        #Cognito User Pool
        user_pool = cognito.UserPool(
            self, "SlopifyUserPool",
            user_pool_name="SlopifyUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY
        )

        #Cognito App Client
        user_pool_client = cognito.UserPoolClient(
            self, "NewUserPoolClient",
            user_pool=user_pool
        )

        #User groups
        admin_group = cognito.CfnUserPoolGroup(
            self, "AdminsGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="admins",
            description="System admins",
            precedence=1
        )

        user_group = cognito.CfnUserPoolGroup(
            self, "UsersGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="users",
            description="Regular users",
            precedence=2
        )

        #Pre sign up lambda to verify email instantly
        pre_sign_up_lambda = _lambda.Function(
            self, "PreSignUpHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/auth"),
            handler="pre_sign_up.handle"
        )

        user_pool.add_trigger(
            cognito.UserPoolOperation.PRE_SIGN_UP,
            pre_sign_up_lambda
        )

        #Post register lambda
        post_confirmation_lambda = _lambda.Function(
            self, "PostConfirmationHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/auth"),
            handler="post_confirmation.handle"
        )

        user_pool.add_trigger(
            cognito.UserPoolOperation.POST_CONFIRMATION,
            post_confirmation_lambda
        )

        post_confirmation_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminAddUserToGroup"],
            resources=[f"*"]
        ))

        #
        #Api stuff
        #
        api = apigw.RestApi(self, "SlopifyApi",
            rest_api_name="Slopify API",
            description="Super cool API"
        )

        #
        #Song lambdas
        #
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
                'ARTIST_SONGS': artist_songs.table_name,
                'GENRE_TABLE': genre_content.table_name,
                'CLOUDFRONT_URL': distribution.domain_name
            }
        )

        #Song API
        api_songs = api.root.add_resource("songs")
        api_songs.add_method("GET", apigw.LambdaIntegration(get_songs_lambda))
        api_songs.add_method("POST", apigw.LambdaIntegration(create_song_lambda))

        #Song lambda grants
        song_table.grant_read_data(get_songs_lambda)

        song_table.grant_read_write_data(create_song_lambda)
        artist_table.grant_read_data(create_song_lambda)
        artist_songs.grant_read_write_data(create_song_lambda)
        genre_content.grant_read_write_data(create_song_lambda)
        bucket.grant_read_write(create_song_lambda)

        #
        #Artist lambdas
        #
        create_artist_lambda = _lambda.Function(
            self, "CreateArtistHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/artist"),
            handler="create.handle",
            environment={
                'ARTIST_TABLE': artist_table.table_name,
                'GENRE_TABLE': genre_content.table_name,
            }
        )

        #Artist API
        api_artists = api.root.add_resource("artists")
        api_artists.add_method("POST", apigw.LambdaIntegration(create_artist_lambda))

        #Artist lambda grants
        artist_table.grant_read_write_data(create_artist_lambda)
        genre_content.grant_read_write_data(create_artist_lambda)

        #
        #Content lambdas
        #
        get_content_by_genre_lambda = _lambda.Function(
            self, "GetContentByGenre",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/content"),
            handler="get_by_genre.handle",
            environment={
                'GENRE_TABLE': genre_content.table_name,
            }
        )

        #Content API
        api_content = api.root.add_resource("contents")
        api_content.add_method("GET", apigw.LambdaIntegration(get_content_by_genre_lambda))

        #Content lambda grants
        genre_content.grant_read_data(get_content_by_genre_lambda)

        from aws_cdk import CfnOutput
        CfnOutput(self, "CloudFrontURL", value=f"https://{distribution.domain_name}")
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)