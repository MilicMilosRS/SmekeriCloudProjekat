import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
user_subscriptions_table = dynamodb.Table(os.environ["SUBSCRIBE_TABLE"])

#body contains {contentId, contentType}
#contentType = genre or song or artist
def handler(event, context):
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        email = claims.get('email')

        if not email:
            return {
                "statusCode": 401,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
                "body": json.dumps({"error": "Unauthorized: no email in claims"})
            }

        body_raw = event.get("body", "{}")
        if isinstance(body_raw, dict):
            body = body_raw
        else:
            body = json.loads(body_raw)

        contentType = body.get('contentType', "")
        contentId = body.get('contentId', "")

        if not (contentType and contentId):
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
                "body": json.dumps({"error": "Missing contentType or contentId"})
            }

        #checking if subscription exists
        response = user_subscriptions_table.query(
            KeyConditionExpression=Key('userId').eq(email) &
                                   Key('contentId').eq(contentType + "#" + contentId)
        )
        items = response.get("Items", [])

        if not items:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
                "body": json.dumps({"error": "Subscription not found"})
            }

        user_subscriptions_table.delete_item(
            Key={
                "userId": email,
                "contentId": contentType + "#" + contentId
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            "body": json.dumps({"message": "Unsubscribed successfully"})
        }

    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            "body": json.dumps({"error": str(e)})
        }