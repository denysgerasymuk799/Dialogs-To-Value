import os


# input dialogs_ids (it should be a list) or -1 for all, 
# which you want to add to general dialogs dataframe
DIALOGS_IDS = [-1]  # or such format -- DIALOGS_IDS = ['777000', '138918380', '147336686']
DEBUG_MODE = 0

PATH_TO_DIALOGS_CSV = os.path.join('data', 'dialogs')

# folder with jsons of dialogs_meta from 'telegram-data-collection/0_download_dialogs_list.py'
PATH_TO_DIALOGS_META = os.path.join("data", "dialogs_meta")

LOGS_PATH = os.path.join('logs', 'project_logs.log')

# name for general dialogs dataframe of 0_data_preprocessing.py
FINAL_DF_NAME = "general_df.csv"

# folder to save prepared (preprocessed) dialogs
PATH_TO_PREPARED_DIALOGS = os.path.join("data", "dialogs_prepared")

# folder to save results of modules
PATH_TO_SAVE_PROCESSED_FILES = os.path.join("data", "processed_dialog_files2")
PATH_TO_SAVE_GENERAL_DF = os.path.join(PATH_TO_SAVE_PROCESSED_FILES, FINAL_DF_NAME)

# path to save file with statistics of all members in each dialog
USER_PATH_TO_SAVE_GENERAL_DF = os.path.join(PATH_TO_SAVE_PROCESSED_FILES, 'user_stats.csv')
