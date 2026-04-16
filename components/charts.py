from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PRODUCTION_COLORS: dict[str, str] = {
    "solar":     "#f4a523",
    "hydro":     "#1a6b8a",
    "wind":      "#5ba85a",
    "thermal":   "#c0543a",
    "other":     "#8a7a9b",
    "remainder": "#b0b0b0",  # Elhub privacy bucket — totals correct but group too small to disclose
}

_LAYOUT_DEFAULTS: dict = {
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


def history_chart(df: pd.DataFrame, municipality_name: str) -> go.Figure:
    """
    Line chart of installed capacity over time, split by production group.

    Args:
        df: History DataFrame from fetch_history().
        municipality_name: Display name for the chart title.
    """
    agg: pd.DataFrame = (
        df.groupby(["usage_date", "production_group"])["installed_capacity_kw"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        agg,
        x="usage_date",
        y="installed_capacity_kw",
        color="production_group",
        color_discrete_map=PRODUCTION_COLORS,
        labels={
            "usage_date": "",
            "installed_capacity_kw": "Installed capacity (kW)",
            "production_group": "Source",
        },
        title=f"Installed capacity over time — {municipality_name}",
    )
    fig.update_layout(**_LAYOUT_DEFAULTS, legend_title_text="")
    return fig


def leaders_chart(df: pd.DataFrame, group: str, top_n: int = 10) -> go.Figure:
    """
    Horizontal bar chart of top N municipalities for a given production group.

    Args:
        df: Snapshot DataFrame from fetch_latest_snapshot().
        group: Production group to rank by (e.g. "solar").
        top_n: Number of municipalities to show.
    """
    filtered = df[df["production_group"] == group]
    agg: pd.DataFrame = (
        filtered.groupby(["municipality_id", "municipality_name"])["installed_capacity_kw"]
        .sum()
        .reset_index()
        .nlargest(top_n, "installed_capacity_kw")
        .sort_values("installed_capacity_kw")
    )

    fig = px.bar(
        agg,
        x="installed_capacity_kw",
        y="municipality_name",
        orientation="h",
        color_discrete_sequence=[PRODUCTION_COLORS.get(group, "#2d6a4f")],
        labels={
            "installed_capacity_kw": "Installed capacity (kW)",
            "municipality_name": "",
        },
        title=f"Top {top_n} municipalities — {group.capitalize()}",
    )
    fig.update_layout(**_LAYOUT_DEFAULTS, showlegend=False)
    return fig
