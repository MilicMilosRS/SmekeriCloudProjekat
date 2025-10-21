import os
import json
import boto3
import io
import uuid
import base64
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
song_table = dynamodb.Table(os.environ["SONG_TABLE"])
bucket_name = os.environ["BUCKET_NAME"]

model_path = "/opt/vosk-model"
vosk_model = Model(model_path)

def handle(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        song_id = body['id']
        s3_key = body['s3SongUrl'].replace(f"s3://{bucket_name}/", "")

        mp3_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
        mp3_bytes = mp3_obj['Body'].read()

        audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = KaldiRecognizer(vosk_model, audio.frame_rate)
        recognizer.SetWords(True)

        data = wav_io.read()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
        else:
            result = json.loads(recognizer.FinalResult())

        transcript_text = result.get("text", "")

        song_table.update_item(
            Key={"id": song_id},
            UpdateExpression="set transcript=:t, transcription_status=:s",
            ExpressionAttributeValues={
                ":t": transcript_text,
                ":s": "COMPLETED" if transcript_text else "FAILED"
            }
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Transcription processed"})
    }
