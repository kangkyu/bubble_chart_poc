"""Bubble chart: views (x) x average view duration (y) x watch time (area)."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go

from data import COLS
from theme import FONT, palette

MAX_DIAMETER_PX = 62  # largest bubble
MIN_DIAMETER_PX = 10  # floor, so the smallest row is still a hit target


def fmt_duration(seconds: float) -> str:
    """212 -> '3:32'."""
    m, s = divmod(int(round(seconds)), 60)
    return f"{m}:{s:02d}"


def fmt_count(n: float) -> str:
    """1_842_000 -> '1.84M'."""
    n = float(n)
    for cutoff, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= cutoff:
            return f"{n / cutoff:,.2f}".rstrip("0").rstrip(".") + suffix
    return f"{n:,.0f}"


def _sizeref(sizes: pd.Series) -> float:
    """Plotly's documented area-mode scale factor for a given max diameter."""
    return 2.0 * float(sizes.max()) / (MAX_DIAMETER_PX**2)


def size_legend_values(sizes: pd.Series) -> list[tuple[float, float]]:
    """Three reference bubbles for the size key: (value, diameter_px).

    Area-proportional, so diameter = MAX * sqrt(value / max) — the same rule
    plotly applies with sizemode='area'.
    """
    top = float(sizes.max())
    return [
        (top * frac, MAX_DIAMETER_PX * math.sqrt(frac))
        for frac in (1.0, 0.35, 0.08)
    ]


def build_figure(
    df: pd.DataFrame,
    mode: str = "light",
    *,
    show_medians: bool = True,
    log_x: bool = False,
    label_top: int = 3,
) -> go.Figure:
    p = palette(mode)

    customdata = list(
        zip(
            df[COLS.label],
            [f"{v:,.0f}" for v in df[COLS.x]],
            [fmt_duration(v) for v in df[COLS.y]],
            [f"{v:,.0f}" for v in df[COLS.size]],
        )
    )

    # Selective direct labels — the biggest bubbles only. Labelling every one
    # would be a wall of text; the rest are covered by hover and the table view.
    # The labels ride the marker trace so plotly clears them past the bubble edge.
    labelled = set(df.nlargest(label_top, COLS.size)[COLS.label])
    text = [t if t in labelled else "" for t in df[COLS.label]]
    # Anchor labels away from the nearest edge so they never spill out of the plot.
    lo, hi = df[COLS.x].min(), df[COLS.x].max()
    span = (hi - lo) or 1
    text_pos = [
        "top left" if (v - lo) / span > 0.7
        else "top right" if (v - lo) / span < 0.3
        else "top center"
        for v in df[COLS.x]
    ]

    fig = go.Figure(
        go.Scatter(
            x=df[COLS.x],
            y=df[COLS.y],
            mode="markers+text",
            text=text,
            textposition=text_pos,
            textfont=dict(family=FONT, size=11, color=p["text_secondary"]),
            cliponaxis=False,
            marker=dict(
                size=df[COLS.size],
                sizemode="area",
                sizeref=_sizeref(df[COLS.size]),
                sizemin=MIN_DIAMETER_PX,
                color=p["series"],
                opacity=0.72,
                # 2px surface ring so overlapping bubbles stay separate marks
                line=dict(color=p["surface"], width=2),
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Views  %{customdata[1]}<br>"
                "Avg view duration  %{customdata[2]}<br>"
                "Watch time  %{customdata[3]} min"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor=p["surface"],
                bordercolor=p["axis"],
                font=dict(color=p["text_primary"], family=FONT, size=13),
                align="left",
            ),
        )
    )

    if show_medians:
        line = dict(color=p["axis"], width=1, dash="dot")
        fig.add_vline(x=df[COLS.x].median(), line=line, layer="below")
        fig.add_hline(y=df[COLS.y].median(), line=line, layer="below")

    y_ticks = _nice_duration_ticks(df[COLS.y].max())
    fig.update_layout(
        height=560,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor=p["surface"],
        plot_bgcolor=p["surface"],
        font=dict(family=FONT, size=13, color=p["text_secondary"]),
        showlegend=False,
        hovermode="closest",
        # A fixed view: the mouse only hovers, it never pans or zooms.
        dragmode=False,
    )
    fig.update_xaxes(
        fixedrange=True,
        title=dict(text="Views", font=dict(color=p["text_secondary"], size=13)),
        type="log" if log_x else "linear",
        rangemode="tozero" if not log_x else "normal",
        tickformat="~s",
        gridcolor=p["grid"],
        zeroline=False,
        linecolor=p["axis"],
        tickfont=dict(color=p["muted"], size=12),
        ticks="outside",
        tickcolor=p["axis"],
        ticklen=4,
    )
    fig.update_yaxes(
        fixedrange=True,
        title=dict(
            text="Engagement — average view duration",
            font=dict(color=p["text_secondary"], size=13),
        ),
        rangemode="tozero",
        tickmode="array",
        tickvals=y_ticks,
        ticktext=[fmt_duration(v) for v in y_ticks],
        gridcolor=p["grid"],
        zeroline=False,
        linecolor=p["axis"],
        tickfont=dict(color=p["muted"], size=12),
        ticks="outside",
        tickcolor=p["axis"],
        ticklen=4,
    )
    return fig


def _nice_duration_ticks(top: float) -> list[int]:
    """Ticks every 60s (or 120s if that would crowd), covering the data."""
    step = 60 if top <= 420 else 120
    return list(range(0, int(top) + step, step))
