import boto3

def handle(event, context):
    client = boto3.client('cognito-idp')
    user_pool_id = event['userPoolId']
    username = event["userName"]

    # Add user to group
    client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=username,
        GroupName="users"
    )

    return event