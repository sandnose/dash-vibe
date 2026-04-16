from __future__ import annotations

import streamlit as st
from streamlit_folium import st_folium

from components.charts import history_chart, leaders_chart
from components.map import build_choropleth
from elhub.client import fetch_history, fetch_latest_snapshot
from elhub.geo import load_kommuner_geojson

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="dash-vibe · Norwegian Electricity",
    page_icon="⚡",
    layout="wide",
)

# ── Theme injection ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600&family=Inter:wght@300;400;500&display=swap');

    /* Brand background */
    .stApp { background-color: #fafaf7; }

    /* Typography */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'EB Garamond', serif; color: #1a3a2a; }
    h1 { font-size: 1.9rem !important; font-weight: 400 !important; letter-spacing: -0.01em; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #ddd9d0; gap: 0; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #999;
        padding: 0.6rem 1.5rem;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1a3a2a !important;
        border-bottom: 2px solid #1a3a2a !important;
        font-weight: 600;
    }

    /* Dividers */
    [data-testid="stDivider"] { border-color: #ddd9d0; }

    /* Primary button — brand green */
    .stButton > button[kind="primary"] {
        background-color: #1a3a2a !important;
        border-color: #1a3a2a !important;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2d6a4f !important;
        border-color: #2d6a4f !important;
    }

    /* Hide Streamlit decoration bar */
    [data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Norwegian Electricity")
st.caption("Installed generation capacity per municipality · [Elhub open data](https://api.elhub.no)")

# ── Load shared data (always needed) ──────────────────────────────────────────
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
tab_map, tab_history, tab_leaders = st.tabs(["Map", "History", "Leaders"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP
# ════════════════════════════════════════════════════════════════════════════════
with tab_map:
    col_controls, col_map = st.columns([1, 3])

    with col_controls:
        st.markdown(
            f'<div style="margin-bottom:1.25rem">'
            f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;color:#999;margin-bottom:3px">Snapshot</div>'
            f'<div style="font-family:\'EB Garamond\',serif;font-size:1.1rem;color:#1a3a2a">{latest_date.strftime("%d %b %Y")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

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
            st_folium(m, width="100%", height=850, returned_objects=[])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — HISTORY (lazy: only fetches when tab is active)
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

        hist_metering_type = st.radio(
            "Scale",
            options=["Both", "E18 — Grid scale", "E19 — Prosumers"],
            index=0,
        )
        hist_metering_code = {
            "Both": "Both",
            "E18 — Grid scale": "E18",
            "E19 — Prosumers": "E19",
        }[hist_metering_type]

        load_history = st.button("Load history", type="primary")

    with col_chart:
        if load_history:
            with st.spinner(f"Loading history for {selected_name}…"):
                hist_df = fetch_history(selected_id, months=months_back)
            if hist_df.empty:
                st.info("No historical data found for this municipality.")
            else:
                if hist_metering_code != "Both":
                    hist_df = hist_df[hist_df["metering_type"] == hist_metering_code]
                st.plotly_chart(history_chart(hist_df, selected_name), use_container_width=True)
        else:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:center;'
                'height:320px;color:#ccc;font-family:\'EB Garamond\',serif;'
                'font-size:1.15rem;font-style:italic;">'
                'Select a municipality and load history to see trends'
                '</div>',
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — LEADERS
# ════════════════════════════════════════════════════════════════════════════════
with tab_leaders:
    st.markdown(
        f'<div style="margin-bottom:1.25rem">'
        f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;color:#999;margin-bottom:3px">Snapshot</div>'
        f'<div style="font-family:\'EB Garamond\',serif;font-size:1.1rem;color:#1a3a2a">{latest_date.strftime("%d %b %Y")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    top_n = st.slider("Show top N municipalities", min_value=5, max_value=20, value=10)

    cols = st.columns(2)
    for i, group in enumerate(["hydro", "solar", "wind", "thermal", "other", "remainder"]):
        if group not in all_groups:
            continue
        with cols[i % 2]:
            fig = leaders_chart(snapshot_df, group, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)

    if "remainder" in all_groups:
        st.caption(
            "**Remainder** — Elhub privacy bucket: group totals too small to disclose "
            "without identifying individual producers."
        )
