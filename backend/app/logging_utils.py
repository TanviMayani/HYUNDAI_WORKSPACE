import os
import json
from datetime import datetime

LOGS_FOLDER = 'logs'

def logger(level, status_code, message, endpoint, traceback_id=None):
    """
    Generate log data and store it in a local file, day-wise.
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime('%H:%M:%S') 
    
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    log_date = current_time.strftime('%Y-%m-%d')
    log_file_path = os.path.join(LOGS_FOLDER, f'{log_date}.log')

    log_data = {
        'level': level,
        'status_code': status_code,
        'message': message,
        'endpoint': endpoint,
        'traceback_id': traceback_id
    }

    formatted_log = f'{formatted_time} {json.dumps(log_data)[1:-1]}'

    with open(log_file_path, 'a') as log_file:
        log_file.write(formatted_log + '\n')

    print(formatted_log)
