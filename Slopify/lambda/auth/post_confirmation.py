import boto3
import os

def handle(event, context):
    event["response"]["autoConfirmUser"] = True
    event["response"]["autoVerifyEmail"] = True
    
    client = boto3.client('cognito-idp')
    user_pool_id = event['userPoolId']
    username = event["userName"]

    client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=username,
        GroupName="users"
    )

    return event