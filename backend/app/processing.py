import datetime
import logging
import os
import pathlib
import tempfile
import zipfile
from typing import Any, Dict, List

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


class Metric(BaseModel):
    Metric: str
    Value: Any


class AnalyzeRunsOutput(BaseModel):
    runs: List[RunSummary]
    metrics: List[Metric]
    zone_pct: Dict[str, float]


def process_zip(zip_bytes: bytes) -> dict[str, Any]:
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
                    dfs.append(pd.DataFrame([item.model_dump() for item in track_points]))
                elif name.endswith(".gpx"):
                    track_points = parse_gpx(extract_path)
                    logging.info(f"Parsed {len(track_points)} track points from {extract_path}")
                    dfs.append(pd.DataFrame([item.model_dump() for item in track_points]))
        if not dfs:
            raise ValueError("No FIT/GPX files found")
        df = pd.concat(dfs, ignore_index=True)
        logging.info(f"Analyzing {len(df)} runs")
        runs, metrics, zone_pct = analyze_runs(df)
        logging.info(f"Analyzed {len(df)} runs")
        return {
            "runs": runs.to_dict(orient="records"),
            "metrics": metrics.to_dict(orient="records"),
            "zone_pct": zone_pct,
        }
