from aws_cdk import (
    Stack,
    Duration,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda_event_sources as event_sources,
    CfnOutput
)
from constructs import Construct

class NotificationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.notification_queue = sqs.Queue(
            self, "NotificationQueue",
            visibility_timeout=Duration.seconds(30)
        )

        self.notification_topic = sns.Topic(
            self, "SlopifyNotificationTopic",
            display_name="Slopify Notifications"
        )

        self.notification_topic.add_subscription(
            subs.EmailSubscription("your.email@example.com")
        )

        self.notify_lambda = _lambda.Function(
            self, "NotifyLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="notify.handler",
            code=_lambda.Code.from_asset("lambda/notifications"),
            environment={
                "TOPIC_ARN": self.notification_topic.topic_arn,
                "SUBSCRIPTIONS_TABLE": "UserSubscriptions"
            }
        )

        self.notify_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:Query",
                    "dynamodb:GetItem",
                    "dynamodb:Scan"
                ],
                resources=["*"] 
            )
        )

        self.notification_topic.grant_publish(self.notify_lambda)

        self.notify_lambda.add_event_source(
            event_sources.SqsEventSource(self.notification_queue)
        )

        CfnOutput(self, "NotificationQueueUrl", value=self.notification_queue.queue_url)
        CfnOutput(self, "NotificationTopicArn", value=self.notification_topic.topic_arn)
