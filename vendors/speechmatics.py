import requests
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('SPEECHMATICS')

headers = {'Authorization': 'Bearer ' + API_KEY}

def transcribe(path):
    url = "https://asr.api.speechmatics.com/v2/jobs"
    payload = {
        'config': '{"type": "transcription", "transcription_config": {"language": "en"}}'
    }
    files = [('data_file', ('file', open(path, 'rb'), 'application/octet-stream'))]

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    id = response.json().get('id')

    if id is None:
        print(response.json())
        return

    while True:
        status_json = check_status(id)
        err = status_json.get('error')
        if not err or err != 'Transcription not ready':
            break
        time.sleep(3)

    if err:
        print(err)
        return
    return get_transcript_text(id)

def check_status(id):
    url = 'https://asr.api.speechmatics.com/v2/jobs/' + id + '/transcript'
    response = requests.request("GET", url, headers=headers)
    return(response.json())

def get_transcript_text(id):
    url = 'https://asr.api.speechmatics.com/v2/jobs/' + id + '/transcript?format=txt'
    response = requests.request("GET", url, headers=headers)
    return(response.text)