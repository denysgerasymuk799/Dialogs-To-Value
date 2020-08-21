import argparse
import datetime
import logging
import os
import re

import numpy as np
import pandas as pd
import pymorphy2
import tokenize_uk
from cube.api import Cube
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from num2words import num2words
from stop_words import get_stop_words
from uk_stemmer import UkStemmer
from word2number import w2n


def init_tool_config_arg():
    parser = argparse.ArgumentParser(description="Step #3.Prepare dialogs data.")
    parser.add_argument(
        "--dialogs_ids",
        nargs="+",
        type=int,
        help="id(s) of dialog(s) to download, -1 for all",
        required=True,
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default="config/config.json",
    )
    parser.add_argument("--debug_mode", type=int, help="Debug mode", default=0)
    return parser.parse_args()


def if_in_date_range(date_time, date_before, date_after):
    """

    :param date_time: msg datetime type
    :return: if msg in range (date_before, date_after)
    """
    dialog_datetime = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    if date_before < dialog_datetime < date_after:
        return True

    if dialog_datetime >= date_after:
        return 'Dialog after date_after'

    return False


def convert_lower_case(data):
    new_data = ""
    for word in data.split():
        word = word.lower()
        new_data += word + " "
    return new_data


def convert_numbers(data, function_type):
    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        if function_type == "words_frequency":
            if not w.isdigit():
                new_text = new_text + " " + w
        else:
            try:
                w = num2words(int(w))
            except:
                pass
            new_text = new_text + " " + w
    new_text = np.char.replace(new_text, "-", " ")
    return new_text


def remove_stop_words(data, lang, function=""):
    """

    :param lang: "ru", "ua" or "en"
    :return: cleaned text from stop_words
    """
    stop_words = []
    if lang in ("ru", "ua"):
        stop_words_ru = get_stop_words('russian')
        stop_words_en = get_stop_words('en')
        stop_words_ua = []

        try:
            with open(os.path.join(os.getcwd(), "..", "dicts", "ukrainian_stopwords.txt"), "r", encoding="utf-8") as file:
                for word in file:
                    stop_words_ua.append(word.strip())

        except FileNotFoundError:
            with open(os.path.join(os.getcwd(), "dicts", "ukrainian_stopwords.txt"), "r",
                      encoding="utf-8") as file:
                for word in file:
                    stop_words_ua.append(word.strip())

        stop_words = stop_words_ru + stop_words_ua + stop_words_en

    elif lang == "en":
        stop_words = get_stop_words('en')

    if function == "get_stop_words":
        return stop_words

    words = word_tokenize(str(data))

    new_text = ""
    for w in words:
        w = w.strip()
        # do not delete it, because it is useful for
        # CountVectorizer ngram_range=(2, 2) or more
        # if w == "не":
        #     new_text = new_text + " " + w
        #     continue

        if w not in stop_words and len(w) > 2:
            new_text = new_text + " " + w

    return new_text


def stemming(data, lang):
    tokens = tokenize_uk.tokenize_uk.tokenize_text(data)
    stemmer = ""
    if lang == "ua":
        stemmer = UkStemmer()
    elif lang == "ru":
        stemmer = SnowballStemmer("russian", ignore_stopwords=True)

    new_text = ""
    for text in tokens:
        for sentence in text:
            for word in sentence:
                if lang == "ua":
                    new_text = new_text + " " + stemmer.stem_word(word)
                elif lang == "ru":
                    new_text = new_text + " " + stemmer.stem(word)

    return new_text


def url_to_domain(word: str, check=False):
    """
    Extracts domain from url.
    :param word: str
    :param check: bool - used to check if given
    string contains url.
    :return: str
    """
    url_extract = re.compile(r'(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)?(?:https?:\/\/)'
                             r'(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)(?:[-a-zA-Z0'
                             r'-9@:%_\+.~#?&//=]*)?')
    if check:
        return url_extract.match(word)
    return url_extract.findall(word)[0]


def word_to_num(word: str) -> str:
    """
    Tries to convert word to number
    works only with English words
    :param word: str
    :return: str
    """
    try:
        num = str(w2n.word_to_num(word))
    except ValueError:
        logging.warning('Cannot convert word to number.')
        return word
    return num


