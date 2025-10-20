import json
import os
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb")
user_subscriptions_table = dynamodb.Table(os.environ["SUBSCRIBE_TABLE"])

#Body contains {contentId, contentType}
#contentType = genre or song or artist
def handle(event, context):
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        username = claims.get('cognito:username')
        
        body_raw = event.get("body", "{}")
        if isinstance(body_raw, dict):
            body = body_raw
        else:
            body = json.loads(body_raw)

        contentType = body.get('contentType', "")
        contentId = body.get('contentId', "")
        if not (contentType and contentId):
            return {"statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                    }
                }

        response = user_subscriptions_table.query(
                KeyConditionExpression=Key('username').eq(username) &
                                     Key('contentId').eq(body.get('contentType', "") + body.get('contentId', ""))
            )
        items = response.get("Items", [])
        if items != []:
            return {"statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                }
            }

        return {"statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            }
        }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
