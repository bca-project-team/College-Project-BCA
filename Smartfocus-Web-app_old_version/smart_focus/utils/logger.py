
import os
import csv
from datetime import datetime

DATA_DIR = None   # injected from app.py


def init_logger(data_dir):
    global DATA_DIR
    DATA_DIR = data_dir


def ensure_files():
    if DATA_DIR is None:
        raise RuntimeError("Logger not initialized. Call init_logger(DATA_DIR).")

    os.makedirs(DATA_DIR, exist_ok=True)

    session_file = os.path.join(DATA_DIR, "sessions.csv")
    timeline_file = os.path.join(DATA_DIR, "timeline.csv")

    if not os.path.exists(session_file):
        with open(session_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "user",
                "mode",
                "focused_seconds",
                "distracted_seconds",
                "goal_hours",
                "goal_achieved",
                "focus_score"
            ])

    if not os.path.exists(timeline_file):
        with open(timeline_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "user",
                "mode",
                "status"
            ])


def log_timeline(user, mode, status):
    ensure_files()
    with open(os.path.join(DATA_DIR, "timeline.csv"), "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user.strip().lower(),
            mode.strip().lower(),
            status
        ])


def log_session(summary):
    ensure_files()
    with open(os.path.join(DATA_DIR, "sessions.csv"), "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary["user"].strip().lower(),
            summary["mode"].strip().lower(),
            summary["focused_seconds"],
            summary["distracted_seconds"],
            summary["goal_hours"],
            summary["goal_achieved"],
            summary["focus_score"]
        ])
