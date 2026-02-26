import pandas as pd
from datetime import datetime, timedelta
import os


def get_weekly_report(data_dir, user):
    if not user:
        return None
    session_file = os.path.join(data_dir, "sessions.csv")

    if not os.path.exists(session_file):
        return None

    df = pd.read_csv(session_file)
    df["user"] = df["user"].str.lower()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    user = user.lower()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    df = df[
        (df["user"] == user) &
        (df["timestamp"] >= start_date)
    ]

    if df.empty:
        return None

    df["focused_minutes"] = df["focused_seconds"] / 60

    return {
        "total_focus_minutes": int(df["focused_minutes"].sum()),
        "average_daily_minutes": int(df["focused_minutes"].mean()),
        "goal_days": int(df["goal_achieved"].sum()),
        "best_day": df.loc[df["focused_minutes"].idxmax()]["timestamp"].strftime("%A"),
        "worst_day": df.loc[df["focused_minutes"].idxmin()]["timestamp"].strftime("%A"),
        "days_tracked": len(df)
    }

def get_monthly_report(data_dir, user):
    if not user:
        return None
    session_file = os.path.join(data_dir, "sessions.csv")

    if not os.path.exists(session_file):
        return None

    df = pd.read_csv(session_file)
    df["user"] = df["user"].str.lower()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    user = user.lower()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    df = df[
        (df["user"] == user) &
        (df["timestamp"] >= start_date)
    ]

    if df.empty:
        return None

    df["focused_minutes"] = df["focused_seconds"] / 60

    return {
        "total_focus_minutes": int(df["focused_minutes"].sum()),
        "average_daily_minutes": int(df["focused_minutes"].mean()),
        "days_tracked": len(df)
    }