import os
import json
import boto3
from urllib.parse import unquote_plus

dynamodb = boto3.resource('dynamodb')
transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')

song_table = dynamodb.Table(os.environ["SONG_TABLE"])

def handle(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        song_id = body['id']
        s3_uri = body['s3SongUrl'] 

        job_name = f"transcription_{song_id}"
        output_bucket = os.environ['BUCKET_NAME']

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri':s3_uri},
            MediaFormat='mp3',
            languageCode='en-US',
            OutputBucketName=output_bucket
        )
        song_table.update_item(
            Key={'id':song_id},
            UpdateExpression='set transcription_status=:s',
            ExpressionAttributeValues={':s':'IN_PROGRESS'}
        )

        return {"statusCode":200, "body":json.dumps("Transcription started")}
