import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

from elhub.client import fetch_latest_snapshot, fetch_history
from elhub.geo import load_kommuner_geojson
from components.map import build_choropleth
from components.charts import history_chart, leaders_chart

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="dash-vibe · Norwegian Electricity",
    page_icon="⚡",
    layout="wide",
)

# ── Theme injection (Elhub-inspired) ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'EB Garamond', serif; color: #1a3a2a; }
    .stTabs [data-baseweb="tab"] { font-family: 'Inter', sans-serif; }
    .stTabs [aria-selected="true"] { color: #1a3a2a; border-bottom-color: #1a3a2a; }
    .metric-card {
        background: #f5f5f0;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        border-left: 4px solid #2d6a4f;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("⚡ Norwegian Electricity Dashboard")
st.caption("Data sourced from [Elhub](https://api.elhub.no) · Open data")

# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner("Loading electricity data…"):
    snapshot_df = fetch_latest_snapshot()
    geojson = load_kommuner_geojson()

if snapshot_df.empty:
    st.error("Could not load data from Elhub. Please try again later.")
    st.stop()

latest_date = snapshot_df["usage_date"].max()
all_groups = sorted(snapshot_df["production_group"].unique().tolist())
all_municipalities = (
    snapshot_df[["municipality_id", "municipality_name"]]
    .drop_duplicates()
    .sort_values("municipality_name")
)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_map, tab_history, tab_leaders = st.tabs(["🗺️ Map", "📈 History", "🏆 Leaders"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP
# ════════════════════════════════════════════════════════════════════════════════
with tab_map:
    col_controls, col_map = st.columns([1, 3])

    with col_controls:
        st.markdown(f"**Snapshot date:** {latest_date.strftime('%d %b %Y')}")
        st.divider()

        selected_groups = st.multiselect(
            "Production source",
            options=all_groups,
            default=all_groups,
            format_func=str.capitalize,
        )

        metering_type = st.radio(
            "Scale",
            options=["Both", "E18 — Grid scale", "E19 — Prosumers"],
            index=0,
        )
        metering_code = {
            "Both": "Both",
            "E18 — Grid scale": "E18",
            "E19 — Prosumers": "E19",
        }[metering_type]

    with col_map:
        if not selected_groups:
            st.info("Select at least one production source.")
        else:
            m = build_choropleth(snapshot_df, geojson, selected_groups, metering_code)
            st_folium(m, use_container_width=True, height=620, returned_objects=[])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — HISTORY
# ════════════════════════════════════════════════════════════════════════════════
with tab_history:
    col_sel, col_chart = st.columns([1, 3])

    with col_sel:
        selected_name = st.selectbox(
            "Municipality",
            options=all_municipalities["municipality_name"].tolist(),
        )
        selected_id = all_municipalities.loc[
            all_municipalities["municipality_name"] == selected_name, "municipality_id"
        ].values[0]

        months_back = st.slider("Months of history", min_value=1, max_value=24, value=12)

    with col_chart:
        with st.spinner(f"Loading history for {selected_name}…"):
            hist_df = fetch_history(selected_id, months=months_back)

        if hist_df.empty:
            st.info("No historical data found for this municipality.")
        else:
            st.plotly_chart(
                history_chart(hist_df, selected_name),
                use_container_width=True,
            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — LEADERS
# ════════════════════════════════════════════════════════════════════════════════
with tab_leaders:
    st.markdown(f"**Based on snapshot:** {latest_date.strftime('%d %b %Y')}")
    st.divider()

    top_n = st.slider("Show top N municipalities", min_value=5, max_value=20, value=10)

    cols = st.columns(2)
    for i, group in enumerate(["hydro", "solar", "wind", "thermal", "other"]):
        if group not in all_groups:
            continue
        with cols[i % 2]:
            fig = leaders_chart(snapshot_df, group, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
