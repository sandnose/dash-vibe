import pandas as pd
import streamlit as st

PRODUCTION_GROUPS = ["hydro", "solar", "wind", "thermal", "other"]

ICONS = {
    "hydro": "💧",
    "solar": "☀️",
    "wind": "🌬️",
    "thermal": "🔥",
    "other": "⚡",
}

ELHUB_BLUE = "#1a3a5c"
ELHUB_GREEN = "#4caf50"


def render_leaders(df: pd.DataFrame, top_n: int = 5):
    if df.empty:
        st.warning("No data available.")
        return

    for group in PRODUCTION_GROUPS:
        group_df = df[df["production_group"] == group].copy()
        if group_df.empty:
            continue

        agg = (
            group_df.groupby(["municipality_id", "municipality_name"])["installed_capacity_kw"]
            .sum()
            .reset_index()
            .sort_values("installed_capacity_kw", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )

        st.markdown(f"### {ICONS.get(group, '⚡')} {group.capitalize()}")

        for i, row in agg.iterrows():
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            capacity_mw = row["installed_capacity_kw"] / 1000
            st.markdown(
                f"{medal} **{row['municipality_name']}** — "
                f"`{capacity_mw:,.1f} MW` installed"
            )

        st.divider()
