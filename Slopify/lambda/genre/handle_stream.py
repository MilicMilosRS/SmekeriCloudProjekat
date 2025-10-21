import boto3
import os

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def handle(event, context):
    for record in event["Records"]:
        # We're only interested in new inserts
        if record["eventName"] != "INSERT":
            continue

        new_image = record["dynamodb"]["NewImage"]
        genre_name = new_image["genreName"]["S"]

        # Check if genre exists already
        existing = genres_table.get_item(Key={"genreName": genre_name})
        if "Item" not in existing:
            print(f"Adding new genre: {genre_name}")
            genres_table.put_item(Item={"genreName": genre_name})
        else:
            print(f"Genre already exists: {genre_name}")

    return {"statusCode": 200}