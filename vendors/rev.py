import time
import re
import os
import json
from rev_ai import apiclient
from dotenv import load_dotenv

load_dotenv()

api_token = os.environ.get('REV')

# revai_client = apiclient.RevAiAPIClient("02EsqhBArMHf8dfxrxrQdq2KPwD4Fo-9xrO1EAUI-5J9aW-vS5acZ6pc077mUTOQmmjHXduky7Zms2iI4GpeCoQJJALtM")
revai_client = apiclient.RevAiAPIClient(api_token)
# revai_client = apiclient.RevAiAPIClient('02rhV4fsAo4wlt0V4PPfBy_tTYjfSCgsPM0tDcnkUqfhDspw9mI7erfRnGHF0UoRS25Z38_mp2qnQ2IeWr3p_evHx9rhw')


def transcribe(speech_file):
    job = revai_client.submit_job_local_file(speech_file, skip_diarization=True, language='en')
    job_details = revai_client.get_job_details(job.id)

    while str(job_details.status) not in ['JobStatus.TRANSCRIBED', 'JobStatus.FAILED']:
        job_details = revai_client.get_job_details(job.id)
        time.sleep(5)

    if str(job_details.status) == 'JobStatus.FAILED':
        print(job_details)
        return ''

    transcript_text = revai_client.get_transcript_text(job.id)
    transcript_text = re.sub(r'^Speaker\s[0-9]\s*[0-9]*:[0-9]*:[0-9]*\s*', '', transcript_text)
    revai_client.delete_job(job.id)
    return transcript_text