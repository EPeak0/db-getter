import os
from appdirs import user_config_dir

APP_NAME = "db_getter"

def get_persistent_config_path(filename : str):
    config_dir = user_config_dir(APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, filename)