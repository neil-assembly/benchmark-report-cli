import os
import traceback
import argparse

from termcolor import colored
from multiprocessing.pool import ThreadPool
from vendors.transcode import transcode_to_wavs, get_sample_rate
from vendors import google
from vendors import aws
from vendors import assembly
from vendors import rev
from vendors import microsoftazure
from vendors import speechmatics
from vendors import deepgram
from vendors.clean import clean_transcript, truth_diffclean_transcript
from jiwer import wer

def get_files_to_transcribe(dir):
    supported_extensions = [".wav", ".mp4", ".mp3", ".m4a", ".flac", ".aac", ".flv", ".m4v"]
    files = []
    if dir:
        for fname in os.listdir(dir):
            if any([fname.endswith(ext) for ext in supported_extensions]) and "transcode" not in fname:
                files.append(os.path.join(dir, fname))
    return files

def get_truth_text(audio_file):
    try:
        truth_txt_fname = audio_file + "-truth.txt"
        with open(truth_txt_fname, 'r') as _in:
            truth_text = _in.read()

        truth_text_clean = clean_transcript(truth_text)

        with open(audio_file + ".clean.txt", "w") as _out:
            _out.write(truth_text_clean)

        with open(audio_file + ".diffclean.txt", "w") as _out:
            _out.write(truth_diffclean_transcript(truth_text))

        return truth_text_clean
    except Exception as Exc:
        print(colored("no truth text found for %s" % audio_file, "red"))
        return "no truth text found"


def run_comparison(audio_file, args):
    print(colored('running on %s' % audio_file, 'green'))
    results = {}
    wers = {'file': audio_file.split('/')[-1]}

    try:
        audio_versions = transcode_to_wavs(audio_file)

        if args.with_google is True:
            transcript = google.transcribe(
                audio_versions['wav_mono'], use_enhanced=args.google_enhanced, model=args.google_model,
                sample_rate=get_sample_rate(audio_versions['wav_mono']))
            results["google_%s" % ("video" if args.google_enhanced else "default")] = transcript

        if args.with_aws is True:
            transcript = aws.transcribe(audio_versions['wav_mono'])
            results["aws"] = transcript

        if args.with_azure is True:
            transcript = microsoftazure.transcribe(audio_versions['wav_mono'])
            results["azure"] = transcript

        if args.with_assembly is True:
            transcript = assembly.transcribe(
                audio_versions['original'], word_boost=args.assembly_word_boosts)
            results["assembly"] = transcript

        if args.with_rev is True:
            transcript = rev.transcribe(audio_versions['original'])
            results['revai'] = transcript
       
        if args.with_deepgram is True:
            transcript = deepgram.transcribe(audio_versions['original'])
            results['deepgram'] = transcript
        
        if args.with_speechmatics is True:
            transcript = speechmatics.transcribe(audio_versions['original'])
            results['speechmatics'] = transcript

        truth_text = get_truth_text(audio_file)
        for provider in results:
            hypothesis = results[provider]
            clean_hypothesis = clean_transcript(hypothesis)
            error_rate = wer(truth_text, clean_hypothesis)
            wers[provider] = error_rate

            output_fname = "%s.%s.txt" % (audio_file, provider)
            with open(output_fname, 'w') as _out:
                _out.write(hypothesis)
            with open(f'{audio_file}.{provider}.clean.txt', 'w') as _out:
                _out.write(clean_hypothesis)

        print(colored("%s complete" % audio_file, 'yellow'))
    except Exception as Exc:
        tb = traceback.format_exc()
        print(colored("Error on file: %s (%s)" % (audio_file, Exc), 'red'))
        print(colored(tb, 'red'))
    finally:
        try:
            os.remove(audio_versions['wav_mono'])
            os.remove(audio_versions['wav_mono_8khz'])
        except:
            pass

    return wers


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', help="Dir containing files to transcribe")
    parser.add_argument('--with_google', default=False, type=bool)
    parser.add_argument('--with_aws', default=False, type=bool)

    parser.add_argument('--with_assembly', default=False, type=bool)
    parser.add_argument('--with_rev', default=False, type=bool)
    parser.add_argument('--with_deepgram', default=False, type=bool)
    parser.add_argument('--with_speechmatics', default=False, type=bool)

    parser.add_argument('--with_watson', default=False, type=bool)
    parser.add_argument('--with_azure', default=False, type=bool)

    # provider specific settings
    parser.add_argument('--google_enhanced', default=False, type=bool)
    parser.add_argument('--google_model', default="general", type=str, help="video | general | phone_call")
    parser.add_argument('--assembly_word_boosts', type=str)
    parser.add_argument('--assembly_model', default="assemblyai_default", type=str)

    # optional
    parser.add_argument('--n', default=8, type=int)

    # get args out
    args = parser.parse_args()

    # run
    files = get_files_to_transcribe(args.directory)

    # transcode each file
    results = []
    pool = ThreadPool(processes=args.n)
    for file in files:
        if 'Retool' in file:
            result = pool.apply_async(run_comparison, (file, args))
            results.append(result)

    all_wers = []
    for result in results:
        wers = result.get()
        all_wers.append(wers)

    for scores in all_wers:
        print(scores)
