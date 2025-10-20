from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy
)
from constructs import Construct

class AlbumStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Table
        album_table = dynamodb.Table(
            self, "AlbumTable",
            table_name="Album",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,  # Auto delete on stack destroy
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        album_table.add_global_secondary_index(
            index_name="ArtistIndex",
            partition_key=dynamodb.Attribute(name="artistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )
