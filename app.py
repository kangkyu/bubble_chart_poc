"""Streamlit entry point.  Run:  streamlit run app.py"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from chart import build_figure, fmt_count, fmt_duration, size_legend_values
from data import COLS, VIDEO_ID, fetch_metrics
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


@st.cache_data(ttl=600, show_spinner="Loading report…")
def load_metrics(video_ids: tuple[str, ...]) -> pd.DataFrame:
    return fetch_metrics(video_ids)


def split_lines(text: str) -> list[str]:
    """One video per line; blank lines and repeats are dropped."""
    ids = []
    for line in text.splitlines():
        line = line.strip()
        if line and line not in ids:
            ids.append(line)
    return ids


def clear_ids() -> None:
    st.session_state.video_ids = ""


mode = current_mode()

st.markdown("### Video performance")
st.caption(
    "Each bubble is one video — reach across, engagement up, total watch time as area."
)

# One filter row above everything it scopes.
left, mid, right = st.columns([3, 1, 1], vertical_alignment="bottom")
with left:
    # A form, so the IDs are sent once on Show, not on every edit. The box
    # holds the whole list: what is in it when Show is pressed replaces the
    # previous list.
    with st.form("videos", border=False):
        st.text_area(
            "Video IDs",
            key="video_ids",
            height=120,
            placeholder="One video ID per line",
        )
        show_col, clear_col, _ = st.columns([1, 1, 4])
        with show_col:
            st.form_submit_button("Show", type="primary", width="stretch")
        with clear_col:
            st.form_submit_button("Clear", on_click=clear_ids, width="stretch")
with mid:
    log_x = st.toggle("Log views", value=False)
with right:
    show_medians = st.toggle("Median lines", value=True)

picked = split_lines(st.session_state.get("video_ids", ""))
invalid = [v for v in picked if not VIDEO_ID.match(v)]
if invalid:
    st.warning(f"Not video IDs (11 letters, digits, - or _): {', '.join(invalid)}")
    picked = [v for v in picked if v not in invalid]

if not picked:
    st.info("Enter video IDs, one per line, and press Show.")
    st.stop()

try:
    view = load_metrics(tuple(picked))
except Exception as exc:
    st.error(f"Couldn't load the report: {exc}")
    st.stop()

if view.empty:
    st.info("No views in the period for any of these videos.")
    st.stop()

missing = [v for v in picked if v not in set(view[COLS.label])]
if missing:
    st.caption(f"No views in the period for: {', '.join(missing)}")

st.plotly_chart(
    build_figure(view, mode, show_medians=show_medians, log_x=log_x),
    width="stretch",
    config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False},
)

st.caption("Watch time — estimated minutes watched")
st.markdown(size_legend_svg(view[COLS.size], palette(mode)), unsafe_allow_html=True)

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
