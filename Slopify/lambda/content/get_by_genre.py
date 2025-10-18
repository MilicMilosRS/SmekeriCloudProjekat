import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
genre_content_table = dynamodb.Table(os.environ["GENRE_TABLE"])

def handle(event, context):
    genre_name = event.get("queryStringParameters", {}).get("genre", None)
    print(event.get("queryStringParameters"))
    print(genre_name)

    items = []
    if not genre_name:
        response = genre_content_table.scan()
        items = response.get("Items", [])
    else:
        genre_name = genre_name.strip().upper()
        response = genre_content_table.query(
            KeyConditionExpression=Key("genreName").eq(genre_name)
        )
        items = response.get("Items", [])

    res = [{"contentId": item["contentId"],
            "name": item.get("contentName", ""),
            } for item in items]

    return {'statusCode': 200, 'body': json.dumps(res)}