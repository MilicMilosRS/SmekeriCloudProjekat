import os
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name='eu-central-1')

SUBS_TABLE = os.environ['SUBSCRIPTIONS_TABLE']
subscriptions_table = dynamodb.Table(SUBS_TABLE)
FROM_EMAIL = "mirkodjukic23@gmail.com"

#record body has {content_id, content_name, song_id, song_name}
#content_id - id of artist/genre that the song belongs to
#content_name - name of artist/genre
def handle(event, context):
    try:
        for record in event['Records']:
            recordBody = json.loads(record['body'])
            body = json.loads(recordBody['Message'])
            content_id = body['content_id']
            content_name = body.get('content_name', 'New content')
            song_id = body.get('song_id', '')
            song_name = body.get('song_name', '')

            content_type = ""
            if content_id.startswith("SONG#"):
                content_type = "song"
            elif content_id.startswith("ARTIST#"):
                content_type = "artist"
            elif content_id.startswith("GENRE#"):
                content_type = "genre"
            else:
                print(f"Unknown content type for content: {content_id}")
                # continue

            response = subscriptions_table.query(
                IndexName="ContentIdIndex",
                KeyConditionExpression=Key('contentId').eq(content_id)
            )

            subscribers = response.get('Items', [])
            # if subscribers == []:
            #     continue

            for user in subscribers:
                email = user.get('userId')
                if email:
                    try:
                        ses.send_email(
                            Source=FROM_EMAIL,
                            Destination={"ToAddresses": [email]},
                            Message={
                                "Subject": {
                                    "Data": f"New slop-drop: {content_type.title()}"
                                },
                                "Body": {
                                    "Text": {
                                        "Data": f"New content drop for You!\n\nNew {content_type} content published: {content_name}!"
                                    }
                                }
                            }
                        )
                    except:
                        pass

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "Content-Type,Authorization"
            },
            "body": json.dumps({"message": "Notification sent"})
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
