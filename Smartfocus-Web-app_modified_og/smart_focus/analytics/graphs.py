import pandas as pd
import os


def build_focus_graph(data_dir, user_name):
    sessions_file = os.path.join(data_dir, "sessions.csv")

    # If no data file
    if not os.path.exists(sessions_file):
        return {"labels": [], "values": []}

    df = pd.read_csv(sessions_file)

    # Clean user column
    df["user"] = df["user"].astype(str).str.strip().str.lower()
    user_name = user_name.strip().lower()

    # Filter by user
    df = df[df["user"] == user_name]

    if df.empty:
        return {"labels": [], "values": []}

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp")

    # Convert focused_seconds to minutes
    df["focused_minutes"] = df["focused_seconds"] / 60

    # Build graph data
    return {
        "labels": df["timestamp"].dt.strftime("%d %b %H:%M").tolist(),
        "values": df["focused_minutes"].round(2).tolist()
    }