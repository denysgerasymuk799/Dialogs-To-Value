import argparse
import datetime as dat
import math
import os
import pandas as pd


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
    data['reply_time'] = ''
    data['raw_date'] = data.apply(lambda row: row['date'][:19].replace('-', ' ').replace(':', ' '), axis=1)
    for index, cur_row in data[::-1].iterrows():
        next_row = cur_row if index == data.index.size - 1 else data.iloc[index + 1]
        if next_row['from_id'] != cur_row['from_id']:
            time_format = '%Y %m %d %H %M %S'
            time_diff = (dat.datetime.strptime(cur_row['raw_date'], time_format)
                         - dat.datetime.strptime(next_row['raw_date'], time_format))
            data['reply_time'][index] = time_diff.total_seconds()
        else:
            data['reply_time'][index] = 0
    del data['raw_date']


def get_reply_frequency(data):
    """
    Counts number of messages with ~same reply_time
    :param data: DataFrame
    :return: DataFrame
    """
    reply_frequency = {}
    for i in data.index:
        reply_time = get_digits_next_hundred(int(data['reply_time'][i]))
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
    data['subdialog_id'] = ''
    reply_frequency = get_reply_frequency(data)
    min_delay = sorted(list(reply_frequency.keys()))[-(round((len(reply_frequency) / 100) * 40))]
    for i in data.index:
        reply_time = data['reply_time'][i]
        if reply_time > min_delay and reply_time:
            subdialog_count += 1
        data['subdialog_id'][i] = subdialog_count


if __name__ == '__main__':
    # change to yours
    path_to_prepared_dialogs = os.path.join("..", "data", "prepared_dialogs")
    path_to_processed_files = "../data/processed_dialog_files/"

    DIALOGS_IDS = -1
    if DIALOGS_IDS == -1:
        DIALOGS_IDS = os.listdir(path_to_prepared_dialogs)

    for dialog_id in DIALOGS_IDS:
        dialog_id = str(dialog_id)[:-4]
        data = pd.read_csv(os.path.join("..", "data", "prepared_dialogs", f"{dialog_id}.csv"))
        add_reply_time(data)
        add_subdialogs_ids(data)
        # print(data)

        if not os.path.exists(path_to_processed_files):
            os.mkdir(path_to_processed_files)

        if not os.path.exists(path_to_processed_files + dialog_id):
            os.mkdir(path_to_processed_files + dialog_id)

        data.to_csv(os.path.join(path_to_processed_files + dialog_id, f"subdialogs_{dialog_id}.csv"))
