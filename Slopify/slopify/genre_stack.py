from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_lambda_event_sources as events,
    RemovalPolicy
)
from constructs import Construct

class GenreStack(Stack):

    def __init__(self, scope: Construct, id: str, core, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Table
        self.genre_content = dynamodb.Table(
            self, "GenreContentTable",
            table_name="GenreContents",
            partition_key=dynamodb.Attribute(name="genreName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            stream=dynamodb.StreamViewType.NEW_IMAGE,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.genre_content.add_global_secondary_index(
            index_name="ContentTypeIndex",
            
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="genreName", type=dynamodb.AttributeType.STRING)
        )

        self.genres_table = dynamodb.Table(
            self, "GenresTable",
            table_name="Genres",
            partition_key=dynamodb.Attribute(name="genreName", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambda
        self.lambda_update_genres = _lambda.Function(
            self, "GenreStreamHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/genre"),
            handler="handle_stream.handle",
            environment={
                "GENRES_TABLE": self.genres_table.table_name
            }
        )

        self.lambda_get_content = _lambda.Function(
            self, "GetContentByGenre",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/content"),
            handler="get_by_genre.handle",
            environment={'GENRE_TABLE': self.genre_content.table_name}
        )

        self.lambda_get_all = _lambda.Function(
            self, "GetAllGenres",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/genre"),
            handler="get_all.handler",
            environment={'GENRE_TABLE': self.genres_table.table_name}
        )

        self.genre_content.grant_read_data(self.lambda_get_content)
        self.genres_table.grant_read_write_data(self.lambda_update_genres)
        self.genres_table.grant_read_data(self.lambda_get_all)

        self.lambda_update_genres.add_event_source(
            events.DynamoEventSource(
                self.genre_content,
                starting_position=_lambda.StartingPosition.LATEST,
                batch_size=10,
                retry_attempts=2
            )
        )