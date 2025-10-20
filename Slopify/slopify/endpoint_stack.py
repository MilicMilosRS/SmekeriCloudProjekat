from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class EndpointStack(Stack):

    def __init__(self, scope: Construct, id: str, song_stack, artist_stack, genre_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        
        # API Gateway
        self.api = apigw.RestApi(self, "SlopifyApi",
            rest_api_name="Slopify API",
            description="Main Slopify API Gateway"
        )

        
        # API
        songs_resource = self.api.root.add_resource("songs")
        songs_resource.add_method("GET", apigw.LambdaIntegration(song_stack.lambda_get_songs))
        songs_resource.add_method("POST", apigw.LambdaIntegration(song_stack.lambda_create_song))

        contents_resource = self.api.root.add_resource("contents")
        contents_resource.add_method("GET", apigw.LambdaIntegration(genre_stack.lambda_get_content))

        artists_resource = self.api.root.add_resource("artists")
        artists_resource.add_method("POST", apigw.LambdaIntegration(artist_stack.lambda_create_artist))


        CfnOutput(self, "ApiUrl", value=self.api.url)

