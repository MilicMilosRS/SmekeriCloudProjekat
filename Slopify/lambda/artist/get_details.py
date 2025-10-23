import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
artist_table = dynamodb.Table(os.environ["ARTIST_TABLE"])
genre_table = dynamodb.Table(os.environ["GENRE_TABLE"])
artist_songs_table = dynamodb.Table(os.environ["ARTIST_SONGS_TABLE"])
GSI_NAME = 'ContentTypeIndex'

#Body contains {contentId, contentType}
#contentType = genre or song or artist
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

        response = artist_table.get_item(Key={'id': contentId})
        item = response.get("Item", None)
        if not item:
            return {"statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                }
            }

        genre_res = genre_table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('contentId').eq("ARTIST#" + contentId),
            ProjectionExpression="genreName"
        )

        items = genre_res.get('Items', [])
        genres = list({item['genreName'] for item in items})

        songs_res = artist_songs_table.query(
            KeyConditionExpression=Key('artistId').eq(contentId)
        )

        songs = [
            {
                "songId": s["songId"],
                "songName": s.get("songName",""),
                "s3ImageUrl": s.get("s3ImageUrl","")
            }
            for s in songs_res.get("Items",[])
        ]
        ret = {
            'id': item.get('id', ''),
            'name': item.get('name', ''),
            'bio': item.get('bio', ''),
            'genres': genres,
            'songs':songs
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
