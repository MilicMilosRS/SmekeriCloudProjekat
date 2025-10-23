import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import json

dynamodb = boto3.resource("dynamodb")
user_feed_table = dynamodb.Table(os.environ["USER_FEED_TABLE"])

def handler(event, context):
    email = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('email')
    if not email:
        return {
            "statusCode": 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Error getting email"})
        }

    #Delete old feed
    songs = []
    feed = user_feed_table.query(KeyConditionExpression=Key("userEmail").eq(email))["Items"]
    if feed:
        with user_feed_table.batch_writer() as batch:
            for item in feed:
                songs.append({
                    'id': item['songId'],
                    'name': item['songName'],
                    'score': float(item['score']),
                })

    #Sort and return
    sorted_songs = sorted(songs, key=lambda x: x["score"], reverse=True)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(sorted_songs)
    }