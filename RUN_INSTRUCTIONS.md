# 🚀 Step-by-Step Command Guide to Run the Weather Analytics Program

This guide provides the complete list of step-by-step terminal commands to set up, run, automate, and visualize the entire Weather Analytics program.

---

## 📋 Prerequisites
Make sure **Python 3.9+** and **Git** are installed on your computer.

---

## 🔹 Step 1: Open Terminal & Navigate to Project Directory

```bash
cd "c:\Users\sohan\OneDrive\Desktop\codegnan\project 6"
```

---

## 🔹 Step 2: Install Required Dependencies

```bash
pip install -r requirements.txt
```
*Installs `requests`, `pandas`, `openpyxl`, and `matplotlib`.*

---

## 🔹 Step 3: Run Data Fetch Script (Extract & Store Data)

```bash
python fetch_weather.py
```
**Expected Output:**
```text
[INFO] Fetching current weather data for Hyderabad...
[SUCCESS] Updated weather record for Hyderabad on 2026-09-14.
```
*This fetches live weather from Open-Meteo API and appends/updates `data/weather_data.xlsx`.*

---

## 🔹 Step 4: Run Dashboard Visualization Script

```bash
python visualize_weather.py
```
**Expected Output:**
```text
[SUCCESS] Dashboard visualization saved to data\weather_dashboard.png
```
*Generates the multi-chart dashboard image at `data/weather_dashboard.png`.*

---

## 🔹 Step 5: Single-Line Command to Run Entire Program

If you want to execute both the ETL fetch and visualization in a single line:

### Windows PowerShell:
```powershell
python fetch_weather.py; python visualize_weather.py
```

### Linux / macOS / Git Bash:
```bash
python fetch_weather.py && python visualize_weather.py
```

---

## 🔹 Step 6: Push Changes to GitHub Repository

```bash
git add .
git commit -m "Update weather dataset and visualization dashboard"
git push origin main
```

---

## 🔹 Step 7: Trigger Daily GitHub Actions Automation

1. Go to your repository on GitHub: `https://github.com/<your-username>/weather-analytics`
2. Click on the **Actions** tab at the top.
3. Select **Daily Weather Data Update** from the left workflow menu.
4. Click **Run workflow** → **Run workflow** button to execute on demand.
5. The bot will run `fetch_weather.py` daily at `03:30 UTC` (09:00 AM IST) automatically and commit updated records.

---

## 🔹 Step 8: View Output Files

- **Excel Data File**: [`data/weather_data.xlsx`](file:///c:/Users/sohan/OneDrive/Desktop/codegnan/project%206/data/weather_data.xlsx)
- **Dashboard Chart**: [`data/weather_dashboard.png`](file:///c:/Users/sohan/OneDrive/Desktop/codegnan/project%206/data/weather_dashboard.png)
