"""Chart palette. Single source of truth for both modes.

One series, so one hue: categorical slot 1 (blue), stepped per mode. Ink and
chrome are recessive by design — the bubbles are the only saturated thing on
the surface.
"""

LIGHT = {
    "surface": "#fcfcfb",
    "text_primary": "#0b0b0b",
    "text_secondary": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "series": "#2a78d6",
}

DARK = {
    "surface": "#1a1a19",
    "text_primary": "#ffffff",
    "text_secondary": "#c3c2b7",
    "muted": "#898781",
    "grid": "#2c2c2a",
    "axis": "#383835",
    "series": "#3987e5",
}

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def palette(mode: str) -> dict[str, str]:
    return DARK if mode == "dark" else LIGHT
