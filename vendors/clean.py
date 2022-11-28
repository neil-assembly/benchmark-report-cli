import re
import string
import num2words

from unidecode import unidecode


def remove_extra_spaces(text):
    text = re.sub(' +', ' ', text)
    return text


def clean_markers(text):
    """clean markers in the text like [foo]"""
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = remove_extra_spaces(text)
    return text


def clean_speaker_labels(text):
    """cleans speaker label from start of line, so assumes
    the transcript has a new-line whenever the speaker changes"""
    text = re.sub(r'^.+:\s', '', text)
    text = remove_extra_spaces(text)
    return text


def expand_int_regex(match):
    token = match.group()
    return expand_int(token)


def expand_phone_number_regex(phone_number):
    try:
        expanded = []
        for c in phone_number.group():
            if c == "-":
                continue
            text = expand_int(c)
            expanded.append(text)
        return ' '.join(expanded)
    except ValueError:
        return phone_number.group()


def expand_int(token):
    """Expand int into a word."""
    _token = token.replace(',', '')
    int_token = int(_token)
    expanded_token = num2words.num2words(int_token).replace('-', ' ')
    return expanded_token + " "


def clean_numbers(text):
    # replace t1 -> t one
    text = re.sub(r'([a-zA-Z]+)(\d)', r'\g<1> \g<2>', text)

    # replace 1t -> 1 t
    text = re.sub(r'(\d)([a-zA-Z]+)', r'\g<1> \g<2>', text)

    # replace $d -> d dollar
    text = re.sub(r'(\$)(\d*[,.]?\d+)', r'\g<2> dollars', text)

    # 3.3 -> 3 point 3
    text = re.sub(r'([^$\d+]\d+)\.(\d+)', r'\g<1> point \g<2>', text)

    return text


def convert_nums_to_spoken(text):
    # convert numbers to written format
    text = re.sub(r'\d+( |$)', expand_int_regex, text)
    return text


def expand_phone_numers(text):
    # expand phone numbers
    text = text.replace(" - ", "-")
    text = re.sub(r'(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})',
                  expand_phone_number_regex, text)
    return text


def remove_disfluencies(text):
    """replace disfluencies like mm and oh"""
    noises = [
        (" mm hmm ", " "),
        (" uh huh ", " "),
        (" mm ", " "),
        (" oh ", " "),
        (" mhm ", " "),
        (" uh ", " "),
        (" hum ", " "),
        (" um ", " ")
    ]

    for noise in noises:
        text = text.replace(noise[0], noise[1])

    return text


def remove_special_cases(text):
    # special replaces
    special = [
        # short-notes
        ('&', ' and '),
        ('%', ' percent '),
        (' cm ', ' centimer '),
        ('y/o', ' year old '),
        ('dr.', 'doctor'),
        ('Dr.', 'doctor'),
        ('+', ' plus '),
        ('<', ' less than '),
        ('>', ' greater than '),
        ('gonna', 'going to'),
        ('kinda', 'kind of'),
        ('wanna', 'want to'),

        # domains and web urls
        (' www.', ' www dot '),
        ('@', ' at '),
        ('.net ', ' dot net '),
        ('.com ', ' dot com '),
        ('.gov ', ' dot gov '),
        ('.edu ', ' dot edu '),
        ('.com.au ', ' dot com dot au '),

        # punctuation
        ('-', ' '),
    ]

    for spec in special:
        text = text.replace(spec[0], spec[1])
    return text


def remove_punctuation(text):
    # python2
    try:
        return str(text).translate(None, string.punctuation.replace("'", ""))
    # python3
    except TypeError:
        return text.translate(str.maketrans('', '', string.punctuation.replace("'", "")))


def clean_transcript(input_text):
    # python2
    try:
        input_text = input_text.decode("utf-8", "ignore")
    # python3
    except AttributeError:
        input_text = input_text

    new_text = []
    for line in input_text.split('\n'):
        line = line.replace('\t', ' ').strip()

        if not line:
            continue

        line = unidecode(line)
        line = line.lower()
        line = expand_phone_numers(line)
        line = clean_markers(line)
        # line = clean_speaker_labels(line)
        line = remove_special_cases(line)
        line = clean_numbers(line)
        line = remove_punctuation(line)
        line = convert_nums_to_spoken(line)
        line = remove_disfluencies(line)
        line = line.replace("\n", " ").replace("\r", "")
        line = remove_extra_spaces(line)
        line = line.replace('\t', ' ')
        line = line.strip()
        line = remove_extra_spaces(line)
        new_text.append(line)

    return " ".join(new_text)


def truth_diffclean_transcript(input_text):
    # python2
    try:
        input_text = input_text.decode("utf-8", "ignore")
    # python3
    except AttributeError:
        input_text = input_text

    new_text = []
    for line in input_text.split('\n'):
        line = line.replace('\t', ' ').strip()

        if not line:
            continue

        # line = unidecode(line)
        # line = line.lower()
        line = clean_markers(line)
        # line = clean_speaker_labels(line)
        # line = remove_special_cases(line)
        # line = clean_numbers(line)
        # line = remove_punctuation(line)
        # line = convert_nums_to_spoken(line)
        # line = remove_disfluencies(line)
        # line = line.replace("\n", " ").replace("\r", "")
        line = remove_extra_spaces(line)
        line = line.replace('\t', ' ')
        line = line.strip()
        line = remove_extra_spaces(line)
        line = line.replace("\\'", "'")
        new_text.append(line)

    return " ".join(new_text)
