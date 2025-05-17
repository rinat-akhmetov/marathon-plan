import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# from ace_tools import display_dataframe_to_user

# Load data
df = pd.read_csv("/Users/arrtz3/code/marathon-plan/consolidated_activity_data.csv")
df["time"] = pd.to_datetime(df["time"], errors="coerce")

# Identify running activities
running_df = df[df["activity_type"] == "running"].copy()


# —— Build per‑run summaries —————————————————————————————————————
def haversine(lat1, lon1, lat2, lon2, *, R=6371):
    """Vectorised haversine distance (km)."""
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


runs_summary = []
for run_id, g in running_df.groupby("run"):
    g = g.sort_values("time")
    # Distance
    lat, lon = g["lat"].values, g["lon"].values
    valid = ~(np.isnan(lat) | np.isnan(lon))
    dist_km = (haversine(lat[:-1][valid[:-1]], lon[:-1][valid[:-1]], lat[1:][valid[1:]], lon[1:][valid[1:]])).sum()
    # Duration
    duration_sec = (g["time"].max() - g["time"].min()).total_seconds()
    # Heart‑rate
    avg_hr = g["hr"].mean()
    # Aerobic % (<150 bpm)
    if g["hr"].count() > 0:
        aerobic_pct = (g["hr"] < 150).sum() / g["hr"].count() * 100
    else:
        aerobic_pct = np.nan
    runs_summary.append(
        {
            "run_id": run_id,
            "date": g["time"].min().date(),
            "distance_km": dist_km,
            "duration_sec": duration_sec,
            "pace_sec_per_km": duration_sec / dist_km if dist_km else np.nan,
            "avg_hr": avg_hr,
            "aerobic_pct": aerobic_pct,
        }
    )

runs = pd.DataFrame(runs_summary)
runs["pace_min_km"] = runs["pace_sec_per_km"] / 60

# —— Key metrics ———————————————————————————————————————————————
total_distance = runs["distance_km"].sum()
total_duration_h = runs["duration_sec"].sum() / 3600
overall_pace_sec = runs["duration_sec"].sum() / total_distance
avg_pace_per_run_sec = runs["pace_sec_per_km"].mean()

marathons = runs[runs["distance_km"] >= 42.195]
avg_marathon_pace_sec = marathons["pace_sec_per_km"].mean() if not marathons.empty else np.nan

metrics = pd.DataFrame(
    {
        "Metric": [
            "Total runs",
            "Total distance (km)",
            "Total duration (h)",
            "Overall average pace (min/km)",
            "Avg. pace per run (min/km)",
            "Marathons completed",
            "Avg. marathon pace (min/km)",
        ],
        "Value": [
            len(runs),
            round(total_distance, 1),
            round(total_duration_h, 2),
            round(overall_pace_sec / 60, 2),
            round(avg_pace_per_run_sec / 60, 2),
            len(marathons),
            round(avg_marathon_pace_sec / 60, 2) if not np.isnan(avg_marathon_pace_sec) else "—",
        ],
    }
)

# —— Heart‑rate zone distribution overall ————————————————
zones = {
    "Zone 1 (<150 bpm)": (running_df["hr"] < 150).sum(),
    "Zone 2 (150–170 bpm)": ((running_df["hr"] >= 150) & (running_df["hr"] < 170)).sum(),
    "Zone 3 (≥170 bpm)": (running_df["hr"] >= 170).sum(),
}
total_samples = sum(zones.values())
zone_pct = {k: v / total_samples * 100 for k, v in zones.items()}

plt.figure()
plt.bar(zone_pct.keys(), zone_pct.values())
plt.ylabel("Time share (%)")
plt.title("Heart‑rate zone distribution across all runs")
plt.xticks(rotation=25)
plt.tight_layout()
plt.savefig("hr_zones.png")

display(
    runs[["date", "distance_km", "pace_min_km", "avg_hr", "aerobic_pct"]].round(
        {"distance_km": 2, "pace_min_km": 2, "avg_hr": 1, "aerobic_pct": 1}
    )
)

display(metrics)
