import os
import logging
import argparse
import pandas as pd
from utils.data_transformation import prepare_message, add_subdialogs_ids, add_reply_time


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


def read_dialogs(dialog_id: str, dialog_path: str, prep_path: str) -> None:
    """
    Reads raw csv data and creates prepared copy
    at /data/prepared_dialogs/
    """
    logging.debug(f'Preparing dialog #{dialog_id}.')

    data = pd.read_csv(f'{dialog_path}{dialog_id}.csv')
    for i in data.index:
        data.loc[i, 'message'] = prepare_message(data.loc[i, 'message'])
    data = add_reply_time(data)
    data = add_subdialogs_ids(data)
    data.to_csv(f'{prep_path}{dialog_id}.csv')


if __name__ == "__main__":
    args = init_tool_config_arg()

    DIALOG_ID = args.dialogs_ids
    DEBUG_MODE = args.debug_mode
    DIALOG_PATH = 'data/dialogs/'
    PREPARED_PATH = 'data/prepared_dialogs/'

    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)

    if os.path.isdir(DIALOG_PATH):
        if not os.path.isdir(PREPARED_PATH):
            os.mkdir(PREPARED_PATH)

        for dialog in DIALOG_ID:
            read_dialogs(dialog, DIALOG_PATH, PREPARED_PATH)
    else:
        logging.error('Dialogs dir does not exist !')
