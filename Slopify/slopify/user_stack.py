from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy
)
from constructs import Construct

class UserStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        #table
        self.user_subs = dynamodb.Table(
            self, "UserSubscriptionsTable",
            table_name="UserSubscriptions",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY )
        self.user_subs.add_global_secondary_index(
            index_name="ContentIdIndex",
            partition_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            )
        
        self.user_grades = dynamodb.Table(
            self, "UserGradesTable",
            table_name="UserGrades",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="contentId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        
        #lambdas
        self.lambda_get_user_data = _lambda.Function(
            self, "GetUserDataHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            handler="get_user_data.handler",
        )

        self.lambda_get_subscriptions = _lambda.Function(
            self, "GetSubscriptionsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            environment={"SUBSCRIPTION_TABLE": self.user_subs.table_name},
            handler="get_subscriptions.handler",
        )

        self.lambda_subscribe = _lambda.Function(
            self, "SubscribeHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            environment={"SUBSCRIBE_TABLE": self.user_subs.table_name},
            handler="subscribe.handler",
        )

        self.lambda_unsubscribe = _lambda.Function(
            self, "UnsubscribeHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            environment={"SUBSCRIBE_TABLE": self.user_subs.table_name},
            handler="unsubscribe.handler",
        )

        self.lambda_is_subscribed = _lambda.Function(
            self, "IsSubscribedHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            environment={"SUBSCRIBE_TABLE": self.user_subs.table_name},
            handler="is_subscribed.handler",
        )

        self.lambda_get_grade = _lambda.Function(
            self, "GetGradeHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            environment={"GRADE_TABLE": self.user_grades.table_name},
            handler="get_grade.handler",
        )
        self.lambda_set_grade = _lambda.Function(
            self, "SetGradeHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/user"),
            environment={"GRADE_TABLE": self.user_grades.table_name},
            handler="set_grade.handler",
        )

        #grants
        self.user_subs.grant_read_data(self.lambda_get_subscriptions)
        self.user_subs.grant_read_write_data(self.lambda_subscribe)
        self.user_subs.grant_read_write_data(self.lambda_unsubscribe)
        self.user_subs.grant_read_data(self.lambda_is_subscribed)

        self.user_grades.grant_read_data(self.lambda_get_grade)
        self.user_grades.grant_read_write_data(self.lambda_set_grade)
        