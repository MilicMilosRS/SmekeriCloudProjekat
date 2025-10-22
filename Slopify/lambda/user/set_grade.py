import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
grade_table = dynamodb.Table(os.environ["GRADE_TABLE"])

ALLOWED_CONTENT_TYPES = {"ARTIST", "GENRE", "SONG", "ALBUM"}

def handler(event, context):
    try:
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        email = claims.get("email")
        if not email:
            return _response(401, {"error": "Unauthorized"})

        body_raw = event.get("body", "{}")
        body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

        contentType = body.get("contentType", "").upper()
        contentId = body.get("contentId", "")
        grade = body.get("grade")

        if not (contentType and contentId and grade is not None):
            return _response(400, {"error": "Missing contentType, contentId, or grade"})

        if contentType not in ALLOWED_CONTENT_TYPES:
            return _response(400, {"error": f"Invalid contentType. Must be one of: {', '.join(ALLOWED_CONTENT_TYPES)}"})

        if not isinstance(grade, int) or grade < 1 or grade > 5:
            return _response(400, {"error": "Grade must be an integer between 1 and 5"})

        full_content_id = f"{contentType}#{contentId}"

        response = grade_table.query(
            KeyConditionExpression=Key("userId").eq(email) & Key("contentId").eq(full_content_id)
        )
        items = response.get("Items", [])
        if items:
            return _response(400, {"error": "User already graded this content"})

        item = {
            "userId": email,
            "contentId": full_content_id,
            "grade": grade
        }
        grade_table.put_item(Item=item)

        return _response(200, {"message": "Grade submitted successfully"})

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