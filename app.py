"""Streamlit entry point.  Run:  streamlit run app.py"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chart import build_figure, fmt_count, fmt_duration, size_legend_values
from data import COLS, fetch_metrics
from theme import FONT, palette

st.set_page_config(page_title="Video performance", page_icon="●", layout="wide")


def current_mode() -> str:
    try:
        return st.context.theme.type or "light"
    except Exception:
        return st.get_option("theme.base") or "light"


def size_legend_svg(sizes: pd.Series, p: dict[str, str]) -> str:
    """Bubble-area key. Without it, circle size carries no readable meaning."""
    items = size_legend_values(sizes)
    slot, baseline = 88, 72
    parts = []
    for i, (value, diameter) in enumerate(items):
        cx = 8 + slot * i + slot / 2
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{baseline - diameter / 2:.1f}" '
            f'r="{diameter / 2:.1f}" fill="{p["series"]}" fill-opacity="0.72" '
            f'stroke="{p["surface"]}" stroke-width="2" />'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="88" text-anchor="middle" font-size="11" '
            f"fill='{p['muted']}' font-family='{FONT}'>{fmt_count(value)}</text>"
        )
    width = 16 + slot * len(items)
    return (
        f'<svg width="{width}" height="96" viewBox="0 0 {width} 96" '
        f'role="img" aria-label="Bubble size key: watch time in minutes">'
        + "".join(parts)
        + "</svg>"
    )


df = fetch_metrics()
p = palette(current_mode())

st.markdown("### Video performance")
st.caption(
    "Each bubble is one video — reach across, engagement up, total watch time as area."
)

# One filter row above everything it scopes.
left, mid, right = st.columns([3, 1, 1], vertical_alignment="bottom")
with left:
    picked = st.multiselect(
        "Videos",
        options=list(df[COLS.label]),
        default=list(df[COLS.label]),
        placeholder="All videos",
    )
with mid:
    log_x = st.toggle("Log views", value=False)
with right:
    show_medians = st.toggle("Median lines", value=True)

view = df[df[COLS.label].isin(picked)] if picked else df

if view.empty:
    st.info("No videos selected.")
    st.stop()

st.plotly_chart(
    build_figure(view, current_mode(), show_medians=show_medians, log_x=log_x),
    width="stretch",
    config={"displayModeBar": False, "scrollZoom": True},
)

st.caption("Watch time — estimated minutes watched")
st.markdown(size_legend_svg(view[COLS.size], p), unsafe_allow_html=True)

with st.expander("Table view"):
    st.dataframe(
        pd.DataFrame(
            {
                "Video": view[COLS.label],
                "Views": [f"{v:,.0f}" for v in view[COLS.x]],
                "Avg view duration": [fmt_duration(v) for v in view[COLS.y]],
                "Watch time (min)": [f"{v:,.0f}" for v in view[COLS.size]],
            }
        ),
        hide_index=True,
        width="stretch",
    )
