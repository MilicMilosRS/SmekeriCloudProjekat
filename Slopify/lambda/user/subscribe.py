import json
import os
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb")
user_subscriptions_table = dynamodb.Table(os.environ["SUBSCRIBE_TABLE"])

#Body contains {contentId, contentType, contentName}
#contentType = genre or song or artist
def handler(event, context):
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        email = claims.get('email')
        
        #parsing json
        body_raw = event.get("body", "{}")
        if isinstance(body_raw, dict):
            body = body_raw
        else:
            body = json.loads(body_raw)

        contentType = body.get('contentType', "")
        contentId = body.get('contentId', "")
        contentName = body.get('contentName', "")
        if not (contentType and contentId and contentName):
            return {"statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                    }
                }

        #checking if subscription already exists
        response = user_subscriptions_table.query(
                KeyConditionExpression=Key('userId').eq(email) &
                                     Key('contentId').eq(contentType + "#" + contentId))
        items = response.get("Items", [])
        if items != []:
            return {"statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                }
            }
        
        item = {
            "userId": email,
            "contentId": contentType + "#" + contentId,
            "contentName": contentName
        }
        user_subscriptions_table.put_item(Item=item)

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
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
