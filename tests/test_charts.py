from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from components.charts import history_chart, leaders_chart

SNAPSHOT_DF = pd.DataFrame(
    {
        "municipality_id": ["0301", "0301", "1122"],
        "municipality_name": ["Oslo", "Oslo", "Gjesdal"],
        "usage_date": pd.to_datetime(["2023-05-03", "2023-05-03", "2023-05-03"]),
        "metering_type": ["E18", "E19", "E18"],
        "production_group": ["hydro", "solar", "solar"],
        "installed_capacity_kw": [10000.0, 500.0, 2000.0],
    }
)

HISTORY_DF = pd.DataFrame(
    {
        "municipality_id": ["0301"] * 4,
        "municipality_name": ["Oslo"] * 4,
        "usage_date": pd.to_datetime(
            ["2023-02-28", "2023-03-31", "2023-04-30", "2023-05-03"]
        ),
        "metering_type": ["E18"] * 4,
        "production_group": ["hydro"] * 4,
        "installed_capacity_kw": [9000.0, 9500.0, 10000.0, 10000.0],
    }
)


def test_history_chart_returns_figure() -> None:
    fig = history_chart(HISTORY_DF, "Oslo")
    assert isinstance(fig, go.Figure)


def test_history_chart_title() -> None:
    fig = history_chart(HISTORY_DF, "Oslo")
    assert "Oslo" in fig.layout.title.text


def test_leaders_chart_returns_figure() -> None:
    fig = leaders_chart(SNAPSHOT_DF, "solar", top_n=5)
    assert isinstance(fig, go.Figure)


def test_leaders_chart_filters_group() -> None:
    fig = leaders_chart(SNAPSHOT_DF, "hydro", top_n=5)
    # Only Oslo has hydro — chart should have 1 bar
    assert len(fig.data[0].y) == 1


def test_leaders_chart_top_n() -> None:
    # Both Oslo and Gjesdal have solar
    fig = leaders_chart(SNAPSHOT_DF, "solar", top_n=1)
    assert len(fig.data[0].y) == 1
