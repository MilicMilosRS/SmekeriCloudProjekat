import json
import os
import boto3
from boto3.dynamodb.conditions import Key
import datetime

dynamodb = boto3.resource("dynamodb")
song_table = dynamodb.Table(os.environ["SONG_TABLE"])
user_history_table = dynamodb.Table(os.environ["HISTORY_TABLE"])

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

        response = song_table.get_item(Key={'id': contentId})
        item = response.get("Item", None)
        if not item:
            return {"statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                }
            }

        ret = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'transcript': item.get('transcript', ''),
            's3SongUrl': "https://" + item.get('s3SongUrl', ''),
            's3ImageUrl': "https://" + item.get('s3ImageUrl', ''),
            'createdAt': item.get('createdAt', ''),
        }

        user_history_table.put_item(Item={
            'userEmail': event['requestContext']['authorizer']['claims']['email'],
            'songId': ret['id'],
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

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
