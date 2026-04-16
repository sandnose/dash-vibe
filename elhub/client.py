from __future__ import annotations

from datetime import date, timedelta
from calendar import monthrange

import httpx
import pandas as pd
import streamlit as st

from elhub.models import ElhubResponse, response_to_df

BASE_URL = "https://api.elhub.no/energy-data/v0"
DATASET = "INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY"


def _date_param(d: date) -> str:
    return f"{d.isoformat()}T00:00:00+02:00"


def _month_window(year: int, month: int) -> tuple[date, date]:
    """Return (first, last) day of a given month."""
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _fetch_municipalities(start: date, end: date) -> pd.DataFrame:
    """Raw fetch for all municipalities over a date range (max 1 month)."""
    params: dict[str, str] = {
        "dataset": DATASET,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    with httpx.Client(timeout=30) as client:
        r = client.get(f"{BASE_URL}/municipalities", params=params)
        r.raise_for_status()
    return response_to_df(ElhubResponse.model_validate(r.json()))


def _fetch_single_municipality(
    municipality_id: str, start: date, end: date
) -> pd.DataFrame:
    """Raw fetch for a single municipality. Returns empty DataFrame on 404."""
    params: dict[str, str] = {
        "dataset": DATASET,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    with httpx.Client(timeout=30) as client:
        r = client.get(
            f"{BASE_URL}/municipalities/{municipality_id}", params=params
        )
        if r.status_code == 404:
            return pd.DataFrame()
        r.raise_for_status()
    return response_to_df(ElhubResponse.model_validate(r.json()))


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_latest_snapshot() -> pd.DataFrame:
    """
    Fetch the most recent daily snapshot for all municipalities.
    Looks back up to 7 days to handle weekends / data lag.
    Stays within the 1-month API window.
    """
    today = date.today()
    start = today - timedelta(days=7)
    df = _fetch_municipalities(start, today)
    if df.empty:
        return df
    latest = df["usage_date"].max()
    return df[df["usage_date"] == latest].copy()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_history(municipality_id: str, months: int = 12) -> pd.DataFrame:
    """
    Fetch monthly history for a single municipality.
    Paginates strictly month by month to respect the 1-month API window.
    Returns one snapshot per month (last available day).
    """
    frames: list[pd.DataFrame] = []
    today = date.today()

    for i in range(months):
        # Step back i months from current month
        month = today.month - i
        year = today.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1

        start, end = _month_window(year, month)

        # Don't request future dates
        if start > today:
            continue
        end = min(end, today)

        df = _fetch_single_municipality(municipality_id, start, end)
        if not df.empty:
            latest_in_month = df["usage_date"].max()
            frames.append(df[df["usage_date"] == latest_in_month])

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
