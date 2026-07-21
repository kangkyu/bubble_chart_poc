"""Metric source for the bubble chart.

The rows are hard-coded for now. When the backend lands, replace the body of
`fetch_metrics()` with the HTTP call and keep the returned column names —
everything downstream depends only on the names in `Columns`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Columns:
    """Column contract between the data source and the chart."""

    label: str = "title"                    # row identity, used for hover / table
    x: str = "views"                        # x-axis
    y: str = "avg_view_duration_sec"        # y-axis: engagement
    size: str = "watch_time_min"            # bubble area


COLS = Columns()

_ROWS = [
    # title,                                 views,   avg view duration (s), watch time (min)
    ("Barbie Dreamhouse Tour",             1_842_000,  212,  6_508_400),
    ("Hot Wheels City Mega Loop",           2_610_000,  138,  6_003_000),
    ("Polly Pocket Compact Reveal",           412_000,  254,  1_744_133),
    ("Monster High Doll Unboxing",            887_000,  301,  4_450_783),
    ("Uno Extreme Family Game Night",         196_000,  176,    574_933),
    ("Mega Bloks Build Challenge",            338_000,   94,    529_533),
    ("Fisher-Price Laugh & Learn Songs",    4_120_000,   67,  4_600_667),
    ("Masters of the Universe Origins",       154_000,  388,    995_733),
    ("Barbie Extra Fashion Haul",             963_000,  145,  2_327_250),
    ("Hot Wheels Monster Trucks Live",        721_000,  233,  2_800_217),
    ("Thomas & Friends Track Builder",      1_355_000,  118,  2_664_833),
    ("Matchbox Action Drivers Playset",       268_000,  161,    719_133),
]


def fetch_metrics() -> pd.DataFrame:
    """Return one row per video with the three plotted metrics.

    Swap point for the backend: build the same DataFrame from the endpoint
    response, e.g.::

        resp = httpx.get(f"{API}/analytics/videos", params={...}).json()
        return pd.DataFrame(resp["rows"])[[COLS.label, COLS.x, COLS.y, COLS.size]]
    """
    return pd.DataFrame(_ROWS, columns=[COLS.label, COLS.x, COLS.y, COLS.size])
