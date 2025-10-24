import os
import json
import boto3
import io
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import io, json
from vosk import Model, KaldiRecognizer

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
song_table = dynamodb.Table(os.environ["SONG_TABLE"])
bucket_name = os.environ["OUTPUT_BUCKET"]

model = Model("/opt/python/vosk-model-small-en-us-0.15")

def handle(event, context):
    for record in event['Records']:
        if 'body' not in record:
            continue
        body = json.loads(record['body'])
        print(f"BODY: {body}")
        if 'wavKey' not in body:
             continue
        song_id = body['id']
        wav_key = body['wavKey']

        wav_obj = s3.get_object(Bucket=bucket_name, Key=wav_key)
        wav_bytes = wav_obj['Body'].read()

        audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
        audio = audio.set_channels(1).set_frame_rate(16000)

        recognizer = KaldiRecognizer(model, 16000)
        recognizer.SetWords(True)

        pcm_io = io.BytesIO()
        audio.export(pcm_io, format="wav")
        pcm_io.seek(0)
        pcm_io.read(44)
        while True:
            data = pcm_io.read(4000)
            if not data:
                break
            recognizer.AcceptWaveform(data)

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
        "body": json.dumps({"message": "Transcription completed"})
    }
