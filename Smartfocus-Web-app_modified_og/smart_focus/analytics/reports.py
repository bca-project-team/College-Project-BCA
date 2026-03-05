import pandas as pd
from datetime import datetime, timedelta
import os
def get_focus_heatmap(data_dir, user):

    session_file = os.path.join(data_dir, "sessions.csv")

    if not os.path.exists(session_file):
        return []

    df = pd.read_csv(session_file)

    df["user"] = df["user"].str.lower()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    now=datetime.now()
    df=df[(df['timestamp'].dt.month==now.month)&(df['timestamp'].dt.year==now.year)]

    df = df[df["user"] == user.lower()]

    df["date"] = df["timestamp"].dt.date

    daily_focus = df.groupby("date")["focused_seconds"].sum().reset_index()

    def get_level(sec):
        if sec == 0:
            return 0
        elif sec < 1800:
            return 1
        elif sec < 3600:
            return 2
        else:
            return 3

    daily_focus["level"] = daily_focus["focused_seconds"].apply(get_level)

    return daily_focus.to_dict(orient="records")

def format_time(seconds):
    seconds=int(seconds)
    hours=seconds//3600
    minutes=(seconds%3600)//60
    secs=seconds%60
    if hours:
        return f'{hours} hr {minutes} min'
    if minutes:
        return f'{minutes} min {secs} sec'
    return f'{secs} sec'

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

    # Convert seconds to minutes
    df["focused_minutes"] = df["focused_seconds"] / 60

    # Extract date and day
    df["date"] = df["timestamp"].dt.date
    df["day"] = df["timestamp"].dt.day_name()

    # Sessions tracked
    sessions_tracked = len(df)

    # Unique days tracked
    days_tracked = df["date"].nunique()

    # Total focus
    total_seconds= int(df["focused_minutes"].sum())
    total_focus=format_time(total_seconds)

    # Average daily focus
    avg_seconds=int(total_seconds / days_tracked) if days_tracked>0 else 0
    avg_daily=format_time(avg_seconds)

    # Aggregate per day
    daily_focus = df.groupby("day")["focused_minutes"].sum()

    return {
        "total_focus": total_focus,
        "average_daily": avg_daily,
        "sessions_tracked": sessions_tracked,
        "days_tracked": days_tracked,
        "goal_days": int(df["goal_achieved"].sum()),
        "best_day": daily_focus.idxmax(),
        "worst_day": daily_focus.idxmin()
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
    df["date"] = df["timestamp"].dt.date
    df["day"] = df["timestamp"].dt.day_name()

    sessions_tracked = len(df)
    days_tracked = df["date"].nunique()

    
    # Total focus
    total_seconds= int(df["focused_minutes"].sum())
    total_focus=format_time(total_seconds)

    # Average daily focus
    avg_seconds=int(total_seconds / days_tracked) if days_tracked>0 else 0
    avg_daily=format_time(avg_seconds)

    daily_focus = df.groupby("day")["focused_minutes"].sum()

    return {
        "total_focus": total_focus,
        "average_daily": avg_daily,
        "sessions_tracked": sessions_tracked,
        "days_tracked": days_tracked,
        "goal_days": int(df["goal_achieved"].sum()),
        "best_day": daily_focus.idxmax(),
        "worst_day": daily_focus.idxmin()
    }