"""
Telangana State & District Daily Weather Collector (SQLite + Excel ETL)

Fetches daily weather metrics for all 33 Telangana districts via Open-Meteo API using parallel threads.
Stores records in both an embedded SQLite database (data/weather_database.db) and multi-sheet Excel file (data/weather_data.xlsx).
Generates daily district reports, state summaries, and aggregated monthly reports.
"""

import os
import sys
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
import pandas as pd
import requests

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


def fetch_district_weather(district: Dict[str, Any], date_str: str) -> Dict[str, Any]:
    """Queries Open-Meteo API for a single district's weather metrics."""
    params = {
        "latitude": district["lat"],
        "longitude": district["lon"],
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "auto",
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        current = response.json().get("current", {})
        
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
        print(f"[WARNING] Failed to fetch data for {district['name']}: {err}", file=sys.stderr)
        return None


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
            
    print(f"[SUCCESS] Retrieved {len(district_records)} district observations.", flush=True)
    return district_records


def generate_state_summary(district_records: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
    """Generates an overall Telangana State daily summary report."""
    if not district_records:
        return {}

    df = pd.DataFrame(district_records)
    
    hottest_row = df.loc[df["temperature_C"].idxmax()]
    coolest_row = df.loc[df["temperature_C"].idxmin()]
    rainiest_row = df.loc[df["precipitation_mm"].idxmax()]
    windiest_row = df.loc[df["wind_speed_kmh"].idxmax()]

    summary = {
        "date": date_str,
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
    """Saves daily weather records into SQLite SQL database tables."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
        PRIMARY KEY (date, district)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telangana_state_summary (
        date TEXT PRIMARY KEY,
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
        max_wind_speed_kmh REAL
    )
    """)

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
        (date, state, total_districts_monitored, state_avg_temp_C, hottest_district, max_temp_C,
         coolest_district, min_temp_C, state_avg_humidity_pct, total_state_rainfall_mm, rainiest_district, max_rainfall_mm, windiest_district, max_wind_speed_kmh)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["date"], s["state"], s["total_districts_monitored"], s["state_avg_temp_C"],
            s["hottest_district"], s["max_temp_C"], s["coolest_district"], s["min_temp_C"],
            s["state_avg_humidity_%"], s["total_state_rainfall_mm"], s["rainiest_district"],
            s["max_rainfall_mm"], s["windiest_district"], s["max_wind_speed_kmh"]
        ))

    conn.commit()

    # Generate Monthly District Aggregated Table in SQL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_district_summary AS
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
                existing_dist = existing_dist[existing_dist["date"] != today_str]
                combined_dist = pd.concat([existing_dist, new_dist_df], ignore_index=True)
            else:
                combined_dist = new_dist_df

            if "Telangana_State_Summary" in excel_file.sheet_names:
                existing_sum = pd.read_excel(file_path, sheet_name="Telangana_State_Summary")
                existing_sum = existing_sum[existing_sum["date"] != today_str]
                combined_sum = pd.concat([existing_sum, new_sum_df], ignore_index=True)
            else:
                combined_sum = new_sum_df

        except Exception:
            combined_dist = new_dist_df
            combined_sum = new_sum_df
    else:
        combined_dist = new_dist_df
        combined_sum = new_sum_df

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
    today_str = datetime.now().strftime("%Y-%m-%d")
    district_records = fetch_all_telangana_districts()
    
    if district_records:
        state_summary = generate_state_summary(district_records, today_str)
        dist_df, sum_df = update_excel_reports(district_records, state_summary)
        update_sqlite_database(pd.DataFrame(district_records), pd.DataFrame([state_summary]))
        
        print("\n=== TELANGANA STATE DAILY WEATHER OVERVIEW ===", flush=True)
        print(f"Date: {state_summary['date']}", flush=True)
        print(f"State Avg Temp: {state_summary['state_avg_temp_C']} deg C", flush=True)
        print(f"Hottest District: {state_summary['hottest_district']} ({state_summary['max_temp_C']} deg C)", flush=True)
        print(f"Coolest District: {state_summary['coolest_district']} ({state_summary['min_temp_C']} deg C)", flush=True)
        print(f"State Avg Humidity: {state_summary['state_avg_humidity_%']} %", flush=True)
        print(f"Total State Rain: {state_summary['total_state_rainfall_mm']} mm", flush=True)
        print("===============================================\n", flush=True)


if __name__ == "__main__":
    main()
