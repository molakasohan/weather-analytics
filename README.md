# Weather Data Collector

Automated Python script that fetches daily weather data via Open-Meteo API and appends it to an Excel dataset (`data/weather_data.xlsx`).

## Features
- Fetches temperature, humidity, precipitation, and wind speed.
- Automatically creates or updates the Excel sheet without duplicating daily entries.
- Automated daily runs using GitHub Actions.

## Usage

### Run locally
```bash
pip install -r requirements.txt
python fetch_weather.py
```
