from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_apigateway as apigw,
    CfnOutput
)
from constructs import Construct

class CoreStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        from aws_cdk.aws_s3 import Bucket

        # S3 Bucket
        self.bucket = s3.Bucket(
            self, "SlopifyBucket",
            # bucket_name="slopify-bucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # CloudFront
        self.distribution = cloudfront.Distribution(
            self, "SlopifyDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            )
        )

        CfnOutput(self, "CloudFrontURL", value=f"https://{self.distribution.domain_name}")
