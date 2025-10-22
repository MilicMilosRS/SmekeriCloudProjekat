import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
GSI_NAME = 'ContentTypeIndex'
albums_table = dynamodb.Table(os.environ["ALBUMS_TABLE"])
album_songs_table = dynamodb.Table(os.environ["ALBUM_SONGS_TABLE"])
genre_content_table = dynamodb.Table(os.environ["GENRE_CONTENT_TABLE"])

def handle(event, context):
    try:
        contentId = event['pathParameters']['id']  # gets {id} from URL

        if not contentId:
            return {"statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                    }
                }

        response = albums_table.get_item(Key={'id': contentId})
        item = response.get("Item", None)
        if not item:
            return {"statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                }
            }

        genre_res = genre_content_table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('contentId').eq("ALBUM#" + contentId),
            ProjectionExpression="genreName"
        )

        items = genre_res.get('Items', [])
        genres = list({item['genreName'] for item in items})

        songs_res = album_songs_table.query(
            KeyConditionExpression=Key('albumId').eq(contentId),
        )
        print(songs_res.get('Items'))
        songs = [{'name': s.get('songName'), 'contentId': s.get('songId')} for s in songs_res.get('Items',[])]

        ret = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'genres': genres,
            'songs': songs
        }

        return {"statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            "body": json.dumps(ret)
        }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
