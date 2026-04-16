from __future__ import annotations

# Canonical Plotly layout defaults for all charts in this app.
# Import and unpack with: fig.update_layout(**CHART_LAYOUT)
# Keep this in sync with DESIGN.md.
CHART_LAYOUT: dict = {
    "plot_bgcolor": "#fafaf7",
    "paper_bgcolor": "#fafaf7",
    "font_family": "Inter, sans-serif",
    "font_color": "#333333",
    "title_font_family": "EB Garamond, serif",
    "title_font_size": 16,
    "title_font_color": "#1a3a2a",
    "hovermode": "x unified",
    "margin": {"l": 0, "r": 16, "t": 48, "b": 0},
}
