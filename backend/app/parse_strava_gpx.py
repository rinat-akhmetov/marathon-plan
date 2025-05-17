#!/usr/bin/env python3
"""
parse_strava_gpx.py — Extract rich running metrics from a Strava‑exported GPX file.

USAGE:
    python parse_strava_gpx.py path/to/activity.gpx -o out.csv

FEATURES:
• Reads every <trkpt> in the GPX file, capturing latitude, longitude, elevation, timestamp, and heart‑rate (if present).
• Computes segment‑by‑segment distance with the Haversine formula, cumulative distance, total elapsed time, and average pace.
• Prints a human‑readable run summary to stdout.
• Optionally writes a fully‑detailed CSV (one row per track‑point) for further analysis or visualisation in a "running canvas".
• Depends **only** on the Python 3 standard library — no extra installs required.

Author: ChatGPT (o3)
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from utils import TrackPoint

# ────────────────────────────────────────────────────────────────────────────────
#  GPX parsing
# ────────────────────────────────────────────────────────────────────────────────


def parse_gpx(path: str) -> List[TrackPoint]:
    """Parse a GPX file and return a GpxData object."""
    ns = {
        "": "http://www.topografix.com/GPX/1/1",
        "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
    }

    tree = ET.parse(path)
    root = tree.getroot()

    activity_type_val: Optional[str] = None
    trk_element = root.find(".//{http://www.topografix.com/GPX/1/1}trk")
    if trk_element is not None:
        type_element = trk_element.find("{http://www.topografix.com/GPX/1/1}type")
        if type_element is not None and type_element.text:
            activity_type_val = type_element.text

    trkpts = root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")

    track_point_data = []
    for pt in trkpts:
        lat = float(pt.attrib["lat"])
        lon = float(pt.attrib["lon"])

        ele_el = pt.find("{http://www.topografix.com/GPX/1/1}ele")
        ele_val = None
        if ele_el is not None and ele_el.text is not None:
            try:
                ele_val = float(ele_el.text)
            except (ValueError, TypeError):
                ele_val = None  # Keep as None if conversion fails

        time_el = pt.find("{http://www.topografix.com/GPX/1/1}time")
        time_val: Optional[datetime] = None
        if time_el is not None and time_el.text is not None:
            try:
                time_val = datetime.fromisoformat(time_el.text.replace("Z", "+00:00"))
            except ValueError:
                time_val = None  # Keep as None if timestamp is invalid

        hr_el = pt.find(".//{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr")
        hr_val = None
        if hr_el is not None and hr_el.text is not None:
            try:
                hr_val = int(hr_el.text)
            except (ValueError, TypeError):
                hr_val = None  # Keep as None if conversion fails

        name = Path(path).stem
        track_point_data.append(
            TrackPoint(
                time=time_val,
                lat=lat,
                lon=lon,
                ele=ele_val,
                hr=hr_val,
                activity_type=activity_type_val,
                run=name,
            )
        )
    return track_point_data
