import json
import string
import time
import threading
import wave
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

api_token = os.environ.get('AZURE')

def transcribe(speech_file):
    
    # Set up the subscription info for the Speech Service:
    # Replace with your own subscription key and service region (e.g., "westus").
    speech_key, service_region = api_token, "westus"

    # Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16
    # kHz).

    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=speech_file)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language="en-US", audio_config=audio_config)

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    done = False
    transcript = []

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer
    # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    # speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt.result.text)))
    speech_recognizer.recognized.connect(lambda evt: transcript.append(evt.result.text))
    # speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    # speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()
    return ' '.join(transcript)

    # # Check the result
    # if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    #     print("Recognized: {}".format(result.text))
    #     return result.text
    # elif result.reason == speechsdk.ResultReason.NoMatch:
    #     print("No speech could be recognized: {}".format(result.no_match_details))
    #     return
    # elif result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = result.cancellation_details
    #     print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         print("Error details: {}".format(cancellation_details.error_details))
    #     return
    # </SpeechRecognitionWithFile>

# if __name__ == "__main__":
#     dir_name = '../2022-benchmark'
#     for fname in os.listdir(dir_name):
#         # if fname == 'Retool_4_minute_demo.mp3':
#         print(transcribe(os.path.join(dir_name, fname)))
#         break