def delete_symbols(msg: str) -> str:
    """
    Substitutes symbols with spaces.
    :param msg: str
    :return: str
    """
    symbols = re.compile(r"[-!$%^&*()_+©|~#=.`{}\[\]:'\";<>?,ʼ/]|[^\w]")

    return re.sub(symbols, ' ', msg)


def lemmatization(msg, lang, cube):
    """

    :param lang: "ru", "ua" or "en"
    :param cube: only for "ua"an object after these commands cube = Cube(verbose=True); cube.load("uk")
    :return: cleaned text from synonyms
    """
    lemmas = ""
    if lang == "ru":
        lemmas = " ".join(pymorphy2.MorphAnalyzer().parse(np.unicode(word))[0].normal_form for word in msg.split())

    elif lang in ("ua", "en"):
        sentences = cube(msg)

        for sentence in sentences:  # note we selected the first sentence (sentence[0])
            for entry in sentence:
                lemmas += entry.lemma
                # now, we look for a space after the lemma to add it as well
                if not "SpaceAfter=No" in entry.space_after:
                    lemmas += " "

    return lemmas


def clean_message(msg: str) -> str:
    """
    Makes preparation for the given message.
    :param msg: str
    :return: str
    """
    out_msg = []
    for word in str(msg).split():
        if url_to_domain(word, check=True):
            out_msg.append(url_to_domain(word))
        else:
            # word = word_to_num(word)
            out_msg.append(delete_symbols(word))
    return re.sub(r'\s\s+', ' ', ' '.join(out_msg))


def transform_raw_data(msg, lang, function_type, cube):
    msg = convert_lower_case(msg)
    msg = clean_message(msg)
    msg = re.sub('\-\s\r\n\s{1,}|\-\s\r\n|\r\n', '', msg)  # deleting newlines and line-breaks
    msg = convert_numbers(msg, function_type)
    msg = remove_stop_words(msg, lang)

    # msg = stemming(msg, lang)
    msg = lemmatization(msg, lang, cube)
    return msg


def prepare_dialogs(dialog_id, dialog_path, prep_path, date_before, date_after, lang,
                    function_type=""):
    """
    Reads raw csv data and creates prepared copy
    at /data/prepared_dialogs/
    :return: None
    """
    
    #TODO: create a new column for preprocessed text. NEVER use the same column for raw and preprocessed data, with such approach you lose information!
    logging.debug(f'Preparing dialog #{dialog_id}.')

    data = pd.read_csv(f'{dialog_path}{dialog_id}.csv')
    cube = ""
    if lang == "ua":
        cube = Cube(verbose=True)
        cube.load("uk")

    elif lang == "en":
        cube = Cube(verbose=True)
        cube.load("en")

    for i in data.index:
        date_time = data["date"][i][:-6]
        dialog_datetime = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

        if dialog_datetime <= date_before:
            break

        elif date_before < dialog_datetime < date_after:
            msg = data.loc[i, 'message']
            if not pd.isnull(msg):
                data.loc[i, 'message'] = transform_raw_data(msg, lang, function_type, cube)
                print("INDEX", i)

    # you start but you didn't finish?
    # TODO: use imperative mood -> save dialog!
    
    logging.warning("start saving")
    print("start saving")
    data.to_csv(f'{prep_path}{dialog_id}.csv')


if __name__ == "__main__":
    args = init_tool_config_arg()

    DIALOG_ID = args.dialogs_ids
    DEBUG_MODE = args.debug_mode
    DIALOG_PATH = '../data/dialogs/'
    PREPARED_PATH = '../data/prepared_dialogs/'

    if DEBUG_MODE:
        logging.basicConfig(filename='../logs/project_logs.log', level=logging.DEBUG)
        # logging.basicConfig(filename='../logs/project_logs.log', level=1)

    if os.path.isdir(DIALOG_PATH):
        if not os.path.isdir(PREPARED_PATH):
            os.mkdir(PREPARED_PATH)

        # change to date range in what you want to analyse messages of user_id_get_msg - from date_before to date_after;
        # format "%Y-%m-%d %H:%M:%S"
        # date_before = datetime.datetime(2020, 5, 9, 0, 0, 0)
        # date_after = datetime.datetime(2020, 8, 10, 0, 0, 0)
        for dialog in DIALOG_ID:
            prepare_dialogs(dialog, DIALOG_PATH, PREPARED_PATH, date_before,
                            date_after, "ua", "words_frequency")
    else:
        logging.error('Dialogs dir does not exist !')
