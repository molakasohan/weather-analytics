"""
Daily Weather Data Collector

Fetches daily current weather statistics for a target city using the Open-Meteo API 
and logs the record into an Excel dataset for downstream analytics and dashboarding.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import requests

# --- Configuration Settings ---
CITY_NAME = "Hyderabad"
LATITUDE = 17.3850
LONGITUDE = 78.4867
EXCEL_PATH = os.path.join("data", "weather_data.xlsx")
API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather_data() -> Dict[str, Any]:
    """
    Queries the Open-Meteo API for real-time weather metrics.

    Returns:
        Dict[str, Any]: Structured dictionary containing daily weather observation metrics.
    """
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "auto",
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        current_data = payload.get("current", {})
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        record = {
            "date": today_str,
            "time": current_data.get("time"),
            "city": CITY_NAME,
            "temperature_C": current_data.get("temperature_2m"),
            "humidity_%": current_data.get("relative_humidity_2m"),
            "precipitation_mm": current_data.get("precipitation"),
            "wind_speed_kmh": current_data.get("wind_speed_10m"),
            "weather_code": current_data.get("weather_code"),
        }
        return record
        
    except requests.RequestException as error:
        print(f"[ERROR] Failed to retrieve weather data: {error}", file=sys.stderr)
        raise SystemExit(1)


def append_to_excel(record: Dict[str, Any], file_path: str = EXCEL_PATH) -> None:
    """
    Appends or updates today's weather observation record in the Excel dataset.

    Args:
        record (Dict[str, Any]): The weather record dictionary to save.
        file_path (str): Path to the Excel dataset file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    new_row = pd.DataFrame([record])

    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        # Avoid duplicate entries for the same date by updating the row if present
        existing_df = existing_df[existing_df["date"] != record["date"]]
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        updated_df = new_row

    updated_df.to_excel(file_path, index=False)
    print(f"[SUCCESS] Updated weather record for {record['city']} on {record['date']}.")


def main():
    print(f"[INFO] Fetching current weather data for {CITY_NAME}...")
    weather_record = fetch_weather_data()
    append_to_excel(weather_record)


if __name__ == "__main__":
    main()
