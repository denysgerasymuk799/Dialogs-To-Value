import json
import re
from word2number import w2n

import logging
import os
from pprint import pprint

import numpy as np
import pandas as pd
import pymorphy2
import tokenize_uk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from num2words import num2words
from stop_words import get_stop_words
from uk_stemmer import UkStemmer


def delete_special_characters(msg: str) -> str:
    """
    Substitutes symbols with spaces.
    :param msg: str
    :return: str
    """
    symbols = re.compile(r"[-!$%^&*()_+|~=`{}\[\]:';<>?,ʼ\/]|[^\w]")
    return re.sub(symbols, " ", msg)


def delete_apostrophes(msg: str) -> str:
    """
    Deletes apostrophes, curly quotes, quotes
    :param msg: str
    :return: str
    """
    out_msg = re.sub(r"`'ʼ", "", msg)
    return re.sub(r'"', "", out_msg)


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
        stop_words_ru = get_stop_words("russian")
        stop_words_en = get_stop_words("en")
        stop_words_ua = []

        try:
            with open(
                os.path.join(os.getcwd(), "..", "dicts", "ukrainian_stopwords.txt"),
                "r",
                encoding="utf-8",
            ) as file:
                for word in file:
                    stop_words_ua.append(word.strip())

        except FileNotFoundError:
            with open(
                os.path.join(os.getcwd(), "dicts", "ukrainian_stopwords.txt"),
                "r",
                encoding="utf-8",
            ) as file:
                for word in file:
                    stop_words_ua.append(word.strip())

        stop_words = stop_words_ru + stop_words_ua + stop_words_en

    elif lang == "en":
        stop_words = get_stop_words("en")

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
    url_extract = re.compile(
        r"(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)?(?:https?:\/\/)"
        r"(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)(?:[-a-zA-Z0"
        r"-9@:%_\+.~#?&//=]*)?"
    )
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
        logging.warning("Cannot convert word to number.")
        return word
    return num


def delete_symbols(msg: str) -> str:
    """
    Substitutes symbols with spaces.
    :param msg: str
    :return: str
    """

    symbols = re.compile(r"[-!$%^&*()_+©|~#=.`{}\[\]:'\";<>?,ʼ/]|[^\w]")

    return re.sub(symbols, " ", msg)


def lemmatization(msg, lang, cube):
    """

    :param lang: "ru", "ua" or "en"
    :param cube: only for "ua"an object after these commands cube = Cube(verbose=True); cube.load("uk")
    :return: cleaned text from synonyms
    """
    lemmas = ""

    try:
        with open(os.path.join("..", "dicts", f"dict_lemmatized_{lang}_words.json"), "r", encoding="utf-8") as f:
            dict_lemmatized_words = json.load(f)
    except FileNotFoundError:
        with open(os.path.join("dicts", f"dict_lemmatized_{lang}_words.json"), "r", encoding="utf-8") as f:
            dict_lemmatized_words = json.load(f)

    if lang == "ru":
        for word in msg.split():
            try:
                lemmas += " " + dict_lemmatized_words[word]

            except KeyError:
                lemma = pymorphy2.MorphAnalyzer().parse(np.unicode(word))[0].normal_form
                lemmas += " " + lemma
                dict_lemmatized_words[word] = lemma

    elif lang in ("ua", "en"):
        for word in msg.split():
            try:
                lemmas += " " + dict_lemmatized_words[word]

            except KeyError:
                sentence = cube(word)

                lemmas += " " + sentence[0][0].lemma
                dict_lemmatized_words[word] = sentence[0][0].lemma

    try:
        with open(os.path.join("..", "dicts", f"dict_lemmatized_{lang}_words.json"), "w", encoding="utf-8") as f:
            json.dump(dict_lemmatized_words, f, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        with open(os.path.join("dicts", f"dict_lemmatized_{lang}_words.json"), "w", encoding="utf-8") as f:
            json.dump(dict_lemmatized_words, f, indent=4, ensure_ascii=False)

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
            out_msg.append(delete_symbols(word))
    return re.sub(r"\s\s+", " ", " ".join(out_msg))


def transform_raw_data(msg, lang, function_type, cube, clean_type=''):
    msg = convert_lower_case(msg)
    msg = clean_message(msg)
    msg = re.sub(
        "\-\s\r\n\s{1,}|\-\s\r\n|\r\n", "", msg
    )  # deleting newlines and line-breaks
    msg = convert_numbers(msg, function_type)
    msg = remove_stop_words(msg, lang)

    if clean_type != 'without_lemma':
        msg = lemmatization(msg, lang, cube)
    return msg

