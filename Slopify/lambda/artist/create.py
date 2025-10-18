import json
import io
import boto3
import uuid
import base64
import datetime
import os
from mutagen.mp3 import MP3

dynamodb = boto3.resource("dynamodb")
artist_table = dynamodb.Table(os.environ["ARTIST_TABLE"])
genre_content_table = dynamodb.Table(os.environ["GENRE_TABLE"])

"""Request body should be like
{
name,
bio,
genres: [name1, name2...],
}
"""
def handle(event, context):
    try:
        print("event loaded")
        body_raw = event.get("body", "{}")
        if isinstance(body_raw, dict):
            body = body_raw
        else:
            body = json.loads(body_raw)
        print("body loaded")

        name = body.get("name")
        bio = body.get("bio")
        genres = [g.strip().upper() for g in body.get("genres", [])]
        
        if not(name and bio and genres):
            return {'statusCode': 400, 'body':json.dumps({'error': 'Missing name bio or genres'})}

        print(body)
        print(genres)
        
        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "bio": bio,
            "genres": genres
        }
        artist_table.put_item(Item=item)

        for genre in genres:
            genre_content_table.put_item(Item={
                'genreName': genre,
                'contentId': f"ARTIST#{item['id']}",
                "contentName": name
            })


        return {'statusCode': 200 }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
