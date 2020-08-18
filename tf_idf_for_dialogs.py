import datetime
import json
import os
import pandas as pd
import logging

from utils.data_transformation import prepare_dialogs, if_in_date_range


def calculate_df(dialog_data, date_before, date_after, user_id_get_msg, dialog_id):
    """

    :param dialog_data: a pandas dataframe of dialogs
    :param date_before: datetime type, from what time start to analyse msgs
    :param date_after: datetime type, to what time to analyse msgs
    :param user_id_get_msg: a user chat id, who msgs to analyse or "all" - for all participants of the dialog
    :param dialog_id: str
    :return: a sorted df - sorted dict of user_id_get_msg most used words
    """
    DF = {}
    file_text = ""

    for row in dialog_data.index:
        if user_id_get_msg != "all":
            if dialog_data["from_id"][row] != user_id_get_msg:
                continue

        if if_in_date_range(dialog_data["date"][row][:-6], date_before, date_after) == 'Dialog after date_after':
            continue

        elif if_in_date_range(dialog_data["date"][row][:-6], date_before, date_after):
            if not pd.isnull(dialog_data["message"][row]):
                file_text += dialog_data["message"][row] + " "
                for w in dialog_data["message"][row].split():
                    try:
                        DF[w] += 1
                    except:
                        DF[w] = 1
        else:
            break

    with open("../static/{}/1_{}.txt".format(dialog_id, dialog_id), "w", encoding="utf-8") as f:
        f.write(file_text)

    DF_sorted = {k: v for k, v in sorted(DF.items(), key=lambda item: item[1], reverse=True)}
    return DF_sorted


if __name__ == '__main__':
    logging.basicConfig(filename='../logs/project_logs.log', level=0)
    logging.info("starting logs for tf_idf_dialogs")

    # 0) in console input: import nltk; nltk.download()
    #
    # Install (or update) NLP-Cube with:
    # pip3 install -U nlpcube
    #
    # use telegram-data-collection/0_download_dialogs_list.py and 1_download_dialogs_data.py
    # to get some files to analyse
    # files SHOULD be in data/dialogs and data/dialogs_meta

    # 1) change a dialog_id, which you want to investigate
    dialog_id = "347963763"

    # 2) change user_id_get_msg
    # int type - user chat id, who massages you want to analyse,
    # you can find it in <dialog_id>.csv
    # str type "all" if you want to analyse nsgs of all users of the dialog
    user_id_get_msg = 511986933
    dialog_path = "../data/dialogs/"
    prep_path = '../data/prepared_dialogs/'

    # 3) change to date range in what you want to analyse messages of user_id_get_msg - from date_before to date_after;
    # format "%Y-%m-%d %H:%M:%S"
    date_before = datetime.datetime(2020, 7, 9, 0, 0, 0)
    date_after = datetime.datetime(2020, 8, 10, 0, 0, 0)

    if not os.path.exists("../static/{}".format(dialog_id)):
        os.mkdir("../static/{}".format(dialog_id))

    # 4) change "ua" to a language of your dialog ("ua", "ru" or "en")
    # if you write "ua" or "ru" - dialog will be cleaned from stop_words_ua + stop_words_ru + stop_words_en
    # so do not bother about these languages if you can not write an exactly language of the dialog
    prepare_dialogs(dialog_id, dialog_path, prep_path, date_before,
                    date_after, "ru", "words_frequency")

    dialog_data = pd.read_csv("../data/prepared_dialogs/{}.csv".format(dialog_id))

    DF_sorted = calculate_df(dialog_data, date_before, date_after, user_id_get_msg, dialog_id)

    with open("../static/{}/words_frequency1_{}.json".format(dialog_id, dialog_id), "w", encoding="utf-8") as f:
        json.dump(DF_sorted, f, indent=4, ensure_ascii=False)

    # 4) after work of this module look at results in static/<dialog_id> dir
    # use command under to make a wordcloud, to understand its parameters use - wordcloud_cli --help
    # wordcloud_cli --text static/<dialog_id>/1_<dialog_id>.txt --mask static/logo_telegram.jpg --imagefile static/my_words_nazar2.png
    print(DF_sorted)
