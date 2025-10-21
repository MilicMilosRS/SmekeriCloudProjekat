from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_notifications as s3n,
    aws_apigateway as apigw,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct
import boto3


from constructs import Construct

class SongStack(Stack):

    def __init__(self, scope: Construct, id: str, core, artist_stack, genre_stack, notification_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.transcription_queue = sqs.Queue(
            self, "TranscriptionQueue",
            queue_name="SongTranscriptionQueue",
            visibility_timeout=Duration.minutes(5)
        )

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
                'BUCKET_NAME': core.bucket.bucket_name,
                'TRANSCRIPTION_QUEUE_URL': self.transcription_queue.queue_url,
                'TOPIC_ARN': notification_stack.notification_topic.topic_arn,
            },
            timeout=Duration.seconds(20),
            memory_size=1024
        )
        self.lambda_create_song.add_to_role_policy(
            iam.PolicyStatement(
                actions=["sns:Publish", "sqs:SendMessage"],
                resources=['*']
            )
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
        #Transcription


        self.lambda_transcribe_song= _lambda.Function(
            self,"TranscribeSongHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="transcribe_song.handle",
            environment={
                'SONG_TABLE':self.song_table.table_name,
                'OUTPUT_BUCKET': core.bucket.bucket_name
            },
            timeout=Duration.seconds(15),
            memory_size=1024
        )


        #Transcription completion
        self.lambda_transcription_complete= _lambda.Function(
            self,"TranscriptionCompleteHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="transcription_complete.handle",
            environment={"SONG_TABLE":self.song_table.table_name}
        )
        bucket = s3.Bucket.from_bucket_arn(self, "ImportedBucket", core.bucket.bucket_arn)
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.lambda_transcription_complete),
            s3.NotificationKeyFilter(prefix="transcriptions/")
        )



        self.transcription_queue.grant_consume_messages(self.lambda_transcribe_song)

        self.lambda_transcribe_song.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "transcribe:*",
                    "s3:GetObject",
                    "s3:PutObject",
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes"
                ],
                resources=["*"]
            )
        )

        self.lambda_transcribe_song.add_event_source(
            lambda_event_sources.SqsEventSource(self.transcription_queue)
        )

        # Grants
        self.song_table.grant_read_data(self.lambda_get_songs)
        self.song_table.grant_read_write_data(self.lambda_create_song)
        self.transcription_queue.grant_send_messages(self.lambda_create_song)
        self.transcription_queue.grant_consume_messages(self.lambda_transcribe_song)
        self.song_table.grant_read_data(self.lambda_get_details)
        self.song_table.grant_read_write_data(self.lambda_transcribe_song)
        self.song_table.grant_read_write_data(self.lambda_transcription_complete)
        artist_stack.artist_table.grant_read_data(self.lambda_create_song)
        artist_stack.artist_songs.grant_read_write_data(self.lambda_create_song)
        genre_stack.genre_content.grant_read_write_data(self.lambda_create_song)
        core.bucket.grant_read_write(self.lambda_create_song)
        core.bucket.grant_read_write(self.lambda_transcribe_song)
        core.bucket.grant_read(self.lambda_transcription_complete)