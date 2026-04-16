import httpx
from datetime import date, timedelta
from .models import EhubResponse, response_to_df
import pandas as pd
import streamlit as st

BASE_URL = "https://api.elhub.no/energy-data/v0"
DATASET = "INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY"


def _date_param(d: date) -> str:
    return f"{d.isoformat()}T00:00:00+02:00"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_latest_snapshot() -> pd.DataFrame:
    """Fetch the most recent available daily snapshot for all municipalities."""
    end = date.today()
    start = end - timedelta(days=7)  # look back up to 7 days to find latest data
    params = {
        "dataset": DATASET,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    with httpx.Client(timeout=30) as client:
        r = client.get(f"{BASE_URL}/municipalities", params=params)
        r.raise_for_status()
    
    parsed = EhubResponse.model_validate(r.json())
    df = response_to_df(parsed)
    
    if df.empty:
        return df
    
    # Keep only the most recent date
    latest = df["usage_date"].max()
    return df[df["usage_date"] == latest].copy()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_history(municipality_id: str, months: int = 12) -> pd.DataFrame:
    """Fetch monthly history for a single municipality by paginating month by month."""
    end = date.today()
    frames = []

    for i in range(months):
        month_end = end.replace(day=1) - timedelta(days=1) if i == 0 else month_end.replace(day=1) - timedelta(days=1)
        month_start = month_end.replace(day=1)
        if i == 0:
            month_end = end

        params = {
            "dataset": DATASET,
            "startDate": _date_param(month_start),
            "endDate": _date_param(month_end),
        }
        with httpx.Client(timeout=30) as client:
            r = client.get(
                f"{BASE_URL}/municipalities/{municipality_id}",
                params=params,
            )
            if r.status_code == 404:
                continue
            r.raise_for_status()
        
        parsed = EhubResponse.model_validate(r.json())
        df = response_to_df(parsed)
        if not df.empty:
            # Take last day of each month as the snapshot
            frames.append(df[df["usage_date"] == df["usage_date"].max()])

    if not frames:
        return pd.DataFrame()
    
    return pd.concat(frames, ignore_index=True)
