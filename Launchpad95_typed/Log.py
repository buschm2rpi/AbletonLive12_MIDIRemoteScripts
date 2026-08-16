import os
from datetime import datetime

LOGGING=True
LOG_DIRECTORY = "/tmp/Launchpad95_typed"
LOG_FILE = LOG_DIRECTORY + "/log.txt"

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

log_num = 0

def log(message):
    if LOGGING:
        with open(LOG_FILE, 'a') as f:
            if type(message) == list:
                message = '\n'.join(message)
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(str(dt) + ' ' + str(message) + '\n')