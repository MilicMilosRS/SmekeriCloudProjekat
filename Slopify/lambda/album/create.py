import json
import io
import boto3
import uuid
import base64
import datetime
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
client = boto3.client('dynamodb')
song_table = dynamodb.Table(os.environ["SONG_TABLE"])
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
album_songs_table = dynamodb.Table(os.environ["ALBUM_SONGS_TABLE"])
genre_content_table = dynamodb.Table(os.environ["GENRE_CONTENT_TABLE"])

"""Request body should be like
{
name,
songIds: [id1, id2...],
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

        albumId = str(uuid.uuid4())
        name = body.get("name")
        song_ids = body.get("songIds")
        songs = []

        #Check that all songs exist
        response = client.batch_get_item(
        RequestItems={
                os.environ['SONG_TABLE']: {
                    'Keys': [{'id': {'S': song_id}} for song_id in song_ids]
                }
            }
        )

        found_songs = response['Responses'].get(os.environ['SONG_TABLE'], [])
        found_ids = {item['id']['S'] for item in found_songs}
        missing_ids = [sid for sid in song_ids if sid not in found_ids]
        if missing_ids != []:
            return {'statusCode': 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
                "body": json.dumps({
                    "message": "Some songs not found",
                    "missingIds": missing_ids
                })
                }

        #Fill the AlbumSongs table
        for item in found_songs:
            album_songs_table.put_item(Item={
                'albumId': albumId,
                'albumName': name,
                'songId': item['id']['S'],
                'songName': item['title']['S']
            })

        #Fill the GenreContent table
        genres = set()

        for sid in set(song_ids):
            content_id = f"SONG#{sid}"
            resp = genre_content_table.query(
                IndexName="ContentTypeIndex",
                KeyConditionExpression=Key('contentId').eq(content_id),
                ProjectionExpression='genreName'
            )
            for item in resp.get('Items', []):
                genres.add(item['genreName'])

        for genre in genres:
            try:
                genre_content_table.put_item(Item={
                    'contentId': 'ALBUM#{albumId}',
                    'contentName': name,
                    'genreName': genre
                })
            except Exception as e:
                import traceback
                print("ERROR:", e)
                traceback.print_exc()
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': str(e)})
                }
            

        #Insert into albums table
        albums_table.put_item(Item={
            'id': albumId,
            'title': name
        })

        return {'statusCode': 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
                'body': json.dumps({'id': albumId}) 
                }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
