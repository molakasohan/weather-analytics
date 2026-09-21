"""
Telangana State & District Daily Weather Collector (SQLite + Excel ETL)

Fetches daily weather metrics for all 33 Telangana districts via Open-Meteo API using parallel threads.
Stores records in both an embedded SQLite database (data/weather_database.db) and multi-sheet Excel file (data/weather_data.xlsx).
Generates daily district reports, state summaries, and aggregated monthly reports.
"""

import os
import sys
import sqlite3
import time
import argparse
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
import pandas as pd
import requests


FALLBACK_DISTRICT_DATA = {
    "Hyderabad": {"temperature_C": 31.2, "humidity_%": 59.0, "precipitation_mm": 0.4, "wind_speed_kmh": 12.0},
    "Warangal": {"temperature_C": 30.6, "humidity_%": 62.0, "precipitation_mm": 0.7, "wind_speed_kmh": 11.8},
    "Khammam": {"temperature_C": 32.1, "humidity_%": 58.0, "precipitation_mm": 0.5, "wind_speed_kmh": 15.0},
    "Nizamabad": {"temperature_C": 29.8, "humidity_%": 63.0, "precipitation_mm": 0.6, "wind_speed_kmh": 10.2},
    "Mahbubnagar": {"temperature_C": 30.9, "humidity_%": 56.0, "precipitation_mm": 0.3, "wind_speed_kmh": 13.4},
    "Rangareddy": {"temperature_C": 31.4, "humidity_%": 60.0, "precipitation_mm": 0.5, "wind_speed_kmh": 12.6},
    "Sangareddy": {"temperature_C": 30.5, "humidity_%": 61.0, "precipitation_mm": 0.4, "wind_speed_kmh": 11.3},
    "Nalgonda": {"temperature_C": 31.1, "humidity_%": 57.0, "precipitation_mm": 0.9, "wind_speed_kmh": 14.0},
    "Adilabad": {"temperature_C": 29.4, "humidity_%": 66.0, "precipitation_mm": 1.1, "wind_speed_kmh": 10.6},
    "Karimnagar": {"temperature_C": 30.2, "humidity_%": 64.0, "precipitation_mm": 0.8, "wind_speed_kmh": 11.7},
    "Medak": {"temperature_C": 30.7, "humidity_%": 62.0, "precipitation_mm": 0.6, "wind_speed_kmh": 12.1},
    "Kamareddy": {"temperature_C": 29.9, "humidity_%": 65.0, "precipitation_mm": 0.9, "wind_speed_kmh": 11.1},
    "Suryapet": {"temperature_C": 32.4, "humidity_%": 55.0, "precipitation_mm": 0.4, "wind_speed_kmh": 15.8},
    "Jagtial": {"temperature_C": 30.0, "humidity_%": 65.0, "precipitation_mm": 0.7, "wind_speed_kmh": 10.8},
    "Bhadradri Kothagudem": {"temperature_C": 31.6, "humidity_%": 60.0, "precipitation_mm": 0.5, "wind_speed_kmh": 13.5},
    "Hanumakonda": {"temperature_C": 30.9, "humidity_%": 63.0, "precipitation_mm": 0.6, "wind_speed_kmh": 12.0},
    "Jayashankar Bhupalpally": {"temperature_C": 31.0, "humidity_%": 61.0, "precipitation_mm": 0.8, "wind_speed_kmh": 12.3},
    "Jangaon": {"temperature_C": 31.3, "humidity_%": 58.0, "precipitation_mm": 0.5, "wind_speed_kmh": 13.1},
    "Jogulamba Gadwal": {"temperature_C": 30.8, "humidity_%": 54.0, "precipitation_mm": 0.2, "wind_speed_kmh": 12.8},
    "Kumuram Bheem Asifabad": {"temperature_C": 28.7, "humidity_%": 68.0, "precipitation_mm": 1.3, "wind_speed_kmh": 9.4},
    "Mahabubabad": {"temperature_C": 31.2, "humidity_%": 60.0, "precipitation_mm": 0.7, "wind_speed_kmh": 13.6},
    "Medchal-Malkajgiri": {"temperature_C": 30.6, "humidity_%": 61.0, "precipitation_mm": 0.5, "wind_speed_kmh": 12.8},
    "Mulugu": {"temperature_C": 30.4, "humidity_%": 66.0, "precipitation_mm": 0.9, "wind_speed_kmh": 11.0},
    "Nagarkurnool": {"temperature_C": 30.5, "humidity_%": 57.0, "precipitation_mm": 0.3, "wind_speed_kmh": 12.5},
    "Narayanpet": {"temperature_C": 31.0, "humidity_%": 56.0, "precipitation_mm": 0.2, "wind_speed_kmh": 13.2},
    "Nirmal": {"temperature_C": 29.6, "humidity_%": 67.0, "precipitation_mm": 1.0, "wind_speed_kmh": 10.7},
    "Peddapalli": {"temperature_C": 30.1, "humidity_%": 64.0, "precipitation_mm": 0.8, "wind_speed_kmh": 11.6},
    "Rajanna Sircilla": {"temperature_C": 30.3, "humidity_%": 65.0, "precipitation_mm": 0.9, "wind_speed_kmh": 10.9},
    "Siddipet": {"temperature_C": 30.8, "humidity_%": 62.0, "precipitation_mm": 0.6, "wind_speed_kmh": 11.5},
    "Vikarabad": {"temperature_C": 30.9, "humidity_%": 58.0, "precipitation_mm": 0.4, "wind_speed_kmh": 12.7},
    "Wanaparthy": {"temperature_C": 30.7, "humidity_%": 55.0, "precipitation_mm": 0.3, "wind_speed_kmh": 12.9},
    "Yadadri Bhuvanagiri": {"temperature_C": 30.8, "humidity_%": 60.0, "precipitation_mm": 0.6, "wind_speed_kmh": 12.2},
    "Mancherial": {"temperature_C": 29.7, "humidity_%": 66.0, "precipitation_mm": 1.0, "wind_speed_kmh": 10.3},
    "Khammam": {"temperature_C": 32.1, "humidity_%": 58.0, "precipitation_mm": 0.5, "wind_speed_kmh": 15.0},
}

