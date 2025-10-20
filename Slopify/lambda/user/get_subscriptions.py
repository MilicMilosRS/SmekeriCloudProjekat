import json
import os
from boto3.dynamodb.conditions import Key
import boto3


dynamodb = boto3.resource("dynamodb")
subscriptions_table = dynamodb.Table(os.environ["SUBSCRIPTION_TABLE"])

def handler(event, context):
    claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
    username = claims.get('cognito:username')
    
    response = subscriptions_table.query(
        KeyConditionExpression=Key("username").eq(username)
    )
    items = response.get("Items", [])

    res = [{"contentId": item["contentId"],
            "name": item.get("contentName", ""),
            } for item in items]

    return {"statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            "body": json.dumps(res)}
