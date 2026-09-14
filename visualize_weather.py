"""
Telangana Weather Analytics Dashboard Generator

Generates high-resolution visualization dashboards analyzing:
1. Individual Telangana District Temperature & Humidity comparisons.
2. Statewide Overall Weather Summary & Extreme Weather Leaders.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

EXCEL_PATH = os.path.join("data", "weather_data.xlsx")
OUTPUT_IMAGE = os.path.join("data", "weather_dashboard.png")


def generate_telangana_visualizations():
    if not os.path.exists(EXCEL_PATH):
        print(f"[ERROR] Data file {EXCEL_PATH} does not exist.")
        return

    excel_file = pd.ExcelFile(EXCEL_PATH)
    
    # Load District Data
    if "District_Daily_Data" in excel_file.sheet_names:
        dist_df = pd.read_excel(EXCEL_PATH, sheet_name="District_Daily_Data")
    else:
        dist_df = pd.read_excel(EXCEL_PATH)

    # Filter latest date records
    latest_date = dist_df["date"].max()
    today_df = dist_df[dist_df["date"] == latest_date].sort_values("temperature_C", ascending=False)

    # Load State Summary
    if "Telangana_State_Summary" in excel_file.sheet_names:
        state_df = pd.read_excel(EXCEL_PATH, sheet_name="Telangana_State_Summary")
        latest_summary = state_df[state_df["date"] == latest_date].iloc[-1].to_dict()
    else:
        latest_summary = {}

    # Set dark-mode theme
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 12), facecolor="#0f172a")

    # Grid layout: Top Bar Chart (District Temps), Bottom Left (Humidity), Bottom Right (State Summary)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1], hspace=0.35, wspace=0.25)
    
    ax_temp = fig.add_subplot(gs[0, :])
    ax_hum = fig.add_subplot(gs[1, 0])
    ax_card = fig.add_subplot(gs[1, 1])

    for ax in [ax_temp, ax_hum]:
        ax.set_facecolor("#1e293b")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#475569")
        ax.spines["bottom"].set_color("#475569")
        ax.tick_params(colors="#94a3b8")

    # 1. District Temperature Ranking Bar Chart
    bars = ax_temp.bar(today_df["district"], today_df["temperature_C"], color="#f59e0b", edgecolor="#b45309", width=0.6)
    ax_temp.set_title(f"Telangana Districts Temperature Comparison (°C) — {latest_date}", color="#f8fafc", fontsize=15, pad=12, fontweight="bold")
    ax_temp.set_ylabel("Temperature (°C)", color="#94a3b8")
    ax_temp.tick_params(axis="x", rotation=75, labelsize=9)
    ax_temp.grid(True, axis="y", linestyle="--", alpha=0.2, color="#94a3b8")
    
    # Highlight hottest and coolest bar
    if len(bars) > 0:
        bars[0].set_color("#ef4444")  # Hottest (red)
        bars[-1].set_color("#3b82f6") # Coolest (blue)

    for bar in bars:
        height = bar.get_height()
        ax_temp.annotate(f"{height:.1f}", (bar.get_x() + bar.get_width() / 2, height + 0.2),
                         color="#f8fafc", fontsize=8, fontweight="bold", ha="center")

    # 2. District Humidity Chart
    hum_df = today_df.sort_values("humidity_%", ascending=False)
    ax_hum.bar(hum_df["district"].head(10), hum_df["humidity_%"].head(10), color="#38bdf8", width=0.5)
    ax_hum.set_title("Top 10 High Humidity Districts (%)", color="#f8fafc", fontsize=13, pad=12, fontweight="bold")
    ax_hum.set_ylabel("Humidity (%)", color="#94a3b8")
    ax_hum.tick_params(axis="x", rotation=45, labelsize=9)
    ax_hum.grid(True, axis="y", linestyle="--", alpha=0.2, color="#94a3b8")

    # 3. Overall Telangana State Summary Card
    ax_card.axis("off")
    
    if latest_summary:
        summary_text = (
            f"TELANGANA STATE OVERALL SUMMARY\n"
            f"--------------------------------------------------\n\n"
            f"Date: {latest_date}\n"
            f"Districts Monitored: {latest_summary.get('total_districts_monitored', 33)}\n\n"
            f"State Avg Temperature: {latest_summary.get('state_avg_temp_C', 'N/A')} °C\n"
            f"Hottest District: {latest_summary.get('hottest_district', 'N/A')} ({latest_summary.get('max_temp_C', 'N/A')} °C)\n"
            f"Coolest District: {latest_summary.get('coolest_district', 'N/A')} ({latest_summary.get('min_temp_C', 'N/A')} °C)\n\n"
            f"State Avg Humidity: {latest_summary.get('state_avg_humidity_%', 'N/A')} %\n"
            f"Total State Rainfall: {latest_summary.get('total_state_rainfall_mm', 'N/A')} mm\n"
            f"Rainiest District: {latest_summary.get('rainiest_district', 'N/A')} ({latest_summary.get('max_rainfall_mm', 'N/A')} mm)\n"
            f"Windiest District: {latest_summary.get('windiest_district', 'N/A')} ({latest_summary.get('max_wind_speed_kmh', 'N/A')} km/h)"
        )
    else:
        summary_text = f"State summary data available in weather_data.xlsx"

    ax_card.text(
        0.05, 0.5, summary_text,
        transform=ax_card.transAxes,
        fontsize=12,
        color="#e2e8f0",
        verticalalignment="center",
        bbox=dict(boxstyle="round,pad=1.2", facecolor="#1e293b", edgecolor="#334155", lw=1.5)
    )

    fig.suptitle("Telangana Daily Weather Analytics Dashboard", color="#f8fafc", fontsize=20, fontweight="bold", y=0.98)
    
    plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches="tight")
    print(f"[SUCCESS] Telangana Dashboard visualization saved to {OUTPUT_IMAGE}")
    plt.close()


if __name__ == "__main__":
    generate_telangana_visualizations()
