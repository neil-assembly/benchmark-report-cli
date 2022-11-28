from __future__ import print_function

import time
import json
import boto3
import logging
import random
import requests

from botocore.exceptions import ClientError


aws_transcribe = boto3.client('transcribe', region_name='us-west-2')
bucket_name = "benchmark-report-submissions"


def upload_file(file_name, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3', region_name='us-west-2')
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return object_name


def transcribe(speech_file):

    job_name = str(random.randint(11111111111, 99999999999))
    object_name = upload_file(speech_file)
    media_format = object_name.split(".")[-1]
    job_uri = "s3://%s/%s" % (bucket_name, object_name)

    aws_transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=media_format,
        LanguageCode='en-US',
    )

    while True:
        status = aws_transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    result = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri']).text
    result = json.loads(result)
    transcript = result['results']['transcripts'][0]
    return transcript['transcript']
    
