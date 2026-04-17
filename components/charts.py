from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.theme import CHART_LAYOUT
from elhub.labels import label_production_group

PRODUCTION_COLORS: dict[str, str] = {
    "solar":     "#f4a523",
    "hydro":     "#1a6b8a",
    "wind":      "#5ba85a",
    "thermal":   "#c0543a",
    "other":     "#8a7a9b",
    "remainder": "#b0b0b0",  # Elhub privacy bucket — totals correct but group too small to disclose
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
    agg["produksjonstype"] = agg["production_group"].map(label_production_group)

    fig = px.line(
        agg,
        x="usage_date",
        y="installed_capacity_kw",
        color="produksjonstype",
        color_discrete_map={
            label_production_group(k): v for k, v in PRODUCTION_COLORS.items()
        },
        labels={
            "usage_date": "",
            "installed_capacity_kw": "Installert kapasitet (kW)",
            "produksjonstype": "Produksjonstype",
        },
        title=f"Installert kapasitet over tid — {municipality_name}",
    )
    fig.update_layout(**CHART_LAYOUT, legend_title_text="")
    fig.update_xaxes(hoverformat="%d.%m.%Y")
    fig.update_traces(hovertemplate="%{y:,.0f} kW<extra></extra>")
    return fig


def leaders_chart(df: pd.DataFrame, group: str, top_n: int = 10) -> go.Figure:
    """
    Horizontal bar chart of top N municipalities for a given production group.

    Args:
        df: Snapshot DataFrame from fetch_latest_snapshot().
        group: Production group ID (e.g. "solar").
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
            "installed_capacity_kw": "Installert kapasitet (kW)",
            "municipality_name": "",
        },
        title=f"Topp {top_n} kommuner — {label_production_group(group)}",
    )
    fig.update_layout(**CHART_LAYOUT, showlegend=False)
    fig.update_layout(hovermode=False)
    return fig
