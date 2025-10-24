from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3_assets as s3_assets,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct


class SongStack(Stack):

    def __init__(self, scope: Construct, id: str, core, artist_stack, genre_stack, notification_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        ####### Queues #######
        self.prepare_audio_queue = sqs.Queue(
            self, "PrepareAudioQueue",
            queue_name="PrepareAudioQueue",
            visibility_timeout=Duration.minutes(5)
        )

        self.transcription_queue = sqs.Queue(
            self, "TranscriptionQueue",
            queue_name="SongTranscriptionQueue",
            visibility_timeout=Duration.minutes(5)
        )

        ####### DynamoDB Tables #######
        self.song_table = dynamodb.Table(
            self, "SongTable",
            table_name="Songs",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            stream=dynamodb.StreamViewType.NEW_IMAGE,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.listening_history = dynamodb.Table(
            self, "UserListeningTable",
            table_name="UserListeningHistory",
            partition_key=dynamodb.Attribute(name="userEmail", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="songId", type=dynamodb.AttributeType.STRING),
            stream=dynamodb.StreamViewType.NEW_IMAGE,
            removal_policy=RemovalPolicy.DESTROY
        )

        ####### Lambda Layers #######
        ffmpeg_asset = s3_assets.Asset(
            self, "FfmpegLayerAsset",
            path="backend/lambda_layer/ffmpeg_layer.zip"
        )

        self.ffmpeg_layer = _lambda.LayerVersion(
            self, "FfmpegLambdaLayer",
            code=_lambda.Code.from_bucket(ffmpeg_asset.bucket, ffmpeg_asset.s3_object_key),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        vosk_asset = s3_assets.Asset(
            self, "VoskLayerAsset",
            path="backend/lambda_layer/vosk_layer.zip"
        )

        self.vosk_layer = _lambda.LayerVersion(
            self, "VoskLambdaLayer",
            code=_lambda.Code.from_bucket(vosk_asset.bucket, vosk_asset.s3_object_key),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        ####### Lambdas #######

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
                'OUTPUT_BUCKET': core.bucket.bucket_name,
                'PREPARE_AUDIO_QUEUE_URL': self.prepare_audio_queue.queue_url,
                'TOPIC_ARN': notification_stack.notification_topic.topic_arn,
            },
            timeout=Duration.seconds(20),
            memory_size=1024
        )
        self.lambda_create_song.add_to_role_policy(
            iam.PolicyStatement(actions=["sns:Publish", "sqs:SendMessage"], resources=['*'])
        )

        self.lambda_get_details = _lambda.Function(
            self, "GetSongDetailsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="get_details.handle",
            environment={
                'SONG_TABLE': self.song_table.table_name,
                'HISTORY_TABLE': self.listening_history.table_name,
            }
        )

        # Prepare audio
        self.lambda_prepare_audio = _lambda.Function(
            self, "PrepareAudioHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="prepare_audio.handle",
            environment={
                "OUTPUT_BUCKET": core.bucket.bucket_name,
                "TRANSCRIPTION_QUEUE_URL": self.transcription_queue.queue_url
            },
            timeout=Duration.seconds(20),
            memory_size=1024,
            layers=[self.ffmpeg_layer]
        )

        self.lambda_prepare_audio.add_event_source(
            lambda_event_sources.SqsEventSource(self.prepare_audio_queue)
        )

        self.lambda_prepare_audio.add_permission(
            "AllowSqsInvoke",
            principal=iam.ServicePrincipal("sqs.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=self.prepare_audio_queue.queue_arn
        )

        self.lambda_prepare_audio.add_to_role_policy(
            iam.PolicyStatement(
                actions=["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes",
                         "s3:GetObject", "s3:PutObject"],
                resources=["*"]
            )
        )

        # Transcribe song
        self.lambda_transcribe_song = _lambda.Function(
            self, "TranscribeSongHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="transcribe_song.handle",
            environment={
                'SONG_TABLE': self.song_table.table_name,
                'OUTPUT_BUCKET': core.bucket.bucket_name
            },
            timeout=Duration.seconds(300),
            memory_size=2048,
            layers=[self.vosk_layer]
        )

        self.lambda_transcribe_song.add_event_source(
            lambda_event_sources.SqsEventSource(self.transcription_queue)
        )

        self.lambda_transcribe_song.add_to_role_policy(
            iam.PolicyStatement(
                actions=["transcribe:*", "s3:GetObject", "s3:PutObject",
                         "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                resources=["*"]
            )
        )

        self.lambda_transcription_complete = _lambda.Function(
            self, "TranscriptionCompleteHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/song"),
            handler="transcription_complete.handle",
            environment={"SONG_TABLE": self.song_table.table_name}
        )

        ####### Grants #######
        # DynamoDB
        self.song_table.grant_read_data(self.lambda_get_songs)
        self.song_table.grant_read_write_data(self.lambda_create_song)
        self.song_table.grant_read_data(self.lambda_get_details)
        self.song_table.grant_read_write_data(self.lambda_transcribe_song)
        self.song_table.grant_read_write_data(self.lambda_transcription_complete)

        self.listening_history.grant_write_data(self.lambda_get_details)

        artist_stack.artist_table.grant_read_data(self.lambda_create_song)
        artist_stack.artist_songs.grant_read_write_data(self.lambda_create_song)
        genre_stack.genre_content.grant_read_write_data(self.lambda_create_song)

        # S3 Buckets
        core.bucket.grant_read_write(self.lambda_prepare_audio)
        core.bucket.grant_read_write(self.lambda_create_song)
        core.bucket.grant_read(self.lambda_transcription_complete)

        # SQS Queues
        self.transcription_queue.grant_consume_messages(self.lambda_transcribe_song)
        self.transcription_queue.grant_send_messages(self.lambda_prepare_audio)

        self.prepare_audio_queue.grant_send_messages(self.lambda_create_song)
        self.prepare_audio_queue.grant_consume_messages(self.lambda_prepare_audio)
