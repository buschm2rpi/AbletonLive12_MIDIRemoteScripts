from __future__ import annotations

import os
from typing import Union

from .Settings import Settings

USER_HOME = os.path.expanduser("~")
LOG_DIRECTORY = USER_HOME + "/Documents/Ableton/User Library/Remote Scripts"
LOG_FILE = LOG_DIRECTORY + "/log.txt"

log_num: int = 0


def log(message: Union[str, list[str]]) -> None:
    global log_num
    if Settings.LOGGING:
        try:
            os.makedirs(LOG_DIRECTORY, exist_ok=True)
        except TypeError:
            try:
                os.makedirs(LOG_DIRECTORY)
            except OSError:
                pass
        with open(LOG_FILE, "a") as f:
            if isinstance(message, list):
                message = "\n".join(message)
            f.write(str(log_num) + " " + str(message) + "\n")
        log_num += 1