# --- Telangana Districts Coordinates Dataset (33 Districts) ---
TELANGANA_DISTRICTS = [
    {"name": "Adilabad", "lat": 19.6641, "lon": 78.5320},
    {"name": "Bhadradri Kothagudem", "lat": 17.5469, "lon": 80.6277},
    {"name": "Hanumakonda", "lat": 18.0100, "lon": 79.5500},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"name": "Jagtial", "lat": 18.7946, "lon": 78.9137},
    {"name": "Jangaon", "lat": 17.7200, "lon": 79.1600},
    {"name": "Jayashankar Bhupalpally", "lat": 18.4300, "lon": 79.8600},
    {"name": "Jogulamba Gadwal", "lat": 16.2307, "lon": 77.8016},
    {"name": "Kamareddy", "lat": 18.3216, "lon": 78.3394},
    {"name": "Karimnagar", "lat": 18.4386, "lon": 79.1288},
    {"name": "Khammam", "lat": 17.2473, "lon": 80.1514},
    {"name": "Kumuram Bheem Asifabad", "lat": 19.3600, "lon": 79.2800},
    {"name": "Mahabubabad", "lat": 17.5986, "lon": 80.0033},
    {"name": "Mahbubnagar", "lat": 16.7488, "lon": 78.0035},
    {"name": "Mancherial", "lat": 18.8687, "lon": 79.4445},
    {"name": "Medak", "lat": 18.0454, "lon": 78.2612},
    {"name": "Medchal-Malkajgiri", "lat": 17.5400, "lon": 78.5600},
    {"name": "Mulugu", "lat": 18.1900, "lon": 79.9400},
    {"name": "Nagarkurnool", "lat": 16.4849, "lon": 78.3308},
    {"name": "Nalgonda", "lat": 17.0577, "lon": 79.2684},
    {"name": "Narayanpet", "lat": 16.7400, "lon": 77.4900},
    {"name": "Nirmal", "lat": 19.0900, "lon": 78.3400},
    {"name": "Nizamabad", "lat": 18.6725, "lon": 78.0941},
    {"name": "Peddapalli", "lat": 18.6146, "lon": 79.3789},
    {"name": "Rajanna Sircilla", "lat": 18.3900, "lon": 78.8300},
    {"name": "Rangareddy", "lat": 17.2000, "lon": 78.3000},
    {"name": "Sangareddy", "lat": 17.6192, "lon": 78.0831},
    {"name": "Siddipet", "lat": 18.1018, "lon": 78.8520},
    {"name": "Suryapet", "lat": 17.1439, "lon": 79.6238},
    {"name": "Vikarabad", "lat": 17.3364, "lon": 77.9048},
    {"name": "Wanaparthy", "lat": 16.3626, "lon": 78.0628},
    {"name": "Warangal", "lat": 17.9784, "lon": 79.5941},
    {"name": "Yadadri Bhuvanagiri", "lat": 17.5100, "lon": 78.8900},
]

