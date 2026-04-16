import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PRODUCTION_COLORS = {
    "solar":   "#f4a523",
    "hydro":   "#1a6b8a",
    "wind":    "#5ba85a",
    "thermal": "#c0543a",
    "other":   "#8a7a9b",
}


def history_chart(df: pd.DataFrame, municipality_name: str) -> go.Figure:
    """Line chart of installed capacity over time, split by production group."""
    agg = (
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
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="serif",
        title_font_size=16,
        legend_title_text="",
        hovermode="x unified",
    )
    return fig


def leaders_chart(df: pd.DataFrame, group: str, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of top N municipalities for a production group."""
    filtered = df[df["production_group"] == group]
    agg = (
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
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="serif",
        title_font_size=16,
        showlegend=False,
    )
    return fig
