"""
Telangana Weather Analytics Multi-Chart Dashboard Generator

Generates high-resolution visualization dashboards featuring a diverse set of chart types:
1. Line Chart with Shaded Area & Average Reference: District Temperatures (°C).
2. Scatter / Bubble Plot: Temperature vs. Humidity (Bubble Size = Wind Speed).
3. Horizontal Bar Chart: Top 10 High Humidity Districts.
4. Metric Card: Statewide Aggregate Statistics.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
    today_df = dist_df[dist_df["date"] == latest_date].sort_values("district")

    # Load State Summary
    if "Telangana_State_Summary" in excel_file.sheet_names:
        state_df = pd.read_excel(EXCEL_PATH, sheet_name="Telangana_State_Summary")
        latest_summary = state_df[state_df["date"] == latest_date].iloc[-1].to_dict()
    else:
        latest_summary = {}

    # Set dark-mode theme
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 12), facecolor="#0f172a")

    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1], hspace=0.35, wspace=0.25)
    
    ax_line = fig.add_subplot(gs[0, :])
    ax_scatter = fig.add_subplot(gs[1, 0])
    ax_card = fig.add_subplot(gs[1, 1])

    for ax in [ax_line, ax_scatter]:
        ax.set_facecolor("#1e293b")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#475569")
        ax.spines["bottom"].set_color("#475569")
        ax.tick_params(colors="#94a3b8")

    # --- 1. Line Chart: Temperature Across 33 Telangana Districts ---
    districts = today_df["district"].values
    temps = today_df["temperature_C"].values
    mean_temp = np.mean(temps)

    ax_line.plot(districts, temps, color="#f59e0b", marker="o", linewidth=2.5, markersize=6, label="District Temp (°C)")
    ax_line.fill_between(districts, temps, mean_temp, where=(temps >= mean_temp), color="#f59e0b", alpha=0.15)
    ax_line.fill_between(districts, temps, mean_temp, where=(temps < mean_temp), color="#3b82f6", alpha=0.15)
    
    ax_line.axhline(mean_temp, color="#ef4444", linestyle="--", linewidth=1.8, label=f"State Avg Temp ({mean_temp:.1f} °C)")
    ax_line.set_title(f"Telangana District Temperature Variations Line Chart — {latest_date}", color="#f8fafc", fontsize=15, pad=12, fontweight="bold")
    ax_line.set_ylabel("Temperature (°C)", color="#94a3b8")
    ax_line.tick_params(axis="x", rotation=75, labelsize=9)
    ax_line.grid(True, linestyle="--", alpha=0.2, color="#94a3b8")
    ax_line.legend(loc="upper right", facecolor="#1e293b", edgecolor="#475569", labelcolor="#f8fafc")

    # --- 2. Scatter / Bubble Plot: Temperature vs Humidity (Bubble Size = Wind Speed) ---
    humidity = today_df["humidity_%"].values
    wind_speeds = today_df["wind_speed_kmh"].values
    bubble_sizes = wind_speeds * 25 + 30  # Scale for visibility

    scatter = ax_scatter.scatter(temps, humidity, s=bubble_sizes, c=temps, cmap="inferno", alpha=0.85, edgecolors="#ffffff", linewidth=0.8)
    ax_scatter.set_title("Scatter Plot: Temperature vs. Humidity (Bubble Size = Wind Speed)", color="#f8fafc", fontsize=13, pad=12, fontweight="bold")
    ax_scatter.set_xlabel("Temperature (°C)", color="#94a3b8")
    ax_scatter.set_ylabel("Humidity (%)", color="#94a3b8")
    ax_scatter.grid(True, linestyle="--", alpha=0.2, color="#94a3b8")
    
    cbar = fig.colorbar(scatter, ax=ax_scatter)
    cbar.ax.set_ylabel("Temp Intensity (°C)", color="#94a3b8")
    cbar.ax.tick_params(colors="#94a3b8")

    # Annotate top extreme points in scatter
    for i, txt in enumerate(districts):
        if temps[i] == np.max(temps) or temps[i] == np.min(temps) or humidity[i] == np.max(humidity):
            ax_scatter.annotate(txt, (temps[i] + 0.1, humidity[i] + 0.5), color="#f8fafc", fontsize=8, fontweight="bold")

    # --- 3. Overall Telangana State Summary Card ---
    ax_card.axis("off")
    
    if latest_summary:
        summary_text = (
            f"TELANGANA STATE OVERALL SUMMARY REPORT\n"
            f"--------------------------------------------------\n\n"
            f"Date: {latest_date}\n"
            f"Total Districts Monitored: {latest_summary.get('total_districts_monitored', 33)}\n\n"
            f"State Avg Temperature: {latest_summary.get('state_avg_temp_C', 'N/A')} °C\n"
            f"Hottest District: {latest_summary.get('hottest_district', 'N/A')} ({latest_summary.get('max_temp_C', 'N/A')} °C)\n"
            f"Coolest District: {latest_summary.get('coolest_district', 'N/A')} ({latest_summary.get('min_temp_C', 'N/A')} °C)\n\n"
            f"State Avg Humidity: {latest_summary.get('state_avg_humidity_%', 'N/A')} %\n"
            f"Total State Rainfall: {latest_summary.get('total_state_rainfall_mm', 'N/A')} mm\n"
            f"Rainiest District: {latest_summary.get('rainiest_district', 'N/A')} ({latest_summary.get('max_rainfall_mm', 'N/A')} mm)\n"
            f"Windiest District: {latest_summary.get('windiest_district', 'N/A')} ({latest_summary.get('max_wind_speed_kmh', 'N/A')} km/h)"
        )
    else:
        summary_text = "State summary data available in weather_data.xlsx"

    ax_card.text(
        0.05, 0.5, summary_text,
        transform=ax_card.transAxes,
        fontsize=12,
        color="#e2e8f0",
        verticalalignment="center",
        bbox=dict(boxstyle="round,pad=1.2", facecolor="#1e293b", edgecolor="#334155", lw=1.5)
    )

    fig.suptitle("Telangana Weather Multi-Chart Analytics Dashboard", color="#f8fafc", fontsize=20, fontweight="bold", y=0.98)
    
    plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches="tight")
    print(f"[SUCCESS] Multi-Chart Dashboard saved to {OUTPUT_IMAGE}")
    plt.close()


if __name__ == "__main__":
    generate_telangana_visualizations()
