import boto3

def handle(event, context):
    client = boto3.client('cognito-idp')
    user_pool_id = event['userPoolId']
    email = event['request']['userAttributes']['email']

    #check if user with this email already exists
    response = client.list_users(
        UserPoolId=user_pool_id,
        Filter=f'email = "{email}"'
    )

    if len(response['Users']) > 0:
        raise Exception(f"User with email {email} already exists")

    event["response"]["autoConfirmUser"] = True
    event["response"]["autoVerifyEmail"] = True
    return event