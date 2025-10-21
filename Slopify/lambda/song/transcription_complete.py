import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
song_table = dynamodb.Table(os.environ["SONG_TABLE"])

def handle(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if not key.startswith("transcriptions/"):
            continue

        song_id = key.split("/")[-1].replace(".json", "")

        response = s3.get_object(Bucket=bucket, Key=key)
        result = json.loads(response['Body'].read())

        transcript_text = result['results']['transcripts'][0]['transcript']

        song_table.update_item(
            Key={'id': song_id},
            UpdateExpression="set transcript = :t, transcription_status = :s",
            ExpressionAttributeValues={
                ':t': transcript_text,
                ':s': 'COMPLETED'
            }
        )
