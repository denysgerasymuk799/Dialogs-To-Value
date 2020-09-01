import datetime
import math

import logging
import os

import pandas as pd
from cube.api import Cube
from pprint import pprint

from utils.text_data_transformation import transform_raw_data


def get_date_from_string(date_info: str):
    """
    Converts string with symbols to datetime obj.
    :param date_info: str
    :return: datetime.datetime()
    """
    date = date_info[:10].split("-") + date_info[11:19].split(":")
    return datetime.datetime(*[int(x) for x in date])


def get_digits_next_hundred(num):
    """
    Rounds given value to be divisible by 10
    :param num:
    :return:
    """
    return int(math.ceil(num / 100.0)) * 100


def add_reply_time(data):
    """
    Adds reply time between two users column @ given DataFrame (data)
    :param data: DataFrame
    :return: DataFrame
    """
    data["reply_time"] = ""
    data["raw_date"] = data.apply(
        lambda row: row["date"][:19].replace("-", " ").replace(":", " "), axis=1
    )
    for index, cur_row in data[::-1].iterrows():
        next_row = cur_row if index == data.index.size - 1 else data.iloc[index + 1]
        if next_row["from_id"] != cur_row["from_id"]:
            time_format = "%Y %m %d %H %M %S"
            time_diff = datetime.datetime.strptime(
                cur_row["raw_date"], time_format
            ) - datetime.datetime.strptime(next_row["raw_date"], time_format)
            data["reply_time"][index] = time_diff.total_seconds()
        else:
            data["reply_time"][index] = 0
    del data["raw_date"]


def get_reply_frequency(data):
    """
    Counts number of messages with ~same reply_time
    :param data: DataFrame
    :return: DataFrame
    """
    reply_frequency = {}
    for i in data.index:
        reply_time = get_digits_next_hundred(int(data["reply_time"][i]))
        if not reply_frequency.get(reply_time):
            reply_frequency.setdefault(reply_time, 1)
        else:
            reply_frequency[reply_time] += 1
    return reply_frequency


def add_subdialogs_ids(data):
    """
    Adds subdialog id column @ given DataFrame (data),
    based on calculated time between subdialogs:
    (( length of list of reply times rounded to be divisible by 10 sorted
    and reversed) / 100) * 40, which is the index of minimum subdialog time.
    Note: in DataFrame reply_time column should be.
    :param data: DataFrame
    :return: DataFrame
    """
    subdialog_count = 1
    data["subdialog_id"] = ""
    reply_frequency = get_reply_frequency(data)
    min_delay = sorted(list(reply_frequency.keys()))[
        -(round((len(reply_frequency) / 100) * 40))
    ]
    for i in data.index:
        reply_time = data["reply_time"][i]
        if reply_time > min_delay and reply_time:
            subdialog_count += 1
        data["subdialog_id"][i] = subdialog_count


def add_subdialogs_langs(data):
    n_subdialog, n_subdialog_msgs = 1, 0
    start_subdialog_n_row = 0
    subdialog_lang_lst = []
    previous_subdialog_id = 1

    for index, row in data.iterrows():
        if previous_subdialog_id != row.subdialog_id:
            # detect data language for data[start_subdialog_n_row: end_subdialog_n_row]
            lang = detect_data_language(data[start_subdialog_n_row: index])
            previous_subdialog_id = row.subdialog_id
            start_subdialog_n_row = index
            subdialog_lang_lst += [lang] * n_subdialog_msgs
            n_subdialog_msgs = 0

        n_subdialog_msgs += 1
        n_subdialog += 1

    # detect data language for data[start_subdialog_n_row: end_subdialog_n_row]
    lang = detect_data_language(data[start_subdialog_n_row: data.index[-1]])
    subdialog_lang_lst += [lang] * n_subdialog_msgs

    data["subdialog_language"] = subdialog_lang_lst


def prepare_dialogs(
    lang,
    cube,
    dialog_id,
    prep_path,
    dialog_path,
    start_date,
    end_date,
    function_type="",
    additional_options=""
):
    """
    Reads raw csv data and creates prepared copy
    at prep_path
    :return: None
    """
    logging.debug(f"Preparing dialog #{dialog_id}.")
    data = pd.read_csv(f"{dialog_path}/{dialog_id}.csv")

    data["preprocessed_message"] = data["message"]
    for index, row in data.iterrows():
        date_time = row["date"][:-6]
        dialog_datetime = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

        if dialog_datetime <= start_date:
            break

        # if start_date < dialog_datetime < end_date:
        if not pd.isnull(row["message"]):
            data.at[index, "preprocessed_message"] = transform_raw_data(
                data.loc[index, "preprocessed_message"], lang, function_type, cube
            )
            print(f"INDEX {index} from {data.index[-1]}")

    if additional_options == "add_lang_column":
        data["dialog_language"] = lang

    data.to_csv(f"{prep_path}/{dialog_id}.csv")
    logging.warning("saved dialog!")


