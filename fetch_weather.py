import os
from datetime import datetime
import pandas as pd
import requests

CITY_NAME = "Hyderabad"
LATITUDE = 17.3850
LONGITUDE = 78.4867
EXCEL_PATH = "data/weather_data.xlsx"


def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()["current"]

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": data["time"],
        "city": CITY_NAME,
        "temperature_C": data["temperature_2m"],
        "humidity_%": data["relative_humidity_2m"],
        "precipitation_mm": data["precipitation"],
        "wind_speed_kmh": data["wind_speed_10m"],
        "weather_code": data["weather_code"],
    }


def append_to_excel(record):
    os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
    new_row = pd.DataFrame([record])

    if os.path.exists(EXCEL_PATH):
        existing = pd.read_excel(EXCEL_PATH)
        existing = existing[existing["date"] != record["date"]]
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_excel(EXCEL_PATH, index=False)
    print(f"Updated weather data for {record['city']} ({record['date']})")


if __name__ == "__main__":
    record = fetch_weather()
    append_to_excel(record)

