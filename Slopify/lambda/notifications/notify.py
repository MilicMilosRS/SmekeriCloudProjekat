import os
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TOPIC_ARN = os.environ['TOPIC_ARN']
SUBS_TABLE = os.environ['SUBSCRIPTIONS_TABLE']
subscriptions_table = dynamodb.Table(SUBS_TABLE)

def handler(event, context):
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
            IndexName = "contentId-userId-index",
            KeyConditionExpression=Key('contentId').eq(content_id)

        )
        subscribers = response.get('Items', [])
        if not subscribers:
            continue

        for user in subscribers:
            email = user.get('email')
            username = user.get('username','unknown_user')
            if email:
                sns.publish(
                    TopicArn=TOPIC_ARN,
                    Message=f"New content drop for user {username},\n\n New {content_type} content published: {content_name}!11!!!!1!1!!1!!!",
                    Subject=f"New slop just just dropped: {content_type.title()}",
                )
        
    return {"status": "ok"}
