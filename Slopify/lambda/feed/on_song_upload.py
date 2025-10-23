import boto3
import os
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")

artist_songs_table = dynamodb.Table(os.environ["ARTIST_SONGS_TABLE"])
subscriptions_table = dynamodb.Table(os.environ["USER_SUBSCRIPTIONS_TABLE"])
genre_content_table = dynamodb.Table(os.environ["GENRE_CONTENT_TABLE"])

def handler(event, context):
    all_users = set()

    for record in event["Records"]:
        if record["eventName"] != "INSERT":
            continue

        new_song = record["dynamodb"]["NewImage"]
        song_id = new_song["id"]["S"]
        song_name = new_song["title"]["S"]

        print(f"New song {song_name} ({song_id})")

        artist_result = artist_songs_table.query(
            IndexName="SongIdIndex",
            KeyConditionExpression=Key("songId").eq(song_id)
        )["Items"]

        artist_ids = [a["artistId"] for a in artist_result]

        genre_result = genre_content_table.query(
            IndexName="ContentTypeIndex",
            KeyConditionExpression=Key("contentId").eq(f"SONG#{song_id}")
        )["Items"]

        genre_names = [g["genreName"] for g in genre_result]

        print(f"Found artist(s): {artist_ids}")
        print(f"Found genre(s): {genre_names}")

        for artist_id in artist_ids:
            subs = subscriptions_table.query(
                IndexName="ContentIdIndex",
                KeyConditionExpression=Key("contentId").eq(f"ARTIST#{artist_id}")
            )["Items"]
            for sub in subs:
                all_users.add(sub["userId"])

        for genre_name in genre_names:
            subs = subscriptions_table.query(
                IndexName="ContentIdIndex",
                KeyConditionExpression=Key("contentId").eq(f"GENRE#{genre_name}")
            )["Items"]
            for sub in subs:
                all_users.add(sub["userId"])

    print(f"Found {len(all_users)} subs")

    for email in all_users:
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