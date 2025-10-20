import os
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name='eu-central-1')

SUBS_TABLE = os.environ['SUBSCRIPTIONS_TABLE']
subscriptions_table = dynamodb.Table(SUBS_TABLE)
FROM_EMAIL = "your_verified_email@example.com"

def handle(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        content_id = body['content_id']
        content_name = body.get('content_name', 'New content')

        if content_id.startswith("SONG#"):
            content_type = "song"
        elif content_id.startswith("ARTIST#"):
            content_type = "artist"
        elif content_id.startswith("GENRE#"):
            content_type = "genre"
        else:
            print(f"Unknown content type for content: {content_id}")
            continue

        response = subscriptions_table.query(
            IndexName="contentId-userId-index",
            KeyConditionExpression=Key('contentId').eq(content_id)
        )

        subscribers = response.get('Items', [])
        if not subscribers:
            continue

        for user in subscribers:
            email = user.get('email')
            username = user.get('username', 'unknown_user')
            if email:
                ses.send_email(
                    Source=FROM_EMAIL,
                    Destination={"ToAddresses": [email]},
                    Message={
                        "Subject": {
                            "Data": f"New slop just dropped: {content_type.title()}"
                        },
                        "Body": {
                            "Text": {
                                "Data": f"New content drop for user {username}!\n\nNew {content_type} content published: {content_name}!"
                            }
                        }
                    }
                )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Headers": "Content-Type,Authorization"
        },
        "body": json.dumps({"message": "Notification sent"})
    }
