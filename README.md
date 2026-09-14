# Daily Weather Analytics Dashboard

A beginner-friendly, real-world data analyst project: a Python script pulls
live weather data once a day, logs it into a growing Excel dataset, and
Power BI turns that dataset into a live dashboard. Automated with GitHub
Actions so the data updates itself daily — no manual work required.

This is designed to be a strong first portfolio project because it
demonstrates the full analyst toolkit in one place: **Python (automation +
data collection), Excel (data storage), Power BI (visualization), and Git/GitHub
(version control + CI automation)**.

---

## How it works

1. `fetch_weather.py` calls the free [Open-Meteo API](https://open-meteo.com)
   (no API key required) for a chosen city and pulls current temperature,
   humidity, precipitation, and wind speed.
2. It appends that day's reading as a new row to `data/weather_data.xlsx`.
3. A GitHub Actions workflow (`.github/workflows/daily_update.yml`) runs this
   script automatically every day and commits the updated file back to your
   repo — so your dataset keeps growing on its own.
4. Power BI connects to the Excel file (or directly to the raw file on
   GitHub) and refreshes to show up-to-date trends.

---

## Setup

### 1. Create the GitHub repo
- Create a new repo on GitHub (e.g., `daily-weather-analytics`).
- Upload all the files in this folder, keeping the folder structure intact
  (the `.github/workflows` folder must stay exactly as-is for automation to work).

### 2. Run it locally first (optional but recommended)
```bash
pip install -r requirements.txt
python fetch_weather.py
```
This creates `data/weather_data.xlsx` with your first row of data. Run it
again on a different day (or edit the date manually) to simulate a few
days of history before your GitHub Action kicks in.

### 3. Turn on GitHub Actions
- Push your repo to GitHub. The workflow will start running automatically
  on the schedule defined in `daily_update.yml` (9:00 AM IST daily).
- You can also trigger it manually anytime: go to the **Actions** tab →
  select **Daily Weather Data Update** → **Run workflow**.
- Make sure your repo settings allow Actions to push commits: go to
  **Settings → Actions → General → Workflow permissions** and select
  **"Read and write permissions."**

### 4. Connect Power BI
Two ways to do this:

**Option A — Connect to the Excel file directly (simplest):**
- Clone/sync the repo locally, or just re-download `weather_data.xlsx`
  periodically.
- In Power BI Desktop: **Get Data → Excel Workbook** → select `weather_data.xlsx`.

**Option B — Connect to the live file on GitHub (more impressive, no manual download):**
- In Power BI Desktop: **Get Data → Web**.
- Use the "raw" GitHub URL for your file, e.g.:
  `https://raw.githubusercontent.com/<your-username>/daily-weather-analytics/main/data/weather_data.xlsx`
- Set up a scheduled refresh in Power BI (if using Power BI Service) so your
  dashboard updates automatically as new daily data lands in the repo.

### 5. Build the dashboard
Suggested visuals for your first version:
- Line chart: temperature over time
- Line chart: humidity over time
- Bar chart: precipitation by day
- Card visuals: latest temperature, latest humidity
- Optional: a simple 7-day rolling average trend line (great talking point in interviews)

---

## Extending this project (good next steps once it's working)

- Track **multiple cities** and compare them side by side
- Pull in an **air quality index** feed alongside weather
- Add a Python step that calculates **weekly/monthly summary stats**
  (avg temp, rainiest day, etc.) into a second Excel sheet
- Write a short `insights.md` each week summarizing what the data shows —
  this is what recruiters actually want to see: not just charts, but
  interpretation

---

## Why this project works well for a fresher portfolio

- It's **real, live data** — not a static Kaggle CSV everyone has used.
- It shows you can **automate a pipeline**, not just clean data once.
- It touches the **exact toolkit** most junior analyst job posts ask for:
  Excel, SQL-adjacent data wrangling in Python, Power BI, and Git.
- It's easy to talk through in an interview: *"I built a pipeline that pulls
  live weather data daily via GitHub Actions, stores it in Excel, and
  visualizes trends in Power BI"* is a strong, concrete answer to
  "tell me about a project."

---

## Files in this project

```
daily-weather-analytics/
├── fetch_weather.py              # Pulls weather data, appends to Excel
├── requirements.txt              # Python dependencies
├── data/
│   └── weather_data.xlsx         # Generated after first run
├── .github/
│   └── workflows/
│       └── daily_update.yml      # Automates the daily run
└── README.md
```
