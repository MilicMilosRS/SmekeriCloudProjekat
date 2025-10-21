from aws_cdk import (
    RemovalPolicy,
    Stack,
    Duration,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda_event_sources as event_sources,
    aws_dynamodb as dynamodb,
    CfnOutput
)
from constructs import Construct

class NotificationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.subscriptions_table = dynamodb.Table(
            self, "SubscriptionsTable",
            table_name="Subscriptions",
            partition_key=dynamodb.Attribute(
                name="contentId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )


        self.notification_queue = sqs.Queue(
            self, "NotificationQueue",
            visibility_timeout=Duration.seconds(30)
        )

        self.notification_topic = sns.Topic(
            self, "SlopifyNotificationTopic",
            display_name="Slopify Notifications"
        )

        self.notification_topic.add_subscription(
            subs.EmailSubscription("mirkodjukic23@gmail.com")
        )

        self.notify_lambda = _lambda.Function(
            self, "NotifyLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="notify.handle",
            code=_lambda.Code.from_asset("lambda/notifications"),
            environment={
                "TOPIC_ARN": self.notification_topic.topic_arn,
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name
            },
                timeout=Duration.seconds(15),
                memory_size=512
        )

        self.notify_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:Query",
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "ses:SendEmail", 
                    "ses:SendRawEmail"
                ],
                resources=["*"] 
            )
        )

        self.notification_topic.grant_publish(self.notify_lambda)

        CfnOutput(self, "NotificationQueueUrl", value=self.notification_queue.queue_url)
        CfnOutput(self, "NotificationTopicArn", value=self.notification_topic.topic_arn)
        CfnOutput(self, "SubscriptionsTableName", value=self.subscriptions_table.table_name)
