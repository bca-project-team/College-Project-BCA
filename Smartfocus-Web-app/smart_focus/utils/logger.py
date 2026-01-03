import csv
import os
from datetime import datetime

DATA_DIR = "data"
SESSION_FILE = os.path.join(DATA_DIR, "sessions.csv")
TIMELINE_FILE = os.path.join(DATA_DIR, "timeline.csv")


def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "user",
                "mode",
                "focused_seconds",
                "distracted_seconds",
                "goal_hours",
                "goal_achieved"
            ])

    if not os.path.exists(TIMELINE_FILE):
        with open(TIMELINE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "user",
                "mode",
                "status"
            ])


def log_timeline(user, mode, status):
    ensure_files()
    with open(TIMELINE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user,
            mode,
            status
        ])


def log_session(summary):
    ensure_files()
    with open(SESSION_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary["user"],
            summary["mode"],
            summary["focused_seconds"],
            summary["distracted_seconds"],
            summary["goal_hours"],
            summary["goal_achieved"]
        ])