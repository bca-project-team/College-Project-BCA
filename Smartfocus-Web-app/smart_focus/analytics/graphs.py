import pandas as pd
import matplotlib.pyplot as plt

TIMELINE_FILE = "data/timeline.csv"


def plot_focus_progress(user_name):
    df = pd.read_csv(TIMELINE_FILE)

    df = df[df["user"] == user_name]

    if df.empty:
        print("No data found for user")
        return

    # Convert status to numeric
    df["focus_score"] = df["status"].apply(
        lambda x: 1 if x == "Focused" else 0
    )

    df["time_index"] = range(len(df))

    plt.figure(figsize=(10, 4))
    plt.plot(df["time_index"], df["focus_score"], marker="o")
    plt.yticks([0, 1], ["Distracted", "Focused"])
    plt.xlabel("Time")
    plt.ylabel("Focus Status")
    plt.title("Focus Progress / Degradation Over Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()