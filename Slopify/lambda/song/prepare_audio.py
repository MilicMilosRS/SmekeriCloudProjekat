import os
import json
import boto3
import io
from pydub import AudioSegment

s3 = boto3.client("s3")
sqs = boto3.client("sqs")

BUCKET_NAME = os.environ["OUTPUT_BUCKET"]
QUEUE_URL = os.environ["TRANSCRIPTION_QUEUE_URL"]
os.environ["PATH"] += os.pathsep + "/opt/python"
AudioSegment.converter = "/opt/python/ffmpeg"
AudioSegment.ffprobe = "/opt/python/ffprobe"

def handle(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        print(f"BODY: {body}")


        song_id = body["id"]
        s3_key = body["s3SongUrl"].replace(f"s3://{BUCKET_NAME}/", "")

        mp3_obj = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        mp3_bytes = mp3_obj["Body"].read()

        audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        wav_key = f"prepared/{song_id}.wav"
        s3.put_object(Bucket=BUCKET_NAME, Key=wav_key, Body=wav_io.getvalue())
        print(wav_key)
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                "id": song_id,
                "wavKey": wav_key
            })
        )

    return {"statusCode": 200, "body": json.dumps({"message": "Audio prepared and queued"})}
