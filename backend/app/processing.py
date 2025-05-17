import os
import pathlib
import tempfile
import zipfile

import fitdecode
import gpxpy
import pandas as pd

HR_ZONES = [(0, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]


def parse_fit(file_path):
    records = []
    with fitdecode.FitReader(file_path) as fr:
        for frame in fr:
            if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == "record":
                d = frame.get_values()
                timestamp = d.get("timestamp")
                if not timestamp:
                    continue
                speed = d.get("enhanced_speed") or d.get("speed")
                hr = d.get("heart_rate")
                distance = d.get("distance")
                records.append({"timestamp": timestamp, "speed": speed, "heart_rate": hr, "distance": distance})
    return pd.DataFrame(records)


def parse_gpx(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append(
                    {
                        "timestamp": point.time,
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "elevation": point.elevation,
                    }
                )
    return pd.DataFrame(data)


def process_zip(zip_bytes: bytes):
    with tempfile.TemporaryDirectory() as td:
        zip_path = os.path.join(td, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)
        with zipfile.ZipFile(zip_path) as zf:
            dfs = []
            for name in zf.namelist():
                ext = pathlib.Path(name).suffix.lower()
                extract_path = zf.extract(name, path=td)
                if ext == ".fit":
                    dfs.append(parse_fit(extract_path))
                elif ext == ".gpx":
                    dfs.append(parse_gpx(extract_path))
        if not dfs:
            raise ValueError("No FIT/GPX files found")
        df = pd.concat(dfs, ignore_index=True)
        return analyze(df)


def analyze(df: pd.DataFrame):
    df = df.sort_values("timestamp")
    df["delta_time"] = df["timestamp"].diff().dt.total_seconds().fillna(0)
    df["distance_delta"] = df["distance"].diff().fillna(0) if "distance" in df else 0
    df["pace"] = df["delta_time"] / (df["distance_delta"] / 1000 + 1e-9)
    summary = {
        "total_distance_km": round(df["distance_delta"].sum() / 1000, 2) if "distance_delta" in df else None,
        "total_time_h": round(df["delta_time"].sum() / 3600, 2),
        "average_pace_min_km": round(df["pace"].mean() / 60, 2),
    }
    if "heart_rate" in df:
        max_hr = df["heart_rate"].max()
        zones = {}
        for i, (low, high) in enumerate(HR_ZONES):
            zone_df = df[(df["heart_rate"] / max_hr >= low) & (df["heart_rate"] / max_hr < high)]
            zones[f"zone_{i + 1}"] = round(zone_df["delta_time"].sum() / 60, 1)
        summary["heart_rate_zones_min"] = zones
    return summary
