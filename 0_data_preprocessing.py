import datetime
import logging
import os
import glob
import pandas as pd

from utils.dialog_manipulation import prepare_dialogs_sorted_by_lang
from utils.dialog_manipulation import add_reply_time, add_subdialogs_ids

# args = init_args()


# DIALOGS_IDS = args.dialogs_ids
# DEBUG_MODE = args.debug_mode


# input dialogs_ids (it should be a list) or -1 for all
DIALOGS_IDS = [-1]
DEBUG_MODE = 0
DIALOG_PATH = os.path.join('data', 'new_type_dialogs')
LOGS_PATH = 'logs/project_logs.log'

FINAL_DF_NAME = "general_df.csv"
PATH_TO_PREPARED_DIALOGS = os.path.join("data", "new_type_dialogs_prepared")
PATH_TO_SAVE_GENERAL_DF = os.path.join("data", "new_type_dialogs_prepared", FINAL_DF_NAME)

# change to date range in what you want to analyse messages of user_id_get_msg - from START_DATE to END_DATE;
# format "%Y-%m-%d %H:%M:%S"
START_DATE = datetime.datetime(2016, 8, 9, 0, 0, 0)
END_DATE = datetime.datetime(2020, 9, 4, 0, 0, 0)

if DEBUG_MODE:
    logging.basicConfig(filename=LOGS_PATH, level=logging.DEBUG)

if os.path.isdir(DIALOG_PATH):
    if not os.path.isdir(PATH_TO_PREPARED_DIALOGS):
        os.mkdir(PATH_TO_PREPARED_DIALOGS)

    prepare_dialogs_sorted_by_lang(DIALOGS_IDS, DIALOG_PATH, PATH_TO_PREPARED_DIALOGS,
                                   START_DATE, END_DATE, "add_lang_column")

else:
    logging.error('Dialogs dir does not exist !')

flag_get_all = 0

if DIALOGS_IDS[0] == -1:
    DIALOGS_IDS = glob.glob(f"{PATH_TO_PREPARED_DIALOGS}/*.csv")
    flag_get_all = 1

frames = []

general_df = pd.DataFrame()
general_n_subdialogs = 0
general_dialog_id = 0
len_dialogs = len(DIALOGS_IDS)

for n_dialog_id, dialog_file in enumerate(DIALOGS_IDS):
    dialog_id = dialog_file.split('/')[-1]

    if dialog_id == os.path.join(PATH_TO_PREPARED_DIALOGS, FINAL_DF_NAME) or\
            not dialog_id[dialog_id.rfind('\\') + 2].isdigit():
        print(f"=========WARNING: This file is not a dialog csv {dialog_id}\n we do not at it to general dataframe")
        continue

    if flag_get_all == 1:
        dialog_id = str(dialog_id)[:-4]

    data = pd.read_csv(dialog_file)

    data["reply_btw_sender_time"], data["reply_btw_own_time"] = add_reply_time(data)
    data["subdialog_id"] = add_subdialogs_ids(data)

    data["dialog ID"] = n_dialog_id

    general_df = pd.concat([general_df, data])
    print(f"{n_dialog_id + 1} dialogs csv from {len_dialogs} succeeded")

general_df.rename(columns={'id': 'message_id'}, inplace=True)

try:
    general_df = general_df.drop("Unnamed: 0", axis=1)
    general_df = general_df.drop("Unnamed: 0.1", axis=1)
except Exception as err:
    print(f"===========ERROR: {err}")

cols = ['dialog ID', "message_id", "date", "from_id", 'to_id', 'fwd_from', 'dialog_language',
        'reply_btw_sender_time', 'reply_btw_own_time', 'subdialog_id', 'message', 'preprocessed_message']

rest_cols = [col for col in general_df.columns if col not in cols]

# place long text columns at the end of df
cols = cols[:-2] + rest_cols + cols[-2:]
general_df = general_df[cols]

general_df.to_csv(PATH_TO_SAVE_GENERAL_DF, index=False)
