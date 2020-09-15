import datetime
import json
import logging
import os
import glob
import re

import pandas as pd

from config import DEBUG_MODE, LOGS_PATH, PATH_TO_DIALOGS_CSV, PATH_TO_PREPARED_DIALOGS, DIALOGS_IDS, \
    PATH_TO_SAVE_PROCESSED_FILES, PATH_TO_DIALOGS_META, FINAL_DF_NAME, PATH_TO_SAVE_GENERAL_DF
from utils.dialog_manipulation import prepare_dialogs_sorted_by_lang
from utils.dialog_manipulation import add_reply_time, add_subdialogs_ids


# change to date range in what you want to analyse messages of user_id_get_msg - from START_DATE to END_DATE;
# format "%Y-%m-%d %H:%M:%S"
START_DATE = datetime.datetime(2016, 8, 9, 0, 0, 0)
END_DATE = datetime.datetime(2020, 9, 8, 0, 0, 0)

if DEBUG_MODE:
    logging.basicConfig(filename=LOGS_PATH, level=logging.DEBUG)


if os.path.isdir(PATH_TO_DIALOGS_CSV):
    if not os.path.isdir(PATH_TO_PREPARED_DIALOGS):
        os.mkdir(PATH_TO_PREPARED_DIALOGS)

    prepare_dialogs_sorted_by_lang(DIALOGS_IDS, PATH_TO_DIALOGS_CSV, PATH_TO_PREPARED_DIALOGS,
                                   START_DATE, END_DATE, "add_lang_column")

else:
    logging.error('Dialogs dir does not exist !')

flag_get_all = 0

if DIALOGS_IDS[0] == -1:
    DIALOGS_IDS = glob.glob(f"{PATH_TO_PREPARED_DIALOGS}/*.csv")
    flag_get_all = 1

if not os.path.isdir(PATH_TO_SAVE_PROCESSED_FILES):
    os.mkdir(PATH_TO_SAVE_PROCESSED_FILES)

# get general json with short info about all dialogs_meta
dialogs_info = {
    "Private dialog": {},
    "Group": {},
    "Channel": {}
}

# make dialogs_info dict: first level keys - "Channel", "Private dialog", "Group"
# second level items - "<name_of_dialog>": <id>
for file in os.listdir(PATH_TO_DIALOGS_META):
    if file[-4:] == "json":
        try:
            with open(os.path.join(PATH_TO_DIALOGS_META, file), "r", encoding="utf8") as meta_file:
                data = json.load(meta_file)

            dialogs_info[data["type"]][data["id"]] = data["name"]
        except KeyError:
            print(f"File {file} was not included in all_dialogs_info.json")

# save results
with open(os.path.join(PATH_TO_SAVE_PROCESSED_FILES, "all_dialogs_info.json"), "w", encoding="utf-8") as f:
    json.dump(dialogs_info, f, indent=4, ensure_ascii=False)


frames = []

general_df = pd.DataFrame()

general_n_subdialogs = 0
general_dialog_id = 0
len_dialogs = len(DIALOGS_IDS)

for n_dialog_id, dialog_file in enumerate(DIALOGS_IDS):
    dialog_id = os.path.basename(dialog_file)

    if dialog_id == FINAL_DF_NAME or\
            not dialog_id[1].isdigit():
        print(f"=========WARNING: This file is not a dialog csv {dialog_id}\n we do not add it to general dataframe")
        continue

    if flag_get_all == 1:
        dialog_id = dialog_id[:-4]
        data = pd.read_csv(dialog_file)

    else:
        data = pd.read_csv(os.path.join(PATH_TO_PREPARED_DIALOGS, dialog_file + '.csv'))

    dialog_name = 'No dialog name'
    for type_dialog in dialogs_info.keys():
        try:
            dialog_name = dialogs_info[type_dialog][int(dialog_id)]
            break
        except KeyError:
            pass

    data["dialog_name"] = dialog_name
    data["reply_btw_sender_time"], data["reply_btw_own_time"] = add_reply_time(data)
    data["subdialog_id"] = add_subdialogs_ids(data)
    data["dialog ID"] = dialog_id

    # extract channel or group id
    try:
        to_id = re.search(r"\((.*?)\)", data["to_id"][0])
        to_id = to_id.group()[1:-1]
        pos_start = to_id.find('_')
        pos_end = to_id.find('=')
        to_id = to_id[:pos_start + 1] + to_id[pos_end + 1:]
        data["to_id"] = to_id
    except TypeError:
        print(f"data['to_id'] in private chat {dialog_name} was not changed\n")

    general_df = pd.concat([general_df, data])
    print(f"{n_dialog_id + 1} dialogs2 csv from {len_dialogs} succeeded")

general_df.rename(columns={'id': 'message_id'}, inplace=True)

try:
    general_df = general_df.drop("Unnamed: 0", axis=1)
    general_df = general_df.drop("Unnamed: 0.1", axis=1)
except Exception as err:
    print(f"===========ERROR: {err}")

cols = ['dialog ID', "dialog_name", "message_id", "date", "from_id", 'to_id', 'fwd_from', 'dialog_language',
        'reply_btw_sender_time', 'reply_btw_own_time', 'subdialog_id', 'message', 'preprocessed_message']

rest_cols = [col for col in general_df.columns if col not in cols]

# place long text columns at the end of df
cols = cols[:-2] + rest_cols + cols[-2:]
general_df = general_df[cols]

general_df.to_csv(PATH_TO_SAVE_GENERAL_DF, index=False)
print(f"Check {PATH_TO_SAVE_PROCESSED_FILES} to see results")
