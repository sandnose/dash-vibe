from __future__ import annotations

import pandas as pd

# ── Unit scaling ───────────────────────────────────────────────────────────────

def auto_scale_unit(df: pd.DataFrame, value_col: str, base_unit: str) -> tuple[pd.DataFrame, str]:
    """
    Scale kWh values to MWh / GWh / TWh based on magnitude.
    Returns modified DataFrame and the new unit label.
    Only applies to kWh — kW (capacity) is never scaled.
    """
    if base_unit != "kWh" or df.empty:
        return df, base_unit

    max_val = df[value_col].abs().max()
    df = df.copy()

    if max_val >= 1_000_000_000:
        df[value_col] = df[value_col] / 1_000_000_000
        return df, "TWh"
    elif max_val >= 1_000_000:
        df[value_col] = df[value_col] / 1_000_000
        return df, "GWh"
    elif max_val >= 1_000:
        df[value_col] = df[value_col] / 1_000
        return df, "MWh"
    else:
        return df, "kWh"


# ── Time aggregation ───────────────────────────────────────────────────────────

AGGREGATION_LABELS: dict[str, str] = {
    "hour": "Per time",
    "day": "Per dag",
    "month": "Per måned",
    "year": "Per år",
}

AGGREGATION_FREQS: dict[str, str] = {
    "hour": "h",
    "day": "D",
    "month": "MS",
    "year": "YS",
}


def aggregate_time(
    df: pd.DataFrame,
    time_col: str,
    value_col: str,
    group_cols: list[str],
    aggregation: str,  # "hour" | "day" | "month" | "year"
) -> pd.DataFrame:
    """
    Resample a volume DataFrame to a coarser time resolution by summing.

    Args:
        df: Input DataFrame with a datetime time_col.
        time_col: Name of the datetime column.
        value_col: Name of the numeric value column to sum.
        group_cols: Additional columns to group by (e.g. production_group, geo_id).
        aggregation: Target resolution.
    """
    if df.empty or aggregation == "hour":
        return df

    freq = AGGREGATION_FREQS[aggregation]
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])

    agg_frames: list[pd.DataFrame] = []
    for keys, group in df.groupby(group_cols):
        resampled = (
            group.set_index(time_col)[value_col]
            .resample(freq)
            .sum()
            .reset_index()
        )
        if isinstance(keys, str):
            keys = (keys,)
        for col, val in zip(group_cols, keys, strict=False):
            resampled[col] = val
        agg_frames.append(resampled)

    if not agg_frames:
        return pd.DataFrame()

    return pd.concat(agg_frames, ignore_index=True)


# ── Theoretical max production ─────────────────────────────────────────────────

def theoretical_max_production(
    capacity_df: pd.DataFrame,
    hours: int,
    capacity_col: str = "installed_capacity_kw",
    group_col: str = "production_group",
    geo_col: str = "price_area_id",
) -> pd.DataFrame:
    """
    Calculate theoretical maximum production (kWh) from installed capacity (kW).
    Assumes 100% capacity factor: max_kwh = installed_kw * hours.

    Only valid when comparing at the same geographic level (price area).

    Args:
        capacity_df: Snapshot DataFrame with installed capacity in kW.
        hours: Number of hours in the analysis period.
        capacity_col: Column name for installed capacity.
        group_col: Column to group by (production group).
        geo_col: Column for geographic entity.
    """
    df = capacity_df.copy()
    df["theoretical_max_kwh"] = df[capacity_col] * hours
    return df.groupby([geo_col, group_col])["theoretical_max_kwh"].sum().reset_index()