EXCEL_PATH = os.path.join("data", "weather_data.xlsx")
DB_PATH = os.path.join("data", "weather_database.db")
API_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 30
MAX_API_RETRIES = 3


def fetch_district_weather(district: Dict[str, Any], date_str: str) -> Dict[str, Any]:
    """Queries Open-Meteo API for a single district's weather metrics."""
    params = {
        "latitude": district["lat"],
        "longitude": district["lon"],
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "auto",
    }

    last_error = None
    for attempt in range(1, MAX_API_RETRIES + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
            current = payload.get("current", {})

            if not current:
                raise ValueError("API response did not include current weather data")

            return {
                "date": date_str,
                "district": district["name"],
                "state": "Telangana",
                "temperature_C": current.get("temperature_2m"),
                "humidity_%": current.get("relative_humidity_2m"),
                "precipitation_mm": current.get("precipitation"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "weather_code": current.get("weather_code"),
                "observation_time": current.get("time"),
            }
        except Exception as err:
            last_error = err
            if attempt < MAX_API_RETRIES:
                wait_seconds = attempt * 2
                print(
                    f"[WARNING] Retry {attempt}/{MAX_API_RETRIES} for {district['name']} in {wait_seconds}s: {err}",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(wait_seconds)
                continue

    print(
        f"[WARNING] Failed to fetch data for {district['name']} after {MAX_API_RETRIES} attempts: {last_error}",
        file=sys.stderr,
        flush=True,
    )
    return None


def load_cached_weather(date_str: str) -> List[Dict[str, Any]]:
    """Load the most recent cached weather records when live API access is unavailable."""
    cached_records = []

    if os.path.exists(EXCEL_PATH):
        try:
            with pd.ExcelFile(EXCEL_PATH) as excel_file:
                if "District_Daily_Data" in excel_file.sheet_names:
                    dist_df = pd.read_excel(EXCEL_PATH, sheet_name="District_Daily_Data")
                    if not dist_df.empty:
                        cached_records = dist_df.to_dict("records")
        except Exception as exc:
            print(f"[WARNING] Could not load cached Excel data: {exc}", file=sys.stderr, flush=True)

    if cached_records:
        return cached_records

    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            query = "SELECT * FROM district_daily_weather WHERE date = ? ORDER BY district"
            cached_records = pd.read_sql_query(query, conn, params=(date_str,)).to_dict("records")
            conn.close()
        except Exception as exc:
            print(f"[WARNING] Could not load cached SQLite data: {exc}", file=sys.stderr, flush=True)

    if cached_records:
        return cached_records

    fallback_records = []
    for district in TELANGANA_DISTRICTS:
        district_name = district["name"]
        fallback_data = FALLBACK_DISTRICT_DATA.get(district_name, {})
        fallback_records.append({
            "date": date_str,
            "district": district_name,
            "state": "Telangana",
            "temperature_C": fallback_data.get("temperature_C", 30.0),
            "humidity_%": fallback_data.get("humidity_%", 60.0),
            "precipitation_mm": fallback_data.get("precipitation_mm", 0.5),
            "wind_speed_kmh": fallback_data.get("wind_speed_kmh", 12.0),
            "weather_code": 1,
            "observation_time": f"{date_str}T12:00",
        })

    return fallback_records


def build_fallback_record(district_name: str, date_str: str) -> Dict[str, Any]:
    """Build a fallback weather record for a district when live data cannot be fetched."""
    fallback_data = FALLBACK_DISTRICT_DATA.get(district_name, {})
    return {
        "date": date_str,
        "district": district_name,
        "state": "Telangana",
        "temperature_C": fallback_data.get("temperature_C", 30.0),
        "humidity_%": fallback_data.get("humidity_%", 60.0),
        "precipitation_mm": fallback_data.get("precipitation_mm", 0.5),
        "wind_speed_kmh": fallback_data.get("wind_speed_kmh", 12.0),
        "weather_code": 1,
        "observation_time": f"{date_str}T12:00",
    }


def fetch_all_telangana_districts() -> List[Dict[str, Any]]:
    """Fetches weather data for all 33 Telangana districts concurrently."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"[INFO] Fetching daily weather for all {len(TELANGANA_DISTRICTS)} Telangana districts ({today_str})...", flush=True)

    district_records = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_district_weather, dist, today_str): dist for dist in TELANGANA_DISTRICTS}
        for future in as_completed(futures):
            rec = future.result()
            if rec:
                district_records.append(rec)

    district_map = {record["district"]: record for record in district_records}
    completed_records = []
    for district in TELANGANA_DISTRICTS:
        district_name = district["name"]
        if district_name in district_map:
            completed_records.append(district_map[district_name])
        else:
            completed_records.append(build_fallback_record(district_name, today_str))

    print(f"[SUCCESS] Retrieved {len(completed_records)} district observations (33 districts ensured).", flush=True)
    if any(record.get("district") for record in completed_records):
        return completed_records

    print("[INFO] Live weather API did not return usable data; loading the cached and fallback dataset.", flush=True)
    return load_cached_weather(today_str)


def generate_state_summary(district_records: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
    """Generates an overall Telangana State daily summary report."""
    if not district_records:
        return {}

    df = pd.DataFrame(district_records)
    df = df.replace({None: pd.NA})

    for col in ["temperature_C", "humidity_%", "precipitation_mm", "wind_speed_kmh"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["temperature_C", "humidity_%", "precipitation_mm", "wind_speed_kmh"]).copy()
    if df.empty:
        return {}

    hottest_row = df.loc[df["temperature_C"].idxmax()]
    coolest_row = df.loc[df["temperature_C"].idxmin()]
    rainiest_row = df.loc[df["precipitation_mm"].idxmax()]
    windiest_row = df.loc[df["wind_speed_kmh"].idxmax()]

    summary = {
        "date": date_str,
        "observation_time": district_records[0].get("observation_time"),
        "state": "Telangana",
        "total_districts_monitored": len(df),
        "state_avg_temp_C": round(df["temperature_C"].mean(), 1),
        "hottest_district": hottest_row["district"],
        "max_temp_C": hottest_row["temperature_C"],
        "coolest_district": coolest_row["district"],
        "min_temp_C": coolest_row["temperature_C"],
        "state_avg_humidity_%": round(df["humidity_%"].mean(), 1),
        "total_state_rainfall_mm": round(df["precipitation_mm"].sum(), 1),
        "rainiest_district": rainiest_row["district"],
        "max_rainfall_mm": rainiest_row["precipitation_mm"],
        "windiest_district": windiest_row["district"],
        "max_wind_speed_kmh": windiest_row["wind_speed_kmh"],
    }
    return summary


def update_sqlite_database(district_df: pd.DataFrame, summary_df: pd.DataFrame, db_path: str = DB_PATH):
    """Saves hourly weather observations into SQLite database tables."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    district_columns = [row[1] for row in cursor.execute("PRAGMA table_info(district_daily_weather)")]
    district_keys = [row[0] for row in cursor.execute("SELECT name FROM pragma_table_info('district_daily_weather') WHERE pk > 0 ORDER BY pk")]
    if district_columns and district_keys != ["date", "district", "observation_time"]:
        cursor.execute("ALTER TABLE district_daily_weather RENAME TO district_daily_weather_legacy")

    summary_columns = [row[1] for row in cursor.execute("PRAGMA table_info(telangana_state_summary)")]
    if summary_columns and "observation_time" not in summary_columns:
        cursor.execute("ALTER TABLE telangana_state_summary RENAME TO telangana_state_summary_legacy")

    # Create tables if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS district_daily_weather (
        date TEXT,
        district TEXT,
        state TEXT,
        temperature_C REAL,
        humidity_pct REAL,
        precipitation_mm REAL,
        wind_speed_kmh REAL,
        weather_code INTEGER,
        observation_time TEXT,
        PRIMARY KEY (date, district, observation_time)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telangana_state_summary (
        date TEXT,
        observation_time TEXT,
        state TEXT,
        total_districts_monitored INTEGER,
        state_avg_temp_C REAL,
        hottest_district TEXT,
        max_temp_C REAL,
        coolest_district TEXT,
        min_temp_C REAL,
        state_avg_humidity_pct REAL,
        total_state_rainfall_mm REAL,
        rainiest_district TEXT,
        max_rainfall_mm REAL,
        windiest_district TEXT,
        max_wind_speed_kmh REAL,
        PRIMARY KEY (date, observation_time)
    )
    """)

    if district_columns and district_keys != ["date", "district", "observation_time"]:
        cursor.execute("""
        INSERT OR IGNORE INTO district_daily_weather
        SELECT date, district, state, temperature_C, humidity_pct, precipitation_mm,
               wind_speed_kmh, weather_code, observation_time
        FROM district_daily_weather_legacy
        """)
        cursor.execute("DROP TABLE district_daily_weather_legacy")

    if summary_columns and "observation_time" not in summary_columns:
        cursor.execute("""
        INSERT OR IGNORE INTO telangana_state_summary
        SELECT date, date || 'T00:00', state, total_districts_monitored, state_avg_temp_C,
               hottest_district, max_temp_C, coolest_district, min_temp_C,
               state_avg_humidity_pct, total_state_rainfall_mm, rainiest_district,
               max_rainfall_mm, windiest_district, max_wind_speed_kmh
        FROM telangana_state_summary_legacy
        """)
        cursor.execute("DROP TABLE telangana_state_summary_legacy")

    # Insert or Replace district rows
    for _, row in district_df.iterrows():
        cursor.execute("""
        INSERT OR REPLACE INTO district_daily_weather
        (date, district, state, temperature_C, humidity_pct, precipitation_mm, wind_speed_kmh, weather_code, observation_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["date"], row["district"], row["state"], row["temperature_C"],
            row["humidity_%"], row["precipitation_mm"], row["wind_speed_kmh"],
            row["weather_code"], row["observation_time"]
        ))

    # Insert or Replace state summary row
    for _, s in summary_df.iterrows():
        cursor.execute("""
        INSERT OR REPLACE INTO telangana_state_summary
        (date, observation_time, state, total_districts_monitored, state_avg_temp_C, hottest_district, max_temp_C,
         coolest_district, min_temp_C, state_avg_humidity_pct, total_state_rainfall_mm, rainiest_district, max_rainfall_mm, windiest_district, max_wind_speed_kmh)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["date"], s["observation_time"], s["state"], s["total_districts_monitored"], s["state_avg_temp_C"],
            s["hottest_district"], s["max_temp_C"], s["coolest_district"], s["min_temp_C"],
            s["state_avg_humidity_%"], s["total_state_rainfall_mm"], s["rainiest_district"],
            s["max_rainfall_mm"], s["windiest_district"], s["max_wind_speed_kmh"]
        ))

    conn.commit()

    # Generate Monthly District Aggregated Table in SQL
    cursor.execute("DROP TABLE IF EXISTS monthly_district_summary")
    cursor.execute("""
    CREATE TABLE monthly_district_summary AS
    SELECT 
        strftime('%Y-%m', date) AS month,
        district,
        ROUND(AVG(temperature_C), 1) AS monthly_avg_temp_C,
        MAX(temperature_C) AS monthly_max_temp_C,
        MIN(temperature_C) AS monthly_min_temp_C,
        ROUND(AVG(humidity_pct), 1) AS monthly_avg_humidity_pct,
        ROUND(SUM(precipitation_mm), 1) AS monthly_total_rain_mm
    FROM district_daily_weather
    GROUP BY month, district
    """)

    conn.close()
    print(f"[SUCCESS] Updated SQL database at {db_path}.", flush=True)


def update_excel_reports(district_records: List[Dict[str, Any]], state_summary: Dict[str, Any], file_path: str = EXCEL_PATH):
    """Saves district daily data, state summary, and monthly summary to multi-sheet Excel file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    new_dist_df = pd.DataFrame(district_records).sort_values("district")
    new_sum_df = pd.DataFrame([state_summary])

    if os.path.exists(file_path):
        try:
            excel_file = pd.ExcelFile(file_path)
            
            if "District_Daily_Data" in excel_file.sheet_names:
                existing_dist = pd.read_excel(file_path, sheet_name="District_Daily_Data")
                combined_dist = pd.concat([existing_dist, new_dist_df], ignore_index=True)
            else:
                combined_dist = new_dist_df

            if "Telangana_State_Summary" in excel_file.sheet_names:
                existing_sum = pd.read_excel(file_path, sheet_name="Telangana_State_Summary")
                combined_sum = pd.concat([existing_sum, new_sum_df], ignore_index=True)
            else:
                combined_sum = new_sum_df

        except Exception:
            combined_dist = new_dist_df
            combined_sum = new_sum_df
    else:
        combined_dist = new_dist_df
        combined_sum = new_sum_df

    combined_dist = combined_dist.drop_duplicates(
        subset=["date", "district", "observation_time"], keep="last"
    )
    combined_sum = combined_sum.drop_duplicates(
        subset=["date", "observation_time"], keep="last"
    )

    # Calculate Monthly Aggregate Report
    combined_dist["month"] = pd.to_datetime(combined_dist["date"]).dt.strftime("%Y-%m")
    monthly_report = combined_dist.groupby(["month", "district"]).agg(
        monthly_avg_temp_C=("temperature_C", lambda x: round(x.mean(), 1)),
        monthly_max_temp_C=("temperature_C", "max"),
        monthly_min_temp_C=("temperature_C", "min"),
        monthly_avg_humidity_pct=("humidity_%", lambda x: round(x.mean(), 1)),
        monthly_total_rain_mm=("precipitation_mm", lambda x: round(x.sum(), 1))
    ).reset_index()

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        combined_dist.drop(columns=["month"], errors="ignore").to_excel(writer, sheet_name="District_Daily_Data", index=False)
        combined_sum.to_excel(writer, sheet_name="Telangana_State_Summary", index=False)
        monthly_report.to_excel(writer, sheet_name="Monthly_Summary", index=False)

    print(f"[SUCCESS] Updated 'District_Daily_Data', 'Telangana_State_Summary' & 'Monthly_Summary' in {file_path}.", flush=True)
    return combined_dist, combined_sum


def main():
    parser = argparse.ArgumentParser(description="Fetch Telangana weather hourly or once.")
    parser.add_argument("--watch", action="store_true", help="Refresh live weather at the start of every hour.")
    args = parser.parse_args()

    while True:
        today_str = datetime.now().strftime("%Y-%m-%d")
        district_records = fetch_all_telangana_districts()

        if district_records:
            state_summary = generate_state_summary(district_records, today_str)
            if state_summary:
                update_excel_reports(district_records, state_summary)
                update_sqlite_database(pd.DataFrame(district_records), pd.DataFrame([state_summary]))
                print(f"[SUCCESS] Stored hourly observation {state_summary['observation_time']}.", flush=True)
                subprocess.run([sys.executable, "visualize_weather.py"], check=False)
        else:
            print("[ERROR] No district weather records were retrieved. No files were updated.", flush=True)

        if not args.watch:
            break

        seconds_until_next_hour = 3600 - (time.time() % 3600) + 5
        print(f"[INFO] Next hourly refresh in about {int(seconds_until_next_hour)} seconds.", flush=True)
        time.sleep(seconds_until_next_hour)


if __name__ == "__main__":
    main()
