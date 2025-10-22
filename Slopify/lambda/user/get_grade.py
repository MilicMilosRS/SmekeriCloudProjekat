import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
grade_table = dynamodb.Table(os.environ["GRADE_TABLE"])

def handler(event, context):
    try:
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        email = claims.get("email")
        if not email:
            return _response(401, {"error": "Unauthorized"})

        body_raw = event.get("body", "{}")
        body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

        contentType = body.get("contentType", "")
        contentId = body.get("contentId", "")

        if not (contentType and contentId):
            return _response(400, {"error": "Missing contentType or contentId"})

        full_content_id = f"{contentType}#{contentId}"

        response = grade_table.query(
            KeyConditionExpression=Key("userId").eq(email) & Key("contentId").eq(full_content_id)
        )

        items = response.get("Items", [])
        if not items:
            #not yet graded
            return _response(200, {"grade": 0})

        grade = items[0].get("grade", 0)
        return _response(200, {"grade": grade})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return _response(500, {"error": str(e)})

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
        },
        "body": json.dumps(body),
    }