def detect_data_language(data, data_type=""):
    key_letters = {
        "ua": {
            "є": 0,
            "і": 0,
            "ї": 0,
            "б": 0,
            "д": 0,
            "г": 0,
            "п": 0,
            "ц": 0,
            "я": 0,
            "ю": 0,
            "total": 0,
        },
        "ru": {
            "ё": 0,
            "б": 0,
            "д": 0,
            "г": 0,
            "п": 0,
            "ц": 0,
            "я": 0,
            "ю": 0,
            "ы": 0,
            "э": 0,
            "total": 0,
        },
        "en": {
            "d": 0,
            "f": 0,
            "g": 0,
            "j": 0,
            "q": 0,
            "r": 0,
            "s": 0,
            "v": 0,
            "w": 0,
            "z": 0,
            "total": 0,
        },
    }
    dialog_step_msgs = []
    n_msgs_to_analyse = 150
    if data_type == "subdialogs":
        n_msgs_to_analyse = 30

    if data.index[-1] < n_msgs_to_analyse - 1:
        msgs_step = 1

    else:
        # in such way with msgs_step I can get 150 messages
        # which are at the different parts of the dialog, so
        # when I analyse there 150 msgs I can get a real language
        msgs_step = data.index[-1] // n_msgs_to_analyse

    for i in range(0, data.index[-1], msgs_step):
        dialog_step_msgs.append(data["message"][i])

    for msg in dialog_step_msgs:
        if not pd.isnull(msg):
            for letter in msg:
                if letter in key_letters["ua"]:
                    lang = "ua"
                    key_letters[lang][letter] += 1

                if letter in key_letters["ru"]:
                    lang = "ru"
                    key_letters[lang][letter] += 1

                elif letter in key_letters["en"]:
                    lang = "en"
                    key_letters[lang][letter] += 1

    # get total sum of all values in languages dicts
    # in key_letters to detect the most common language
    mx_total, mx_total_lang = 0, ""
    for lang in key_letters.keys():
        key_letters[lang]["total"] = sum(key_letters[lang].values())
        if key_letters[lang]["total"] >= mx_total:
            mx_total_lang = lang
            mx_total = key_letters[lang]["total"]

    return mx_total_lang


def prepare_dialogs_sorted_by_lang(
    dialog_ids, dialog_path, prepared_path, start_date, end_date,
        additional_options=""
):
    dialog_ids_sorted_by_lang = {"ua": [], "ru": [], "en": []}
    if dialog_ids[0] == -1:
        for filename in os.listdir(dialog_path):
            data = pd.read_csv(f"{dialog_path}/{filename}")
            lang = detect_data_language(data)
            dialog_ids_sorted_by_lang[lang].append(filename[:-4])
    else:
        for dialog in dialog_ids:
            data = pd.read_csv(f"{dialog_path}/{dialog}.csv")
            lang = detect_data_language(data)
            dialog_ids_sorted_by_lang[lang].append(dialog)

    print("dialog_ids_sorted_by_lang")
    pprint(dialog_ids_sorted_by_lang)
    n_all_dialogs = sum(
        [
            len(dialog_ids_sorted_by_lang[lang])
            for lang in dialog_ids_sorted_by_lang.keys()
        ]
    )
    n_dialog = 0
    for lang in dialog_ids_sorted_by_lang.keys():
        if not dialog_ids_sorted_by_lang[lang]:
            continue

        cube = ""
        if lang == "ua":
            cube = Cube(verbose=True)
            cube.load("uk")

        elif lang == "en":
            cube = Cube(verbose=True)
            cube.load("en")

        for dialog_id in dialog_ids_sorted_by_lang[lang]:
            n_dialog += 1
            print(f"\n=======Language {lang} -- {n_dialog} from {n_all_dialogs}=======")
            prepare_dialogs(
                lang,
                cube,
                dialog_id,
                prepared_path,
                dialog_path,
                start_date,
                end_date,
                "words_frequency", additional_options
            )
