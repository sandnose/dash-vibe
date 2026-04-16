import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from elhub.client import fetch_latest_snapshot, fetch_history
from components.map import build_choropleth
from components.leaders import render_leaders
from components.history import render_history

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Norwegian Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Elhub-inspired theme ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Elhub brand colors: deep navy #1a3a5c, green #4caf50, light grey bg */
    [data-testid="stAppViewContainer"] {
        background-color: #f5f7fa;
    }
    [data-testid="stSidebar"] {
        background-color: #1a3a5c;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stMultiSelect span,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    /* Header bar */
    .elhub-header {
        background: linear-gradient(90deg, #1a3a5c 0%, #1e5f8c 100%);
        padding: 1.2rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .elhub-header h1 {
        color: white;
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
    }
    .elhub-header .powered-by {
        color: #a8d5f5;
        font-size: 0.8rem;
    }
    .elhub-header .powered-by a {
        color: #4caf50;
        text-decoration: none;
        font-weight: 600;
    }
    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border-left: 4px solid #4caf50;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a3a5c;
        border-radius: 8px 8px 0 0;
        padding: 0 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a8d5f5 !important;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: white !important;
        border-bottom: 3px solid #4caf50 !important;
    }
    /* Snapshot badge */
    .snapshot-badge {
        background: #e8f5e9;
        border: 1px solid #4caf50;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.85rem;
        color: #1a3a5c;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="elhub-header">
    <h1>⚡ Norwegian Energy Dashboard</h1>
    <div class="powered-by">
        Powered by <a href="https://api.elhub.no" target="_blank">api.elhub.no</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
PRODUCTION_GROUPS = ["solar", "hydro", "wind", "thermal", "other"]
ICONS = {"solar": "☀️", "hydro": "💧", "wind": "🌬️", "thermal": "🔥", "other": "⚡"}

with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    selected_groups = st.multiselect(
        "Production group",
        options=PRODUCTION_GROUPS,
        default=PRODUCTION_GROUPS,
        format_func=lambda x: f"{ICONS.get(x, '')} {x.capitalize()}",
    )
    if not selected_groups:
        selected_groups = PRODUCTION_GROUPS

    metering_type = st.radio(
        "Metering point type",
        options=["both", "E18", "E19"],
        format_func=lambda x: {
            "both": "Both (E18 + E19)",
            "E18": "E18 — Grid-connected",
            "E19": "E19 — Local / prosumers",
        }[x],
    )

    st.markdown("---")
    st.markdown("**About**")
    st.markdown(
        "Data: [Elhub Energy Data API](https://api.elhub.no/energy-data-api)\n\n"
        "Map: [Kartverket](https://www.kartverket.no) via robhop/fylker-og-kommuner\n\n"
        "Capacity unit: **kW** (charts in MW)"
    )

# ── Load snapshot ──────────────────────────────────────────────────────────────
with st.spinner("Loading latest data from Elhub..."):
    snapshot_df = fetch_latest_snapshot()

if snapshot_df.empty:
    st.error("Could not fetch data from Elhub. Please try again later.")
    st.stop()

snapshot_date = snapshot_df["usage_date"].max().strftime("%d %b %Y")

# ── Summary metrics ────────────────────────────────────────────────────────────
filtered = snapshot_df[snapshot_df["production_group"].isin(selected_groups)]
if metering_type != "both":
    filtered = filtered[filtered["metering_type"] == metering_type]

total_mw = filtered["installed_capacity_kw"].sum() / 1000
n_municipalities = filtered["municipality_id"].nunique()
top_group = (
    filtered.groupby("production_group")["installed_capacity_kw"].sum().idxmax()
    if not filtered.empty else "—"
)

col1, col2, col3 = st.columns(3)
col1.metric("Total installed capacity", f"{total_mw:,.0f} MW")
col2.metric("Municipalities with data", n_municipalities)
col3.metric("Dominant production group", f"{ICONS.get(top_group, '')} {top_group.capitalize()}")

st.markdown(f'<div class="snapshot-badge">📅 Snapshot: {snapshot_date}</div>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_map, tab_history, tab_leaders = st.tabs(["🗺️ Map", "📈 History", "🏆 Leaders"])

# ── Map tab ────────────────────────────────────────────────────────────────────
with tab_map:
    with st.spinner("Rendering map..."):
        m = build_choropleth(snapshot_df, selected_groups, metering_type)
    st_folium(m, use_container_width=True, height=620, returned_objects=[])

# ── History tab ────────────────────────────────────────────────────────────────
with tab_history:
    municipalities = (
        snapshot_df[["municipality_id", "municipality_name"]]
        .drop_duplicates()
        .sort_values("municipality_name")
    )
    muni_options = {
        row["municipality_name"]: row["municipality_id"]
        for _, row in municipalities.iterrows()
    }

    selected_muni_name = st.selectbox("Select municipality", options=list(muni_options.keys()))
    selected_muni_id = muni_options[selected_muni_name]

    months = st.slider("Months of history", min_value=1, max_value=24, value=12)

    with st.spinner(f"Loading history for {selected_muni_name}..."):
        history_df = fetch_history(selected_muni_id, months=months)

    render_history(history_df, selected_muni_name)

# ── Leaders tab ────────────────────────────────────────────────────────────────
with tab_leaders:
    top_n = st.slider("Show top N municipalities", min_value=3, max_value=20, value=5)
    render_leaders(snapshot_df, top_n=top_n)
