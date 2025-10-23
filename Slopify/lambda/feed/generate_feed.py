import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import json

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(os.environ["SONG_TABLE"])
artist_songs_table = dynamodb.Table(os.environ["ARTIST_SONGS_TABLE"])
genre_content_table = dynamodb.Table(os.environ["GENRE_CONTENT_TABLE"])
subscriptions_table = dynamodb.Table(os.environ["USER_SUBSCRIPTIONS_TABLE"])
user_feed_table = dynamodb.Table(os.environ["USER_FEED_TABLE"])
grades_table = dynamodb.Table(os.environ["GRADE_TABLE"])
history_table = dynamodb.Table(os.environ["HISTORY_TABLE"])

def handler(event, context):
    email = event.get("userEmail")

    feed_songs = {}

    #Subscriptions
    subs = subscriptions_table.query(KeyConditionExpression=Key("userId").eq(email))["Items"]
    for sub in subs:
        content_id = sub["contentId"]
        if content_id.startswith("ARTIST#"):
            artist_id = content_id.split("#")[1]
            artist_songs = artist_songs_table.query(KeyConditionExpression=Key("artistId").eq(artist_id))["Items"]
            for s in artist_songs:
                feed_songs[s["songId"]] = feed_songs.get(s["songId"], 0) + 2
        elif content_id.startswith("GENRE#"):
            genre_name = sub["contentName"]
            genre_songs = genre_content_table.query(KeyConditionExpression=Key("genreName").eq(genre_name))["Items"]
            for s in genre_songs:
                if s["contentId"].startswith("SONG#"):
                    song_id = s["contentId"].split("#")[1]
                    feed_songs[song_id] = feed_songs.get(song_id, 0) + 1

    #Ratings
    grades = grades_table.query(KeyConditionExpression=Key("userId").eq(email))["Items"]
    for g in grades:
        if g["contentId"].startswith("SONG#") and int(g["grade"]) >= 4:
            song_id = g["contentId"].split("#")[1]
            feed_songs[song_id] = feed_songs.get(song_id, 0) + 3

    #ListeningHistory
    history = history_table.query(KeyConditionExpression=Key("userEmail").eq(email))["Items"]
    for h in history:
        song_id = h["songId"]
        recency_score = max(1, 5 - (days_since(h["timestamp"])))
        feed_songs[song_id] = feed_songs.get(song_id, 0) + recency_score

    #Sort and return
    sorted_songs = sorted(feed_songs.items(), key=lambda x: x[1], reverse=True)

    with user_feed_table.batch_writer() as batch:
        for song_id, score in sorted_songs[:20]:
            song = songs_table.get_item(Key={"id": song_id}).get("Item")
            if song:
                batch.put_item(
                    Item={
                        "userEmail": email,
                        "songId": song_id,
                        "songName": song["title"],
                        "score": score,
                    }
                )

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({'message':'Success'})
    }

def days_since(timestamp_str):
    try:
        date = datetime.fromisoformat(timestamp_str)
        return (datetime.utcnow() - date).days
    except Exception:
        return 5