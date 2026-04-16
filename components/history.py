import pandas as pd
import streamlit as st

PRODUCTION_COLORS = {
    "solar":   "#f4a61d",
    "hydro":   "#1a6bbd",
    "wind":    "#3ea055",
    "thermal": "#d94e2a",
    "other":   "#7b5ea7",
}


def render_history(df: pd.DataFrame, municipality_name: str):
    if df.empty:
        st.info("No historical data available for this municipality.")
        return

    # Take the latest reading per (date, production_group) — ignore E18/E19 split
    agg = (
        df.groupby(["usage_date", "production_group"])["installed_capacity_kw"]
        .sum()
        .reset_index()
    )

    pivot = agg.pivot(index="usage_date", columns="production_group", values="installed_capacity_kw")
    pivot = pivot.sort_index()
    pivot.columns.name = None

    # Convert to MW for readability
    pivot = pivot / 1000

    st.markdown(f"#### Installed capacity over time — {municipality_name}")
    st.line_chart(pivot, color=[PRODUCTION_COLORS.get(c, "#888") for c in pivot.columns])
    st.caption("Values in MW. Each line represents a production group.")
