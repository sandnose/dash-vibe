from __future__ import annotations

import pandas as pd

from elhub.aggregator import aggregate_time, auto_scale_unit


def _make_df(values: list[float], timestamps: list[str], group: str = "hydro") -> pd.DataFrame:
    return pd.DataFrame({
        "time": pd.to_datetime(timestamps),
        "quantityKwh": values,
        "productionGroup": group,
    })


def test_auto_scale_kwh_stays_kwh() -> None:
    df = _make_df([100.0, 200.0], ["2023-01-01", "2023-01-02"])
    result, unit = auto_scale_unit(df, "quantityKwh", "kWh")
    assert unit == "kWh"
    assert result["quantityKwh"].iloc[0] == 100.0


def test_auto_scale_to_mwh() -> None:
    df = _make_df([5000.0, 8000.0], ["2023-01-01", "2023-01-02"])
    result, unit = auto_scale_unit(df, "quantityKwh", "kWh")
    assert unit == "MWh"
    assert abs(result["quantityKwh"].iloc[0] - 5.0) < 0.001


def test_auto_scale_to_gwh() -> None:
    df = _make_df([5_000_000.0], ["2023-01-01"])
    _result, unit = auto_scale_unit(df, "quantityKwh", "kWh")
    assert unit == "GWh"


def test_auto_scale_kw_unchanged() -> None:
    df = _make_df([5_000_000.0], ["2023-01-01"])
    result, unit = auto_scale_unit(df, "quantityKwh", "kW")
    assert unit == "kW"
    assert result["quantityKwh"].iloc[0] == 5_000_000.0


def test_aggregate_time_daily() -> None:
    df = _make_df(
        [10.0] * 24,
        [f"2023-01-01 {h:02d}:00:00" for h in range(24)],
    )
    result = aggregate_time(df, "time", "quantityKwh", ["productionGroup"], "day")
    assert len(result) == 1
    assert abs(result["quantityKwh"].iloc[0] - 240.0) < 0.001


def test_aggregate_time_hour_passthrough() -> None:
    df = _make_df([10.0, 20.0], ["2023-01-01 00:00:00", "2023-01-01 01:00:00"])
    result = aggregate_time(df, "time", "quantityKwh", ["productionGroup"], "hour")
    assert len(result) == 2


def test_aggregate_time_empty_df() -> None:
    df = pd.DataFrame(columns=["time", "quantityKwh", "productionGroup"])
    result = aggregate_time(df, "time", "quantityKwh", ["productionGroup"], "day")
    assert result.empty
