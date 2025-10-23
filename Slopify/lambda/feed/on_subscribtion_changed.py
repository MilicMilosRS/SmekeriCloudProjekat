import boto3
import os
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")

def handler(event, context):
    for record in event["Records"]:
        rating = record["dynamodb"].get("NewImage") or record["dynamodb"].get("OldImage")
        print(rating)
        if not rating:
            continue
        email = rating["userId"]["S"]

        print(f"New sub")

        lambda_client.invoke(
            FunctionName=os.environ["FEED_GENERATOR_LAMBDA"],
            InvocationType="Event",
            Payload=json.dumps({
                "userEmail": email,
                "triggeredBy": "newSong"
            })
        )
        print(f"Triggered feed generation for {email}")

    return {"statusCode": 200}