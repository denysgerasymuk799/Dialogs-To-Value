import argparse


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