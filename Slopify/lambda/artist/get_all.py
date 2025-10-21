import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
artist_table = dynamodb.Table(os.environ["ARTIST_TABLE"])

def handle(event, context):
    response = artist_table.scan()
    items = response.get("Items", [])

    res = [{"id": item["id"],
            "name": item["name"]
            } for item in items]

    return {
        "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
        'statusCode': 200,
        'body': json.dumps(res)
        }