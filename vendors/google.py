"""
Google Cloud Speech API sample application using the REST API for async
batch processing.


Example usage:
    python transcribe_async.py --path resources/audio.raw
"""

import uuid
import argparse

from google.cloud import storage
storage_client = storage.Client()
GCP_BUCKET_NAME = 'aai-customer-evals'


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name, chunk_size=262144)

    blob.upload_from_filename(source_file_name)


def upload_to_gcs(fname):
    gcp_object_name = uuid.uuid4().hex.upper()[0:6]
    upload_blob(bucket_name=GCP_BUCKET_NAME,
                source_file_name=fname,
                destination_blob_name=gcp_object_name)
    gcs_uri = "gs://%s/%s" % (GCP_BUCKET_NAME, gcp_object_name)
    return gcs_uri


def transcribe(speech_file, use_enhanced=False, model="video", sample_rate=8000,
               language_code="en-US"):
    """Transcribe the given audio file asynchronously."""
    from google.cloud import speech

    client = speech.SpeechClient()

    gcs_uri = upload_to_gcs(speech_file)

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        language_code=language_code,
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        enable_automatic_punctuation=True)

    if use_enhanced is True:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            use_enhanced=True,
            model=model,  # video | phone_call
            language_code='en-US',
            enable_automatic_punctuation=True)
    

    operation = client.long_running_recognize({"config":config, "audio":audio})
    response = operation.result(timeout=60*500)

    all_transcript_text = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        if not result.alternatives[0].transcript:
            continue

        all_transcript_text.append(result.alternatives[0].transcript)

    final_transcript = (" ".join(all_transcript_text))
    return final_transcript