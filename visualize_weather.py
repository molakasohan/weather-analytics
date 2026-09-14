"""
Weather Analytics Visualization Script

Generates visual dashboard charts from data/weather_data.xlsx 
to analyze temperature, humidity, precipitation, and wind speed trends.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

EXCEL_PATH = os.path.join("data", "weather_data.xlsx")
OUTPUT_IMAGE = os.path.join("data", "weather_dashboard.png")


def generate_visualizations():
    if not os.path.exists(EXCEL_PATH):
        print(f"[ERROR] Data file {EXCEL_PATH} does not exist.")
        return

    df = pd.read_excel(EXCEL_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Set modern dark-mode aesthetic
    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor="#0f172a")

    # Colors
    accent_blue = "#38bdf8"
    accent_teal = "#2dd4bf"
    accent_amber = "#fbbf24"
    card_bg = "#1e293b"

    for ax in axes.flat:
        ax.set_facecolor(card_bg)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#475569")
        ax.spines["bottom"].set_color("#475569")
        ax.tick_params(colors="#94a3b8")

    # 1. Temperature Trend
    axes[0, 0].plot(df["date"], df["temperature_C"], marker="o", color=accent_amber, linewidth=2.5, markersize=8)
    axes[0, 0].set_title("Temperature Trend (°C)", color="#f8fafc", fontsize=14, pad=12, fontweight="bold")
    axes[0, 0].set_ylabel("°C", color="#94a3b8")
    axes[0, 0].grid(True, linestyle="--", alpha=0.2, color="#94a3b8")
    for i, txt in enumerate(df["temperature_C"]):
        axes[0, 0].annotate(f"{txt}°C", (df["date"].iloc[i], df["temperature_C"].iloc[i] + 0.3),
                            color="#f8fafc", fontweight="bold", ha="center")

    # 2. Humidity Trend
    axes[0, 1].plot(df["date"], df["humidity_%"], marker="s", color=accent_blue, linewidth=2.5, markersize=8)
    axes[0, 1].set_title("Relative Humidity (%)", color="#f8fafc", fontsize=14, pad=12, fontweight="bold")
    axes[0, 1].set_ylabel("%", color="#94a3b8")
    axes[0, 1].grid(True, linestyle="--", alpha=0.2, color="#94a3b8")
    for i, txt in enumerate(df["humidity_%"]):
        axes[0, 1].annotate(f"{txt}%", (df["date"].iloc[i], df["humidity_%"].iloc[i] + 0.5),
                            color="#f8fafc", fontweight="bold", ha="center")

    # 3. Wind Speed
    axes[1, 0].bar(df["date"].dt.strftime("%Y-%m-%d"), df["wind_speed_kmh"], color=accent_teal, width=0.4)
    axes[1, 0].set_title("Wind Speed (km/h)", color="#f8fafc", fontsize=14, pad=12, fontweight="bold")
    axes[1, 0].set_ylabel("km/h", color="#94a3b8")
    axes[1, 0].grid(True, axis="y", linestyle="--", alpha=0.2, color="#94a3b8")
    for i, txt in enumerate(df["wind_speed_kmh"]):
        axes[1, 0].annotate(f"{txt}", (i, txt + 0.2), color="#f8fafc", fontweight="bold", ha="center")

    # 4. Key Metrics Summary Card
    axes[1, 1].axis("off")
    avg_temp = df["temperature_C"].mean()
    avg_hum = df["humidity_%"].mean()
    total_precip = df["precipitation_mm"].sum()
    latest_city = df["city"].iloc[-1]
    latest_date = df["date"].iloc[-1].strftime("%Y-%m-%d")

    summary_text = (
        f"SUMMARY METRICS\n"
        f"-----------------------------------------\n\n"
        f"Location: {latest_city}\n"
        f"Latest Update: {latest_date}\n\n"
        f"Avg Temperature: {avg_temp:.1f} °C\n"
        f"Avg Humidity: {avg_hum:.1f} %\n"
        f"Total Rain: {total_precip:.1f} mm\n"
        f"Total Records: {len(df)} days"
    )

    axes[1, 1].text(
        0.1, 0.5, summary_text,
        transform=axes[1, 1].transAxes,
        fontsize=13,
        color="#e2e8f0",
        verticalalignment="center",
        bbox=dict(boxstyle="round,pad=1", facecolor="#1e293b", edgecolor="#334155", lw=1.5)
    )

    fig.suptitle(f"Weather Analytics Dashboard - {latest_city}", color="#f8fafc", fontsize=18, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches="tight")
    print(f"[SUCCESS] Dashboard visualization saved to {OUTPUT_IMAGE}")
    plt.close()


if __name__ == "__main__":
    generate_visualizations()
