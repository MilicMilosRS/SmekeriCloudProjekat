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
genre_content_table = dynamodb.Table(os.environ["GENRE_TABLE"])
CLOUDFRONT_URL = os.environ["CLOUDFRONT_URL"]
bucket_name = os.environ["BUCKET_NAME"]

"""Request body should be like
{
title,
genres: [name1, name2...],
artistIds: [id1, id2...],
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
        genres = [g.strip().upper() for g in body.get("genres", [])]
        print(body)
        print(genres)

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
        s3.put_object(Bucket=bucket_name, Key=song_filename, Body=song_bytes, ContentType='audio/mpeg')
        s3.put_object(Bucket=bucket_name, Key=image_filename, Body=image_bytes, ContentType='image/jpeg')
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
            "s3SongUrl": f"{CLOUDFRONT_URL}/{song_filename}",
            "s3ImageUrl": f"{CLOUDFRONT_URL}/{image_filename}",
            "fileName": song_filename.split('/')[-1],
            "fileType": "audio/mpeg",
            "fileSize": file_size,
            "createdAt": creation_time,
            "updatedAt": modification_time,
            "duration": duration,
            "transcription_status": "PENDING",
            "transcript": ""
        }
        song_table.put_item(Item=item)

        for id in body.get("artistIds", []):
            response = artist_table.get_item(Key={'id': id})
            if 'Item' not in response:
                return {'statusCode': 404 }
            artist = response['Item']
            artist_songs_table.put_item(Item={
                'artistId': id,
                'songId': item['id'],
                'songName': title,
                'artistName': artist['name']
            })

        for genre in genres:
            genre_content_table.put_item(Item={
                'genreName': genre,
                'contentId': f"SONG#{item['id']}",
                "contentName": item['title']
            })

        sqs = boto3.client('sqs')
        queue_url = os.environ['TRANSCRIPTION_QUEUE_URL']

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'id': item['id'],
                's3SongUrl': f"s3://{bucket_name}/{song_filename}"
            })
        )

        return {'statusCode': 200 }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
