import os
import csv
from datetime import datetime

DATA_DIR = None  # injected from app.py


def init_logger(data_dir):
    global DATA_DIR
    DATA_DIR = data_dir
    os.makedirs(DATA_DIR, exist_ok=True)


def log_session(summary):
    if DATA_DIR is None:
        raise RuntimeError("Logger not initialized. Call init_logger(DATA_DIR).")

    file_path = os.path.join(DATA_DIR, "sessions.csv")
    file_exists = os.path.exists(file_path)

    # Add timestamp dynamically
    summary_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **summary
    }

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(summary_data)


# OPTIONAL: Keep timeline if needed
def log_timeline(user, mode, status):
    if DATA_DIR is None:
        raise RuntimeError("Logger not initialized. Call init_logger(DATA_DIR).")

    file_path = os.path.join(DATA_DIR, "timeline.csv")
    file_exists = os.path.exists(file_path)

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user.strip().lower(),
        "mode": mode.strip().lower(),
        "status": status
    }

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)