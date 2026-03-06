import pandas as pd
import sqlite3
import os

DATA_DIR = "data"

csv_path = os.path.join(DATA_DIR, "sessions.csv")
db_path = os.path.join(DATA_DIR, "smartfocus.db")


def import_csv():

    if not os.path.exists(csv_path):
        print("sessions.csv not found")
        return

    df = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_path)

    df.to_sql(
        "sessions",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("CSV imported into database successfully")


if __name__ == "__main__":
    import_csv()