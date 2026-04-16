import httpx
import json
import streamlit as st

GEOJSON_URL = (
    "https://raw.githubusercontent.com/robhop/fylker-og-kommuner/main/kommuner-simple.geojson"
)


@st.cache_data(ttl=86400, show_spinner=False)
def load_kommuner_geojson() -> dict:
    """Fetch and cache the Norwegian municipality GeoJSON."""
    with httpx.Client(timeout=30) as client:
        r = client.get(GEOJSON_URL)
        r.raise_for_status()
    return r.json()
