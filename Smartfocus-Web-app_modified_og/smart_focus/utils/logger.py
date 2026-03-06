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

    # -----------------------------
    # Create summary data
    # -----------------------------
    summary_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **summary
    }

    # -----------------------------
    # SAVE TO DATABASE
    # -----------------------------
    import sqlite3

    db_path = os.path.join(DATA_DIR, "smartfocus.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sessions (
        timestamp,
        user,
        mode,
        activity,
        goal_hours,
        focused_seconds,
        distracted_seconds,
        focused_minutes,
        focus_score,
        goal_achieved,
        total_seconds
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        summary_data["timestamp"],
        summary_data["user"],
        summary_data["mode"],
        summary_data["activity"],
        summary_data["goal_hours"],
        summary_data["focused_seconds"],
        summary_data["distracted_seconds"],
        summary_data["focused_minutes"],
        summary_data["focus_score"],
        int(summary_data["goal_achieved"]),
        summary_data["total_seconds"]
    ))

    conn.commit()
    conn.close()

    # -----------------------------
    # SAVE TO CSV
    # -----------------------------
    file_path = os.path.join(DATA_DIR, "sessions.csv")

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=summary_data.keys()
        )

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