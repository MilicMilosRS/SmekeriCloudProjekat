from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

from slopify import notification_stack

class EndpointStack(Stack):

    def __init__(self, scope: Construct, id: str, song_stack, artist_stack, genre_stack, user_stack, auth_stack, notification_stack, album_stack, feed_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        
        # API Gateway
        self.api = apigw.RestApi(self, "SlopifyApi",
            rest_api_name="Slopify API",
            description="Main Slopify API Gateway",
            deploy=True,
            deploy_options=apigw.StageOptions(stage_name="dev"),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET", "OPTIONS", "PUT", "POST", "DELETE"],
                allow_headers=["Content-Type", "Authorization"],
            )
        )

        self.notification_stack = notification_stack
        self.authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[auth_stack.user_pool],
            authorizer_name="SlopifyCognitoAuthorizer"
        )
        
        #API
        #Songs
        songs_resource = self.api.root.add_resource("songs")
        songs_resource.add_method("GET", apigw.LambdaIntegration(song_stack.lambda_get_songs))
        songs_resource.add_method("POST",
            apigw.LambdaIntegration(song_stack.lambda_create_song),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
            )
        songs_id_resource = songs_resource.add_resource("{id}")
        songs_id_resource.add_method(
            "GET", apigw.LambdaIntegration(song_stack.lambda_get_details),                         
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
            )

        #content
        contents_resource = self.api.root.add_resource("contents")
        contents_resource.add_method("GET", apigw.LambdaIntegration(genre_stack.lambda_get_content))

        #Genres
        genre_resource = self.api.root.add_resource("genres")
        genre_resource.add_method("GET", apigw.LambdaIntegration(genre_stack.lambda_get_all))

        #Artists
        artists_resource = self.api.root.add_resource("artists")
        artists_resource.add_method("GET", apigw.LambdaIntegration(artist_stack.lambda_get_all_artists))
        artists_resource.add_method("POST",
            apigw.LambdaIntegration(artist_stack.lambda_create_artist),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
            )
        artists_id_resource = artists_resource.add_resource("{id}")
        artists_id_resource.add_method("GET", apigw.LambdaIntegration(artist_stack.lambda_get_artist_details))

        #Users
        user_resource = self.api.root.add_resource("user")
        user_sub_resourse = user_resource.add_resource("subscriptions")
        user_resource.add_method(
            "GET", apigw.LambdaIntegration(user_stack.lambda_get_user_data),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer)
        user_sub_resourse.add_method(
            "GET", apigw.LambdaIntegration(user_stack.lambda_get_subscriptions),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer)
        user_sub_resourse.add_method(
            "POST", apigw.LambdaIntegration(user_stack.lambda_subscribe),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer)
        user_sub_resourse.add_method(
            "DELETE",
            apigw.LambdaIntegration(user_stack.lambda_unsubscribe),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
        )
        user_sub_check_resource = user_sub_resourse.add_resource("check")
        user_sub_check_resource.add_method(
            "POST",
            apigw.LambdaIntegration(user_stack.lambda_is_subscribed),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
        )
        user_feed_resource = user_resource.add_resource("feed")
        user_feed_resource.add_method(
            "GET",
            apigw.LambdaIntegration(feed_stack.lambda_get_feed),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
        )

        #Grades
        grades_resource = self.api.root.add_resource("grades")
        grades_resource.add_method(
            "POST",
            apigw.LambdaIntegration(user_stack.lambda_set_grade),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
        )
        grades_resource.add_method(
            "GET",
            apigw.LambdaIntegration(user_stack.lambda_get_grade),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
        )

        #Albums
        albums_resource = self.api.root.add_resource("albums")
        albums_resource.add_method(
            "POST", apigw.LambdaIntegration(album_stack.lambda_create_album),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=self.authorizer
            )
        albums_id_resource = albums_resource.add_resource("{id}")
        albums_id_resource.add_method("GET", apigw.LambdaIntegration(album_stack.lambda_get_details))

        #Notification
        notifications_resource = self.api.root.add_resource("notifications")
        notifications_resource.add_method(
            "POST",
            apigw.LambdaIntegration(self.notification_stack.notify_lambda),
        )
        
        CfnOutput(self, "ApiUrl", value=self.api.url)

