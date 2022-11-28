import os
import wave
import random
import subprocess


def transcode_to_wavs(audio_file):
    randid = str(random.randint(0000000, 9999999))
    filename, file_extension = os.path.splitext(audio_file)
    in_fname = audio_file
    tmp_out_fname = filename + "." + randid + ".transcoded.tmp.wav"
    final_out_fname = filename + "." + randid + ".transcoded.wav"
    final_out_fname_8khz = filename + "." + randid + ".transcoded.8khz.wav"

    FNULL = open(os.devnull, 'w')

    # convert to wav
    subprocess.call(["ffmpeg", "-i", in_fname, tmp_out_fname], stdout=FNULL, stderr=subprocess.STDOUT)

    # make sure its single channel
    subprocess.call(["sox", tmp_out_fname, "-c", "1", final_out_fname], stdout=FNULL, stderr=subprocess.STDOUT)
    subprocess.call(["sox", tmp_out_fname, "-c", "1", "-r", "8000", final_out_fname_8khz], stdout=FNULL, stderr=subprocess.STDOUT)

    os.remove(tmp_out_fname)

    return {
        'original': audio_file,
        'wav_mono': final_out_fname,
        'wav_mono_8khz': final_out_fname_8khz
    }


def get_sample_rate(audio_file):
    with wave.open(audio_file, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        return frame_rate
