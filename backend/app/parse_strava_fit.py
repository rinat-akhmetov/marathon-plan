#!/usr/bin/env python3
"""
parse_strava_fit.py — Extract rich running metrics from a Strava .fit or .fit.gz file.

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

import gzip
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .utils import TrackPoint

try:
    from fitparse import FitFile  # type: ignore
    from fitparse.records import DataMessage  # Added to help with type hinting
except ModuleNotFoundError:
    sys.exit("❌ 'fitparse' library is required. Install it with:  pip install fitparse")


# ────────────────────────────────────────────────────────────────────────────────
#  FIT parsing helpers
# ────────────────────────────────────────────────────────────────────────────────


_SEMICIRCLE_TO_DEG = 180.0 / 2**31


def _semicircle_to_deg(value: Optional[int]) -> Optional[float]:
    return value * _SEMICIRCLE_TO_DEG if value is not None else None


# ────────────────────────────────────────────────────────────────────────────────
#  Core parser
# ────────────────────────────────────────────────────────────────────────────────
def _extract_sport(fit):
    # try sport messages first
    for m in fit.get_messages("sport"):
        for key in ("sport", "sub_sport", "name"):
            val = m.get_value(key)
            if val not in (None, "", 0):
                return str(val)

    # then sessions
    for m in fit.get_messages("session"):
        for key in ("sport", "sub_sport", "sport_name", "name"):
            val = m.get_value(key)
            if val not in (None, "", 0):
                return str(val)

    return "unknown"


def parse_fit(path: str) -> List[TrackPoint]:  # Updated return type
    """Return a GpxData object from a *.fit* or *.fit.gz* file."""

    # Auto‑detect compression
    if path.endswith(".gz"):
        fit_io = gzip.open(path, "rb")
    else:
        fit_io = open(path, "rb")

    fit = FitFile(fit_io)
    track_points_data: List[TrackPoint] = []
    activity_type: Optional[str] = None
    activity_type = _extract_sport(fit)

    for record in fit.get_messages("record"):
        if not isinstance(record, DataMessage):
            continue

        lat_raw = record.get_value("position_lat")
        lon_raw = record.get_value("position_long")
        lat = _semicircle_to_deg(lat_raw)
        lon = _semicircle_to_deg(lon_raw)

        if lat is None or lon is None:
            continue  # skip points lacking coordinates

        # Ensure timestamp is datetime object
        timestamp_raw = record.get_value("timestamp")
        timestamp: Optional[datetime] = None
        if isinstance(timestamp_raw, datetime):
            timestamp = timestamp_raw

        # Ensure heart rate is int or None
        hr_raw = record.get_value("heart_rate")
        hr: Optional[int] = None
        if isinstance(hr_raw, (int, float)):  # fitparse might return float for hr sometimes
            hr = int(hr_raw)

        name = Path(path).stem
        pt = TrackPoint(
            time=timestamp,
            lat=lat,
            lon=lon,
            ele=record.get_value("altitude"),  # altitude is usually float
            hr=hr,
            activity_type=activity_type,
            run=name,
        )
        track_points_data.append(pt)

    fit_io.close()  # Important to close the file handle

    return track_points_data


# ────────────────────────────────────────────────────────────────────────────────
#  Metric enrichment (same logic as GPX version)
# ────────────────────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────────────────────
#  CLI
# ────────────────────────────────────────────────────────────────────────────────
