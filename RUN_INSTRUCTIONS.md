# 🚀 How to Run the Weather Analytics Program

For full step-by-step documentation, see [`PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md).

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 2. Run the Full Program (Fetch Data, Update SQL/Excel & Generate Pictures)

**Run Step-by-Step:**
```bash
python fetch_weather.py
python visualize_weather.py
```

**OR Run in One Command (PowerShell):**
```powershell
python fetch_weather.py; python visualize_weather.py
```

### Automatically refresh every hour
```powershell
python fetch_weather.py --watch
```

---

### 3. Push Updates to Git
```bash
git add .
git commit -m "Update weather dataset, SQL DB, and visualization archives"
git push origin main
```

---

### 📂 Generated Output Files & Archives
- **SQLite Database**: [`data/weather_database.db`](data/weather_database.db)
- **Excel Dataset**: [`data/weather_data.xlsx`](data/weather_data.xlsx)
- **Latest Dashboard Image**: [`data/weather_dashboard.png`](data/weather_dashboard.png)
- **Daily Picture Archive**: [`data/daily_charts/`](data/daily_charts/)
- **Monthly Picture Archive**: [`data/monthly_charts/`](data/monthly_charts/)
