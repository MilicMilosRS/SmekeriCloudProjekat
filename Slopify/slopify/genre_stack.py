from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
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
            removal_policy=RemovalPolicy.DESTROY
        )

        self.genre_content.add_global_secondary_index(
            index_name="ContentTypeIndex",
            
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="genreName", type=dynamodb.AttributeType.STRING)
        )

        # Lambda
        self.lambda_get_content = _lambda.Function(
            self, "GetContentByGenre",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/content"),
            handler="get_by_genre.handle",
            environment={'GENRE_TABLE': self.genre_content.table_name}
        )

        self.genre_content.grant_read_data(self.lambda_get_content)