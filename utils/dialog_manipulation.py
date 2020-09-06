import datetime
import logging
import os
from pprint import pprint

import pandas as pd
# from cube.api import Cube

from utils.text_data_transformation import transform_raw_data


def add_reply_time(data: pd.DataFrame):
    """
    Returns reply time columns between two users
    column @ given DataFrame (data)
    """

    reply_btw_sender_time, reply_btw_own_time = [], []
    for index, cur_row in data[::-1].iterrows():
        next_row = cur_row if index == data.index.size - 1 else data.iloc[index + 1]
        time_format = "%Y-%m-%d %H:%M:%S"
        time_diff = datetime.datetime.strptime(cur_row["date"][:19], time_format) \
                    - datetime.datetime.strptime(next_row["date"][:19], time_format)
        if next_row["from_id"] != cur_row["from_id"]:
            reply_btw_sender_time.append(time_diff.total_seconds())
            reply_btw_own_time.append(0)
        else:
            reply_btw_sender_time.append(0)
            reply_btw_own_time.append(time_diff.total_seconds())

    return reply_btw_sender_time, reply_btw_own_time


def get_avg_subdialog_reply_time(data: pd.DataFrame) -> float:
    """
    Finds average reply time after which it is considered
    that two messages are @ separate subdialogs.
    """
    reply_values = sorted({row['reply_btw_sender_time'] for index, row in data.iterrows()})
    if not reply_values:
        logging.error("No reply time data !")
    cut_off = int(len(reply_values) / 100 * 10)
    reply_values = reply_values[cut_off:-cut_off] if cut_off else reply_values
    return reply_values[int(len(reply_values) / 100 * 50)]


def add_subdialogs_ids(data: pd.DataFrame):
    """
    Returns subdialog id column @ given DataFrame (data),
    based on calculated time between subdialogs:
    Note: reply_time column should be in pd.DataFrame.
    """
    subdialog_count = 1
    subdialog_ids = [1]
    # subdialog_count = data["subdialog_id"] = 1
    min_delay = get_avg_subdialog_reply_time(data)
    for index, rows in data[:len(data) - 1].iterrows():
        reply_time = data.loc[index, "reply_btw_sender_time"]
        if reply_time > min_delay and reply_time:
            subdialog_count += 1
        subdialog_ids.append(subdialog_count)

    return subdialog_ids


def add_typing_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns typing speed column with WPM (words per min)
    and CPM (characters per minute) in each subdialog.
    """

    def get_msg_typing_time(row):
        time = row['reply_btw_own_time'] if row['reply_btw_own_time'] else row['reply_btw_sender_time']
        if not time:
            return 0
        else:
            return time / 60

    output = {'wpm': [], 'cpm': []}
    for subdialog in list(df.groupby(['subdialog_id']).groups.keys()):
        gdf = df.groupby(df.subdialog_id).get_group(subdialog)[:-1:]
        output['wpm'] += list(
            gdf.apply(lambda row: round(len(row['message'].split()) / get_msg_typing_time(row)), axis=1)) + [0]
        output['cpm'] += list(
            gdf.apply(lambda row: round(len(row['message']) / get_msg_typing_time(row)), axis=1)) + [0]
    return pd.DataFrame(output)


def add_subdialogs_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns columns with average stats for each subdialog
    and with subdialog and dialog ID.
    """
    output_df = pd.concat([df['dialog_id'], df['subdialog_id']], axis=1, keys=['dialog_id', 'subdialog_id'])
    adf = pd.DataFrame()
    for dialog in list(df.groupby(['dialog_id']).groups.keys()):
        gdf = df.groupby(df.dialog_id).get_group(dialog)
        tdf = gdf.groupby('subdialog_id').agg(
            words_num=pd.NamedAgg('message', aggfunc=lambda x: round(x.apply(lambda y: len(str(y).split())).mean(), 1)),
            reply_time=pd.NamedAgg('reply_btw_sender_time', aggfunc=lambda x: round(x.mean(), 1)),
            message_number=pd.NamedAgg('from_id', aggfunc=lambda x: int(len(x))),
            # chars_num=pd.NamedAgg('message', aggfunc=lambda x: x.apply(lambda y: len(str(y))).mean()),
        )  # TODO: ^ why cannot aggregate same column multiple times in df??
        tdf['dialog_id'] = dialog
        adf = pd.concat([adf, tdf])
    output_df = pd.merge(output_df, adf, how='left', on=list(output_df.keys()))
    # output_df.drop(['dialog_id', 'subdialog_id'], axis=1, inplace=True)
    return output_df


def add_sleep_bounds(data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns avg sleep bounds for each user per weekdays.
    """
    # TODO: need to create new dataframe struct.
    pass


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

        if dialog_datetime < start_date:
            break

        if start_date <= dialog_datetime <= end_date:
            if not pd.isnull(row["message"]):
                data.at[index, "preprocessed_message"] = transform_raw_data(
                    data.loc[index, "preprocessed_message"], lang, function_type, cube
                )
                print(f"INDEX {index} from {data.index[-1]}")

    if additional_options == "add_lang_column":
        data["dialog_language"] = lang

    data.to_csv(f"{prep_path}/{dialog_id}.csv", index=False)
    logging.warning("saved dialog!")


# TODO: add proper handler for empty message
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

    #     print(len(data))
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
            for letter in str(msg):
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
    mx_total, mx_total_lang = 0, "ru"

    for lang in key_letters.keys():
        key_letters[lang]["total"] = sum(key_letters[lang].values())
        if key_letters[lang]["total"] > mx_total:
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
            if f"{dialog_id}.csv" in os.listdir(prepared_path):
                print(f"=========WARNING: {dialog_id}.csv already in {prepared_path}")
                n_dialog += 1
                continue

            n_dialog += 1
            print(f"\n=======Language {lang}, dialog_id {dialog_id}-- {n_dialog} from {n_all_dialogs}=======")
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
