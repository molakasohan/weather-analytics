# 🌾 Telangana State Daily Weather Analytics & Automated Pipeline

An end-to-end data analytics and ETL project monitoring real-time weather metrics across all **33 Telangana districts**. Features automated daily data extraction, dual storage (SQLite Database + Excel), monthly aggregated reporting, multi-chart visualization dashboards, picture archiving, and daily GitHub Actions automation.

---

## 📌 Architecture & Features

- **Multi-District Extraction**: Python script (`fetch_weather.py`) uses parallel threading to pull daily weather metrics (temperature, humidity, rain, wind speed) for all 33 Telangana districts concurrently via the Open-Meteo API.
- **Dual Data Storage**:
  - **SQLite Database (`data/weather_database.db`)**: Stores raw daily metrics (`district_daily_weather`), daily state summaries (`telangana_state_summary`), and auto-generated monthly aggregates (`monthly_district_summary`).
  - **Excel Workbook (`data/weather_data.xlsx`)**: Multi-sheet file containing `District_Daily_Data`, `Telangana_State_Summary`, and `Monthly_Summary`.
- **Advanced Visual Analytics**: Script (`visualize_weather.py`) generates multi-chart dashboards featuring Temperature Line Charts, Temperature vs. Humidity Scatter/Bubble Plots, and State Metric Cards.
- **Automated Picture Archiving**: Saves dated daily charts (`data/daily_charts/`) and monthly report charts (`data/monthly_charts/`).
- **Hourly Automation**: Run `python fetch_weather.py --watch` to fetch live observations at the start of every hour, update the database and Excel workbook, and regenerate the dashboard.

---

## 📁 Repository Structure

```text
weather-analytics/
├── .github/
│   └── workflows/
│       └── daily_update.yml       # CI/CD workflow for automated daily execution
├── data/
│   ├── weather_database.db        # SQLite SQL database storing daily & monthly records
│   ├── weather_data.xlsx          # Multi-sheet Excel workbook (Daily, State, Monthly)
│   ├── weather_dashboard.png      # Latest multi-chart visualization dashboard
│   ├── daily_charts/              # Daily chart picture archive (weather_dashboard_YYYY-MM-DD.png)
│   └── monthly_charts/            # Monthly chart picture archive (monthly_dashboard_YYYY-MM.png)
├── .gitignore                     # Prevents untracked and temporary files from being committed
├── fetch_weather.py               # Core Python ETL script (33 Districts + SQLite + Excel)
├── visualize_weather.py           # Multi-chart dashboard generator & image archiver
├── query_db.py                    # Database query & inspection helper script
├── requirements.txt               # Required Python package dependencies
├── RUN_INSTRUCTIONS.md            # Quick execution guide
└── README.md                      # Project documentation
```

---

## 🚀 Quick Start & Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
```powershell
python fetch_weather.py; python visualize_weather.py
```

### Keep the dashboard updated every hour
```powershell
python fetch_weather.py --watch
```

---

## ⚙️ GitHub Actions Automation Setup

1. Push this repository to GitHub.
2. Under **Settings → Actions → General → Workflow permissions**, enable **"Read and write permissions"**.
3. The workflow triggers daily at `03:30 UTC` (09:00 AM IST) automatically or manually under the **Actions** tab using **Workflow Dispatch**.

---

## 📊 Power BI & SQL Integration

- **Power BI / Excel**: Connect directly to `data/weather_data.xlsx`.
- **SQL Analytics**: Connect any SQL viewer/Python script to `data/weather_database.db`.

---

