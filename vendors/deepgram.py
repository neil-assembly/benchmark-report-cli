import time
import requests
import json as jsonlib
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.environ.get('DEEPGRAM')

def get_mimetype(path):
   if '.wav' in path: return 'audio/x-wav'
   if '.mp4' in path or 'm4a' in path: return 'video/mp4'
   if ".mp3" in path: return 'audio/mpeg'
   if ".flac" in path: return 'audio/x-flac'
   if ".aac" in path: return 'audio/aac'
   if ".flv" in path: return 'video/x-flv'
   if ".m4v" in path: return 'video/x-m4v'
   return 'audio/mpeg'

def read_file(fname, chunk_size=5242880, sleep=0):
  with open(fname, 'rb') as _file:
    while True:
      time.sleep(sleep)
      data = _file.read(chunk_size)
      if not data:
          break
      yield data

def transcribe(path):
  data = read_file(path)

  DEEPGRAM_API = api_token
  DEEPGRAM_ENDPOINT = 'https://api.deepgram.com'

  # payload = {
  #   "url": url
  # }

  headers = {
    'content-type': get_mimetype(path),
    'Authorization': "Token " + DEEPGRAM_API
  }

  response = requests.post(DEEPGRAM_ENDPOINT +
                           "/v1/listen?punctuate=true",
                           data=data, #jsonlib.dumps(payload),
                           headers=headers)
                          
  return (
    response.json()['results']['channels'][0]['alternatives'][0]['transcript'])