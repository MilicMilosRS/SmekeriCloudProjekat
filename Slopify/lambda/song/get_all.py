import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]
table = dynamodb.Table(table_name)

def get_all(event, context):
    response = table.scan()
    items = response.get("Items", [])

    res = [{"id": item["id"],
            "title": item["title"],
            "genres": item["genres"],
            "imageUrl": item["s3ImageUrl"],
            "songUrl": item["s3SongUrl"]
            } for item in items]

    return {'statusCode': 200, 'body': json.dumps(res)}