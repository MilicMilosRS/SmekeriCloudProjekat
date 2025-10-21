import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
genre_table = dynamodb.Table(os.environ["GENRE_TABLE"])

def handler(event, context):
    try:
        genres = [g['genreName'] for g in genre_table.scan()['Items']]

        return {
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
                },
            'statusCode': 200,
            'body': json.dumps(genres)
            }
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return {
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }