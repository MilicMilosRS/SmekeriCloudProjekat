from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_lambda_event_sources as event_source,
    RemovalPolicy
)
from constructs import Construct

class FeedStack(Stack):

    def __init__(self, scope: Construct, id: str, core_stack, song_stack, genre_stack, artist_stack, user_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        #Table
        self.user_feed = dynamodb.Table(
            self, "UserFeedTable",
            table_name="UserFeed",
            partition_key=dynamodb.Attribute(name="userEmail", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #Lambda
        self.lambda_generate_feed = _lambda.Function(
            self, "GenerateFeedHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/feed"),
            handler="generate_feed.handler",
            environment={
                "SONG_TABLE": song_stack.song_table.table_name,
                "ARTIST_SONGS_TABLE": artist_stack.artist_songs.table_name,
                "GENRE_CONTENT_TABLE": genre_stack.genre_content.table_name,
                "USER_SUBSCRIPTIONS_TABLE": user_stack.user_subs.table_name,
                "GRADE_TABLE": user_stack.user_grades.table_name,
                "USER_FEED_TABLE": self.user_feed.table_name,
                "HISTORY_TABLE": song_stack.listening_history.table_name,
            }
        )

        self.lambda_on_song_upload = _lambda.Function(
            self, "FeedOnSongUploadHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/feed"),
            handler="on_song_upload.handler",
            environment={
                "ARTIST_SONGS_TABLE": artist_stack.artist_songs.table_name,
                "GENRE_CONTENT_TABLE": genre_stack.genre_content.table_name,
                "USER_SUBSCRIPTIONS_TABLE": user_stack.user_subs.table_name,
                "FEED_GENERATOR_LAMBDA": self.lambda_generate_feed.function_name
            }
        )

        self.lambda_on_rating_changed = _lambda.Function(
            self, "FeedOnRatingChanged",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/feed"),
            handler="on_rating_changed.handler",
            environment={
                "FEED_GENERATOR_LAMBDA": self.lambda_generate_feed.function_name
            }
        )

        self.lambda_on_subscription_changed = _lambda.Function(
            self, "FeedOnSubscriptionChanged",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/feed"),
            handler="on_subscribtion_changed.handler",
            environment={
                "FEED_GENERATOR_LAMBDA": self.lambda_generate_feed.function_name
            }
        )

        self.lambda_on_song_viewed = _lambda.Function(
            self, "FeedOnSongViewed",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/feed"),
            handler="on_song_viewed.handler",
            environment={
                "FEED_GENERATOR_LAMBDA": self.lambda_generate_feed.function_name
            }
        )

        #Callback
        self.lambda_on_song_upload.add_event_source(
            event_source.DynamoEventSource(
                song_stack.song_table,
                starting_position=_lambda.StartingPosition.LATEST,
                bisect_batch_on_error=True,
                retry_attempts=2,
            )
        )

        self.lambda_on_rating_changed.add_event_source(
            event_source.DynamoEventSource(
                user_stack.user_grades,
                starting_position=_lambda.StartingPosition.LATEST,
                bisect_batch_on_error=True,
                retry_attempts=2,
            )
        )

        self.lambda_on_subscription_changed.add_event_source(
            event_source.DynamoEventSource(
                user_stack.user_subs,
                starting_position=_lambda.StartingPosition.LATEST,
                bisect_batch_on_error=True,
                retry_attempts=2,
            )
        )
        
        self.lambda_on_song_viewed.add_event_source(
            event_source.DynamoEventSource(
                song_stack.listening_history,
                starting_position=_lambda.StartingPosition.LATEST,
                bisect_batch_on_error=True,
                retry_attempts=2,
            )
        )

        #Grants
        song_stack.song_table.grant_read_data(self.lambda_generate_feed)
        song_stack.listening_history.grant_read_data(self.lambda_generate_feed)
        artist_stack.artist_songs.grant_read_data(self.lambda_generate_feed)
        genre_stack.genre_content.grant_read_data(self.lambda_generate_feed)
        user_stack.user_subs.grant_read_data(self.lambda_generate_feed)
        user_stack.user_grades.grant_read_data(self.lambda_generate_feed)
        self.user_feed.grant_write_data(self.lambda_generate_feed)

        song_stack.song_table.grant_stream_read(self.lambda_on_song_upload)
        artist_stack.artist_songs.grant_read_data(self.lambda_on_song_upload)
        genre_stack.genre_content.grant_read_data(self.lambda_on_song_upload)
        user_stack.user_subs.grant_read_data(self.lambda_on_song_upload)
        self.lambda_generate_feed.grant_invoke(self.lambda_on_song_upload)
        self.lambda_generate_feed.grant_invoke(self.lambda_on_rating_changed)
        self.lambda_generate_feed.grant_invoke(self.lambda_on_subscription_changed)
        self.lambda_generate_feed.grant_invoke(self.lambda_on_song_viewed)