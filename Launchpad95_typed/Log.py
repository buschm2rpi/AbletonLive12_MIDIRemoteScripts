import os
from datetime import datetime

LOGGING: bool = True
LOG_DIRECTORY: str = "/tmp/Launchpad95_typed"
LOG_FILE: str = LOG_DIRECTORY + "/log.txt"

if LOGGING:
    try:
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
    except TypeError:
        try:
            os.makedirs(LOG_DIRECTORY)
        except OSError:
            pass
            
    with open(LOG_FILE, 'a') as f:
        f.write('====================\n')

log_num: int = 0

def log(message: str | list[str]) -> None:
    if LOGGING:
        with open(LOG_FILE, 'a') as f:
            if type(message) == list:
                message = '\n'.join(message)
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(str(dt) + ' ' + str(message) + '\n')