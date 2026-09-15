import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join("data", "weather_database.db")


def inspect_database():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        tables_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
        if tables_df.empty:
            print("[INFO] No tables found in the database.")
            return

        print("=== SQLITE DATABASE TABLES ===")
        print(tables_df.to_string(index=False))
        print("==============================\n")

        for table_name in tables_df["name"]:
            print(f"--- Table: {table_name} ---")
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10;", conn)
            print(df.to_string(index=False))
            print("\n")
    finally:
        conn.close()


if __name__ == "__main__":
    inspect_database()
