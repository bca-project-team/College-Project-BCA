import pandas as pd
import os

def build_focus_graph(data_dir, user_name):
    timeline_file = os.path.join(data_dir, "timeline.csv")

    if not os.path.exists(timeline_file):
        return None

    df = pd.read_csv(timeline_file)
    df["user"] = df["user"].str.strip().str.lower()
    df["status"] = df["status"].str.strip().str.lower()

    user_name = user_name.strip().lower()
    df = df[df["user"] == user_name]

    if df.empty:
        return None

    return {
        "x": df["timestamp"].tolist(),
        "y": [1 if s == "focused" else 0 for s in df["status"]]
    }