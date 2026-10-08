"""Metric source for the bubble chart.

Rows come from slide-gen-reports' ``POST /v1/traffic_source/videos`` at
``REPORTS_API_URL``, the service's base URL; requests carry
``REPORTS_API_TOKEN`` as a bearer token. Everything downstream depends only on
the names in `Columns`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

import pandas as pd
import requests


@dataclass(frozen=True)
class Columns:
    """Column contract between the data source and the chart."""

    label: str = "title"                    # row identity, used for hover / table
    x: str = "views"                        # x-axis
    y: str = "avg_view_duration_sec"        # y-axis: engagement
    size: str = "watch_time_min"            # bubble area


COLS = Columns()

# slide-gen-reports field -> chart column. The API has no titles, so the
# video ID is the row label.
_API_FIELDS = {
    "video_id": COLS.label,
    "views": COLS.x,
    "average_view_duration_seconds": COLS.y,
    "watch_time_minutes": COLS.size,
}

VIDEO_ID = re.compile(r"^[\w-]{11}$")


def fetch_metrics(
    video_ids: tuple[str, ...], *, days: int = 7, timeout: float = 60
) -> pd.DataFrame:
    """Return one row per given video with the three plotted metrics.

    Over the latest ``days`` report dates. Videos without views are left out.
    """
    base = os.environ.get("REPORTS_API_URL")
    if not base:
        raise RuntimeError("REPORTS_API_URL is not set")

    # A POST, as the list of IDs can be long.
    resp = requests.post(
        f"{base.rstrip('/')}/v1/traffic_source/videos",
        json={"video_ids": list(video_ids), "days": days},
        headers={"Authorization": f"Bearer {os.environ.get('REPORTS_API_TOKEN', '')}"},
        timeout=timeout,
    )
    resp.raise_for_status()

    df = pd.DataFrame(resp.json()["videos"], columns=list(_API_FIELDS))
    return df.rename(columns=_API_FIELDS)
