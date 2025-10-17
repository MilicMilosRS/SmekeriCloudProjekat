import json
import io
import boto3
import uuid
import base64
import datetime
import os
from mutagen.mp3 import MP3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
song_table = dynamodb.Table(os.environ["SONG_TABLE"])
artist_table = dynamodb.Table(os.environ["ARTIST_TABLE"])
artist_songs_table = dynamodb.Table(os.environ["ARTIST_SONGS"])

"""Request body should be like
{
title,
genres: [name1, name2...]
songMp3Data,
imageData
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
        title = body.get("title")
        genres = body.get("genres", [])

        #Fajlovi u base64
        song_data = body.get("songMp3Data")
        image_data = body.get("imageData")

        if not (title and song_data and image_data):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required fields'})}

        #Dekodiranje fajlova
        song_bytes = base64.b64decode(song_data)
        image_bytes = base64.b64decode(image_data)
        print("files decoded")
        #Kreiranje unikatanih imena fajlova
        song_filename = f"songs/{uuid.uuid4()}.mp3"
        image_filename = f"images/{uuid.uuid4()}.jpg"

        #Upload na S3
        s3.put_object(Bucket="slopify-bucket", Key=song_filename, Body=song_bytes, ContentType='audio/mpeg')
        s3.put_object(Bucket="slopify-bucket", Key=image_filename, Body=image_bytes, ContentType='image/jpeg')
        print("objects uploaded to s3")
        # MP3 metapodaci
        mp3_file = io.BytesIO(song_bytes)
        audio = MP3(mp3_file)
        duration = int(audio.info.length)  # trajanje u sekundama
        print("mp3 metadata extracted")
        # Ostali metapodaci
        file_size = len(song_bytes)
        creation_time = datetime.datetime.utcnow().isoformat()
        modification_time = creation_time
        print("other metadata extracted")
        item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "genres": genres,
            "s3SongUrl": f"https://slopify-bucket.s3.amazonaws.com/{song_filename}",
            "s3ImageUrl": f"https://slopify-bucket.s3.amazonaws.com/{image_filename}",
            "fileName": song_filename.split('/')[-1],
            "fileType": "audio/mpeg",
            "fileSize": file_size,
            "createdAt": creation_time,
            "updatedAt": modification_time,
            "duration": duration
        }

        song_table.put_item(Item=item)

        return {'statusCode': 200 }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
