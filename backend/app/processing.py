import datetime
import logging
import os
import pathlib
import tempfile
import zipfile
from functools import lru_cache
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from pydantic import BaseModel

from .parse_strava_fit import parse_fit
from .parse_strava_gpx import parse_gpx

HR_ZONES = [(0, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]

logging.basicConfig(level=logging.INFO)


class RunSummary(BaseModel):
    run_id: Any
    date: datetime.date
    distance_km: float
    duration_sec: float
    pace_sec_per_km: float | None
    avg_hr: float | None
    aerobic_pct: float | None
    pace_min_km: float | None

    @property
    def distance_km(self) -> float:
        return self._distance_km

    @distance_km.setter
    def distance_km(self, value: float):
        self._distance_km = None if pd.isna(value) else value

    @property
    def duration_sec(self) -> float:
        return self._duration_sec

    @duration_sec.setter
    def duration_sec(self, value: float):
        self._duration_sec = None if pd.isna(value) else value

    @property
    def pace_sec_per_km(self) -> float | None:
        return self._pace_sec_per_km

    @pace_sec_per_km.setter
    def pace_sec_per_km(self, value: float | None):
        self._pace_sec_per_km = None if pd.isna(value) else value

    @property
    def avg_hr(self) -> float | None:
        return self._avg_hr

    @avg_hr.setter
    def avg_hr(self, value: float | None):
        self._avg_hr = None if pd.isna(value) else value

    @property
    def aerobic_pct(self) -> float | None:
        return self._aerobic_pct

    @aerobic_pct.setter
    def aerobic_pct(self, value: float | None):
        self._aerobic_pct = None if pd.isna(value) else value

    @property
    def pace_min_km(self) -> float | None:
        return self._pace_min_km

    @pace_min_km.setter
    def pace_min_km(self, value: float | None):
        self._pace_min_km = None if pd.isna(value) else value


class Metric(BaseModel):
    Metric: str
    Value: Any


class AnalyzeRunsOutput(BaseModel):
    runs: List[RunSummary]
    metrics: List[Metric]
    zone_pct: Dict[str, float]


@lru_cache(maxsize=10)
def process_zip(zip_bytes: bytes) -> AnalyzeRunsOutput:
    with tempfile.TemporaryDirectory() as td:
        zip_path = os.path.join(td, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)
        with zipfile.ZipFile(zip_path) as zf:
            dfs = []
            for name in zf.namelist():
                if "activities" not in name:
                    continue
                ext = pathlib.Path(name).suffix.lower()
                logging.info(f"Extracting {name} with extension {ext}")
                extract_path = zf.extract(name, path=td)
                if name.endswith(".fit") or name.endswith(".fit.gz"):
                    track_points = parse_fit(extract_path)
                    logging.info(f"Parsed {len(track_points)} track points from {extract_path}")
                    if track_points:
                        dfs.append(pd.DataFrame([item.model_dump() for item in track_points]))
                elif name.endswith(".gpx"):
                    track_points = parse_gpx(extract_path)
                    logging.info(f"Parsed {len(track_points)} track points from {extract_path}")
                    if track_points:
                        dfs.append(pd.DataFrame([item.model_dump() for item in track_points]))
        if not dfs:
            raise ValueError("No FIT/GPX files found")
        df = pd.concat(dfs, ignore_index=True)
        # df.to_csv("test.csv", index=False)
        logging.info(f"Analyzing {len(df)} runs")
        runs, metrics, zone_pct = analyze_runs(df)
        logging.info(f"Analyzed {len(df)} runs")
        return AnalyzeRunsOutput(runs=runs, metrics=metrics, zone_pct=zone_pct)


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


def parse_time(s: str) -> datetime.datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S%z"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None  # or raise, or pd.NaT


def parse_time_df(df: pd.DataFrame) -> pd.DataFrame:
    # 1) define your two regexes
    naive_re = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
    tz_re = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$"

    # 2) build masks
    df["time"] = df["time"].astype(str)
    mask_naive = df["time"].str.match(naive_re, na=False)
    mask_tz = df["time"].str.match(tz_re, na=False)

    # 3) slice out each group
    df_naive = df[mask_naive].copy()
    df_tz = df[mask_tz].copy()

    # 4) parse with the exact format string
    df_naive["time_parsed"] = pd.to_datetime(
        df_naive["time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",  # or 'coerce' if you want invalid → NaT
        utc=True,
    )

    df_tz["time_parsed"] = pd.to_datetime(
        df_tz["time"],
        format="%Y-%m-%d %H:%M:%S%z",
        errors="raise",
        utc=True,
    )

    # 5) recombine if you like
    df_parsed = pd.concat([df_naive, df_tz]).sort_index()
    return df_parsed


def analyze_runs(df: pd.DataFrame) -> tuple[List[RunSummary], List[Metric], Dict[str, float]]:
    """
    Analyze running activities from a CSV file and return summary DataFrames.

    Args:
        csv_path (str): Path to the CSV file containing activity data.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (runs, metrics)
    """

    # Identify running activities
    running_df = df[df["activity_type"] == "running"].copy()
    running_df = parse_time_df(running_df)
    running_df["time"] = running_df["time_parsed"]
    running_df = running_df.sort_values(by=["run", "time"]).copy()

    runs_summary = []
    for run_id, g in running_df.groupby("run"):
        g = g.sort_values("time")
        # Distance
        lat, lon = g["lat"].to_numpy(), g["lon"].to_numpy()
        valid = ~(np.isnan(lat) | np.isnan(lon))
        valid_lat = lat[valid]
        valid_lon = lon[valid]
        dist_m = 0.0
        for i in range(len(valid_lat) - 1):
            dist_m += haversine(valid_lat[i], valid_lon[i], valid_lat[i + 1], valid_lon[i + 1]) * 1000
            g.loc[g.index[i + 1], "dist_m"] = dist_m
        distance = max(g["distance"].max(), dist_m)
        # Duration
        duration_sec = (g["time"].max() - g["time"].min()).total_seconds()
        # Heart‑rate
        avg_hr = g["hr"].mean()
        # Aerobic % (<150 bpm)
        if g["hr"].count() > 0:
            aerobic_pct = (g["hr"] < 150).sum() / g["hr"].count() * 100
        else:
            aerobic_pct = None
        runs_summary.append(
            {
                "run_id": run_id,
                "date": g["time"].max().date(),
                "distance_km": distance / 1000,
                "duration_sec": duration_sec,
                "pace_sec_per_km": duration_sec / distance / 1000 if distance else None,
                "avg_hr": avg_hr,
                "aerobic_pct": aerobic_pct,
            }
        )

    runs = pd.DataFrame(runs_summary)
    runs["pace_min_km"] = runs["pace_sec_per_km"] / 60

    # Key metrics
    total_distance = runs["distance_km"].sum()
    total_duration_h = runs["duration_sec"].sum() / 3600
    overall_pace_sec = runs["duration_sec"].sum() / total_distance if total_distance else np.nan
    avg_pace_per_run_sec = runs["pace_sec_per_km"].mean() if not runs.empty else np.nan

    marathons = runs[runs["distance_km"] >= 42.195]
    avg_marathon_pace_sec = marathons["pace_sec_per_km"].mean() if not marathons.empty else np.nan

    # Updated heart rate zones calculation (5 zones)
    zone_pct = {}
    if "hr" in running_df and running_df["hr"].count() > 0:
        max_hr = running_df["hr"].max()
        zones = {}
        running_df = running_df.sort_values("time")
        running_df["delta_time"] = running_df["time"].diff().dt.total_seconds().fillna(0)
        for i, (low, high) in enumerate(HR_ZONES):
            zone_df = running_df[(running_df["hr"] / max_hr >= low) & (running_df["hr"] / max_hr < high)]
            zones[f"zone_{i + 1}"] = round(zone_df["delta_time"].sum() / 60, 1)
        total_zone_time = sum(zones.values())
        if total_zone_time > 0:
            zone_pct = {k: v / total_zone_time * 100 for k, v in zones.items()}
        else:
            zone_pct = {k: 0.0 for k in zones.keys()}
    else:
        zone_pct = {f"zone_{i + 1}": 0.0 for i in range(len(HR_ZONES))}

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
                round(overall_pace_sec / 60, 2) if not np.isnan(overall_pace_sec) else "—",
                round(avg_pace_per_run_sec / 60, 2) if not np.isnan(avg_pace_per_run_sec) else "—",
                len(marathons),
                round(avg_marathon_pace_sec / 60, 2) if not np.isnan(avg_marathon_pace_sec) else "—",
            ],
        }
    )

    for r in runs.to_dict(orient="records"):
        print(r)

    runs_summary = [RunSummary.model_validate(r) for r in runs.to_dict(orient="records")]
    metrics = [Metric.model_validate(m) for m in metrics.to_dict(orient="records")]
    zone_pct = {k: v for k, v in zone_pct.items()}
    return runs_summary, metrics, zone_pct


if __name__ == "__main__":
    # df = pd.read_csv("test.csv")
    # print(runs)
    # print(metrics)
    # print(zone_pct)
    # print(AnalyzeRunsOutput(runs=runs, metrics=metrics, zone_pct=zone_pct))
    with open("/Users/arrtz3/Downloads/export_137365229.zip", "rb") as f:
        print(process_zip(f.read()))
