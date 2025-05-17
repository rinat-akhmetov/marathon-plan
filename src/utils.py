#!/usr/bin/env python3
"""
Utility functions for parsing and processing ভয়ঙ্করunning activity data.
Includes Haversine calculation, metric enrichment, CSV writing, and Pydantic models.

USAGE:
    python parse_strava_fit.py path/to/activity.fit[.gz] -o out.csv

FEATURES:
• Transparently handles raw *.fit* and compressed *.fit.gz* files.
• Leverages the `fitparse` library to iterate over every **record** message.
• Collects latitude, longitude, altitude, timestamp, and heart‑rate (when present).
• Converts FIT *semicircle* coordinates to standard WGS‑84 degrees.
• Computes segment distance (Haversine), cumulative distance, elapsed time, and average pace.
• Prints a tidy run summary to stdout and, optionally, writes a per‑track‑point CSV identical to *parse_strava_gpx.py* — perfect drop‑in for your running canvas.

DEPENDENCIES:
    pip install fitparse>=1.2.0

Author: ChatGPT (o3)
"""

import csv
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# ────────────────────────────────────────────────────────────────────────────────
#  Pydantic Models
# ────────────────────────────────────────────────────────────────────────────────


class TrackPoint(BaseModel):
    time: Optional[datetime] = None
    lat: float
    lon: float
    ele: Optional[float] = None
    hr: Optional[int] = None


class GpxData(BaseModel):
    track_points: List[TrackPoint]
    activity_type: Optional[str] = None


class CsvRowData(TrackPoint):  # New model for CSV rows
    run: str
    activity_type: Optional[str] = None
    seg_distance_m: Optional[float] = None
    cum_distance_km: Optional[float] = None


# ────────────────────────────────────────────────────────────────────────────────
#  Geolocation and Metrics
# ────────────────────────────────────────────────────────────────────────────────


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great‑circle distance in metres between two WGS‑84 coordinates."""

    R = 6_371_000.0  # Earth radius (m)
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)

    a = sin(Δφ / 2) ** 2 + cos(φ1) * cos(φ2) * sin(Δλ / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def enrich_metrics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enriches a list of track point dictionaries with segment/cumulative distance.
    Modifies the input 'data' list in-place.
    Returns a summary dictionary of overall metrics.
    """
    if not data:
        # Attempt to provide a more informative error or handle gracefully
        # For now, let's assume this means no valid track points to process for summary.
        # The function should still handle empty data list for pt processing part.
        print("Warning: enrich_metrics called with empty data list. Summary will be empty.")
        return {
            "total_distance_km": 0,
            "elapsed_time_hms": "0:00:00",
            "average_pace": "0:00 min/km",
            "start_time": None,
            "end_time": None,
        }

    # Add per-point metrics
    current_cumulative_distance_m = 0.0
    previous_point: Optional[Dict[str, Any]] = None
    for point in data:
        segment_distance_m = 0.0
        if (
            previous_point
            and previous_point.get("lat") is not None
            and previous_point.get("lon") is not None
            and point.get("lat") is not None
            and point.get("lon") is not None
        ):
            segment_distance_m = haversine(previous_point["lat"], previous_point["lon"], point["lat"], point["lon"])

        current_cumulative_distance_m += segment_distance_m
        point["seg_distance_m"] = segment_distance_m
        point["cum_distance_km"] = current_cumulative_distance_m / 1000.0
        previous_point = point

    # Calculate summary metrics using points that have time and coordinates
    valid_points_for_summary = [
        pt for pt in data if pt.get("time") is not None and pt.get("lat") is not None and pt.get("lon") is not None
    ]

    if not valid_points_for_summary:
        print("Warning: No valid points with time and coordinates for summary in enrich_metrics.")
        # Return summary based on overall cumulative distance calculated if desired, or empty summary
        return {
            "total_distance_km": round(current_cumulative_distance_m / 1000.0, 2),
            "elapsed_time_hms": "0:00:00",
            "average_pace": "N/A",
            "start_time": None,
            "end_time": None,
        }

    summary_total_distance_m = 0.0
    summary_prev_pt = None
    for pt_summary in valid_points_for_summary:
        if summary_prev_pt:  # Relies on lat/lon being present due to filter above
            summary_total_distance_m += haversine(
                summary_prev_pt["lat"], summary_prev_pt["lon"], pt_summary["lat"], pt_summary["lon"]
            )
        summary_prev_pt = pt_summary

    start_time: datetime = valid_points_for_summary[0]["time"]
    end_time: datetime = valid_points_for_summary[-1]["time"]
    elapsed_seconds = (end_time - start_time).total_seconds() if start_time and end_time else 0

    average_pace_seconds_per_km = 0
    if summary_total_distance_m > 0 and elapsed_seconds > 0:
        average_pace_seconds_per_km = elapsed_seconds / (summary_total_distance_m / 1000.0)

    avg_pace_str = "N/A"
    if average_pace_seconds_per_km > 0:
        pace_minutes = int(average_pace_seconds_per_km // 60)
        pace_seconds = int(average_pace_seconds_per_km % 60)
        avg_pace_str = f"{pace_minutes:02d}:{pace_seconds:02d} min/km"

    return {
        "total_distance_km": round(summary_total_distance_m / 1000.0, 2),
        "elapsed_time_hms": str(end_time - start_time) if start_time and end_time else "0:00:00",
        "average_pace": avg_pace_str,
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": end_time.isoformat() if end_time else None,
    }


# ────────────────────────────────────────────────────────────────────────────────
#  FIT parsing helpers (Consider moving to a FIT-specific module if utils grows)
# ────────────────────────────────────────────────────────────────────────────────

_SEMICIRCLE_TO_DEG = 180.0 / 2**31


def _semicircle_to_deg(value: Optional[int]) -> Optional[float]:
    return value * _SEMICIRCLE_TO_DEG if value is not None else None


# ────────────────────────────────────────────────────────────────────────────────
#  CSV writer
# ────────────────────────────────────────────────────────────────────────────────


def write_csv(data: List[CsvRowData], dst: str) -> None:
    if not data:
        print(f"Info: No data provided to write_csv for destination '{dst}'. File will not be created.")
        return

    fieldnames = list(CsvRowData.model_fields.keys())

    with open(dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for pydantic_row in data:
            row_as_dict = pydantic_row.model_dump(exclude_none=False)
            csv_compatible_dict = {}
            for field_key in fieldnames:
                value = row_as_dict.get(field_key)
                if isinstance(value, datetime):
                    csv_compatible_dict[field_key] = value.isoformat()
                else:
                    csv_compatible_dict[field_key] = value
            writer.writerow(csv_compatible_dict)
