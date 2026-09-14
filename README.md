# 🌤️ Daily Weather Analytics Dashboard & Automated Data Pipeline

An end-to-end data analytics project featuring an automated Python ETL pipeline that fetches daily weather metrics, stores them in an Excel dataset via GitHub Actions, and visualizes historical weather trends in Power BI.

---

## 📌 Architecture & Features

- **Automated Data Extraction**: Python script (`fetch_weather.py`) queries the live [Open-Meteo API](https://open-meteo.com/) for daily weather metrics (temperature, humidity, precipitation, wind speed).
- **Persistent Data Storage**: Appends daily readings directly into `data/weather_data.xlsx`.
- **CI/CD Automation**: GitHub Actions (`.github/workflows/daily_update.yml`) runs on a daily schedule, auto-committing updated dataset records to the repository.
- **Interactive Visualization**: Connects Power BI Desktop directly to the dataset to build real-time trend dashboards.

---

## 📁 Repository Structure

```text
weather-analytics/
├── .github/
│   └── workflows/
│       └── daily_update.yml      # CI/CD workflow for automated daily execution
├── data/
│   └── weather_data.xlsx         # Primary dataset file updated daily
├── .gitignore                    # Prevents untracked and temporary files from being committed
├── fetch_weather.py              # Core Python ETL script
├── requirements.txt              # Required Python package dependencies
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Weather Extractor
```bash
python fetch_weather.py
```
*Executing this script will create or append to `data/weather_data.xlsx` with today's weather observation.*

---

## ⚙️ GitHub Actions Automation Setup

1. Push this repository to GitHub.
2. In GitHub, navigate to **Settings → Actions → General → Workflow permissions**.
3. Enable **"Read and write permissions"** so GitHub Actions can auto-commit the updated Excel dataset back to your repository.
4. The workflow runs automatically at `03:30 UTC` daily. You can also trigger it manually under the **Actions** tab using **Workflow Dispatch**.

---

## 📊 Power BI Dashboard Integration

- **Direct File Connection**: Connect Power BI to `data/weather_data.xlsx`.
- **GitHub Web Connection**: Use the raw GitHub URL (`https://raw.githubusercontent.com/<username>/<repo>/main/data/weather_data.xlsx`) for dynamic refresh capabilities.

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
