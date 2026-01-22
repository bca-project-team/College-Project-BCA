import pandas as pd
import os


def build_focus_graph(data_dir, user_name):
    timeline_file = os.path.join(data_dir, "timeline.csv")

    if not os.path.exists(timeline_file):
        return None

    df = pd.read_csv(timeline_file)

    # ---------------------------
    # Clean data
    # ---------------------------
    df["user"] = df["user"].astype(str).str.strip().str.lower()
    df["status"] = df["status"].astype(str).str.strip().str.lower()

    user_name = user_name.strip().lower()
    df = df[df["user"] == user_name]

    if df.empty:
        return None

    # ---------------------------
    # Parse + format timestamp
    # ---------------------------
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Convert to readable time for Chart.js
    df["time_label"] = df["timestamp"].dt.strftime("%H:%M:%S")

    # ---------------------------
    # Build graph data
    # ---------------------------
    y_values = []
    for s in df["status"]:
        if s == "focused":
            y_values.append(1)
        else:
            y_values.append(0)

    return {
        "x": df["time_label"].tolist(),
        "y": y_values
    }