import json
import os
from datetime import datetime
from pathlib import Path

from config import DisplayTableEncoder

LOGS_FOLDER_NAME = "logs"


class GameLog:
    def __init__(self):
        if not Path(LOGS_FOLDER_NAME).is_dir():
            os.mkdir(LOGS_FOLDER_NAME)

        # Get the current timestamp with milliseconds
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]

        # Use the timestamp in your filename
        self.filename = f"{LOGS_FOLDER_NAME}/game_{timestamp}_log.json"
        self.logs = []

    def write_log(self):
        log_data = [
            {"timestamp": log["timestamp"], "log": log["log"]} for log in self.logs
        ]

        with open(self.filename, "w") as f:
            json.dump(
                log_data, f, indent=4, cls=DisplayTableEncoder
            )  # Use the custom encoder

    def add_log(self, log):
        # Get the current timestamp with milliseconds
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
        log_entry = {"timestamp": timestamp, "log": log}
        self.logs.append(log_entry)
        self.save_logs()  # Save to JSON after each log

    def save_logs(self):
        self.write_log()
