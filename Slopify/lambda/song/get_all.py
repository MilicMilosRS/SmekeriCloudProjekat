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
            "imageUrl": item["s3ImageUrl"],
            "songUrl": item["s3SongUrl"]
            } for item in items]

    return {'statusCode': 200,
            "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
            'body': json.dumps(res)}