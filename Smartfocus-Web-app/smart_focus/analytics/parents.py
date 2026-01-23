import pandas as pd
import os

def get_parent_email(data_dir, user):
    file_path = os.path.join(data_dir, "users.csv")
    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
    except Exception:
        return None

    if df.empty:
        return None

    df["user"] = df["user"].str.lower()
    user = user.lower()

    row = df[df["user"] == user]
    if row.empty:
        return None

    return row.iloc[0]["parent_email"]