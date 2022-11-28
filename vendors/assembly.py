import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_token = os.environ.get('ASSEMBLYAI')

def read_file(fname, chunk_size=5242880, sleep=0):
    with open(fname, 'rb') as _file:
        while True:
            time.sleep(sleep)
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


def upload(fname, sleep=0, chunk_size=5242880*2):
    headers = {'authorization': api_token}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             data=read_file(fname, sleep=sleep, chunk_size=chunk_size))

    return response.json()['upload_url']


def transcribe(speech_file, word_boost=None, boost_param=None,
               punctuate=True, format_text=True, dual_channel=False, redact_pii=False,
               redact_pii_policies=None, redact_pii_sub='entity_name'):

    url = "https://api.assemblyai.com/v2/transcript"
    staging = "https://api.staging.assemblyai-labs.com/v2/transcript"

    audio_url = upload(speech_file)

    payload = {
        "audio_url": audio_url,
        "language_code": "en",
        # "disfluencies": True
        # "punctuate": punctuate,
        # "format_text": format_text,
        # "dual_channel": dual_channel,
        # "redact_pii": redact_pii,
        # "redact_pii_audio": redact_pii,
        # "redact_pii_policies": None if not redact_pii_policies else redact_pii_policies.split(","),
        # "redact_pii_sub": redact_pii_sub,
    }

    if word_boost is not None:
        word_boost = word_boost.split(",")
        boost_param = boost_param
        payload['word_boost'] = word_boost

        if boost_param is not None:
            payload['boost_param'] = boost_param

    headers = {'authorization': api_token}

    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    status = response_json.get('status')
    id = response_json.get('id')

    if status is None:
        print(response.json())
        return

    while status not in ["completed", "error"]:
        response = requests.get(url + "/%s" % id, headers=headers)
        response_json = response.json()
        status = response_json.get('status')

        time.sleep(3)

    if status == "error":
        print(response_json['error'])
        return

    text = response_json.pop('text')
    return text