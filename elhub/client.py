from __future__ import annotations

from calendar import monthrange
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import httpx
import pandas as pd
import streamlit as st

from elhub.datasets import DATASETS_BY_ID, INSTALLED_CAPACITY_MUNICIPALITY, DatasetConfig
from elhub.models import ElhubResponse, response_to_df

BASE_URL = "https://api.elhub.no/energy-data/v0"


def _date_param(d: date) -> str:
    return f"{d.isoformat()}T00:00:00+02:00"


def _month_window(year: int, month: int) -> tuple[date, date]:
    """Return (first, last) day of a calendar month."""
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_raw(
    geo_level: str,
    dataset_id: str,
    start: date,
    end: date,
    entity_id: str | None = None,
) -> dict:
    """
    Generic raw fetch for any geo level and dataset.
    Returns empty data dict on 404. Raises on other errors.
    """
    url = f"{BASE_URL}/{geo_level}"
    if entity_id:
        url += f"/{entity_id}"
    params: dict[str, str] = {
        "dataset": dataset_id,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    with httpx.Client(timeout=30) as client:
        r = client.get(url, params=params)
    if r.status_code == 404:
        return {"data": []}
    r.raise_for_status()
    return r.json()


def _fetch_municipalities(start: date, end: date) -> pd.DataFrame:
    """Fetch all municipalities for the installed capacity snapshot dataset."""
    raw = _fetch_raw("municipalities", INSTALLED_CAPACITY_MUNICIPALITY.id, start, end)
    return response_to_df(ElhubResponse.model_validate(raw))


def _fetch_single_municipality(
    municipality_id: str, start: date, end: date
) -> pd.DataFrame:
    """Fetch a single municipality for the installed capacity snapshot dataset."""
    raw = _fetch_raw(
        "municipalities",
        INSTALLED_CAPACITY_MUNICIPALITY.id,
        start,
        end,
        entity_id=municipality_id,
    )
    return response_to_df(ElhubResponse.model_validate(raw))


# ── Snapshot fetchers ──────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_latest_snapshot() -> pd.DataFrame:
    """
    Fetch the most recent daily installed capacity snapshot for all municipalities.
    Looks back up to 7 days to handle weekends / data lag.
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
    Fetch monthly installed capacity history for a single municipality.
    Uses last day of each completed month as the target date; today-7 for
    the current partial month. Fetches in parallel (4 workers).
    """
    today = date.today()
    current_year, current_month = today.year, today.month

    windows: list[tuple[int, int, date, date, date]] = []
    for i in range(months):
        m = today.month - i
        y = today.year + (m - 1) // 12
        m = ((m - 1) % 12) + 1

        if y == current_year and m == current_month:
            target = today - timedelta(days=7)
        else:
            target = _month_window(y, m)[1]

        win_start = max(target - timedelta(days=2), date(y, m, 1))
        win_end = min(target + timedelta(days=2), today)
        windows.append((y, m, target, win_start, win_end))

    def _fetch_one(args: tuple[int, int, date, date, date]) -> pd.DataFrame | None:
        _y, _m, target, win_start, win_end = args
        try:
            df = _fetch_single_municipality(municipality_id, win_start, win_end)
            if df.empty:
                return None
            closest_idx = (df["usage_date"] - pd.Timestamp(target)).abs().idxmin()
            snap_date = df["usage_date"].iloc[closest_idx]
            return df[df["usage_date"] == snap_date].copy()
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(_fetch_one, windows))

    frames = [r for r in results if r is not None and not r.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ── Volume fetchers ────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_volume(
    dataset_id: str,
    geo_level: str,
    start: date,
    end: date,
    entity_id: str | None = None,
) -> pd.DataFrame:
    """
    Fetch a volume dataset (production, consumption, exchange, loss).
    Paginates by calendar month if date range exceeds max window.
    Returns a flat DataFrame with columns driven by dataset response.

    Args:
        dataset_id: Elhub dataset name constant.
        geo_level: "municipalities" or "price-areas".
        start: Start date (inclusive).
        end: End date (inclusive).
        entity_id: Optional specific entity (municipality ID or price area ID).
    """
    dataset = DATASETS_BY_ID[dataset_id]

    windows: list[tuple[date, date]] = []
    current = start
    while current <= end:
        month_last = date(current.year, current.month, monthrange(current.year, current.month)[1])
        window_end = min(month_last, end)
        windows.append((current, window_end))
        if month_last >= end:
            break
        current = month_last + timedelta(days=1)

    def _fetch_window(args: tuple[date, date]) -> pd.DataFrame | None:
        w_start, w_end = args
        try:
            raw = _fetch_raw(geo_level, dataset_id, w_start, w_end, entity_id)
            df = _flatten_volume_response(raw, dataset, geo_level)
            return df if not df.empty else None
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(_fetch_window, windows))

    frames = [r for r in results if r is not None and not r.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _flatten_volume_response(
    raw: dict,
    dataset: DatasetConfig,
    geo_level: str,
) -> pd.DataFrame:
    """
    Flatten a raw volume API response into a tidy DataFrame.
    Handles varying response schemas across dataset types.
    """
    rows: list[dict] = []

    for entity in raw.get("data", []):
        entity_id = entity.get("id", "")
        attrs = entity.get("attributes", {})

        # Find the nested records list — key varies by dataset
        records_key = _find_records_key(attrs)
        records: list[dict] = attrs.get(records_key, []) if records_key else [attrs]

        for record in records:
            row: dict = {
                "entity_id": entity_id,
                "geo_level": geo_level,
            }
            # Parse time fields
            for time_field in ("startTime", "endTime", "usageDateId"):
                if time_field in record:
                    if time_field == "usageDateId":
                        row["time"] = pd.to_datetime(str(record[time_field]), format="%Y%m%d")
                    else:
                        row["time"] = pd.to_datetime(record[time_field])
            # Extract all numeric and string fields
            for k, v in record.items():
                if k not in ("startTime", "endTime", "usageDateId", "lastUpdatedTime"):
                    row[k] = v
            rows.append(row)

    return pd.DataFrame(rows)


def _find_records_key(attrs: dict) -> str | None:
    """Find the key in attributes that holds the list of records."""
    for k, v in attrs.items():
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            return k
    return None
