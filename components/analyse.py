from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.theme import CHART_LAYOUT
from elhub.aggregator import (
    AGGREGATION_LABELS,
    aggregate_time,
    auto_scale_unit,
    theoretical_max_production,
)
from elhub.client import fetch_latest_snapshot, fetch_volume
from elhub.datasets import (
    CONSUMPTION_PER_GROUP_MBA_HOUR,
    CONSUMPTION_PER_GROUP_MUNICIPALITY_HOUR,
    EXCHANGE_PER_MBA_HOUR,
    LOSS_PER_MBA_HOUR,
    PRODUCTION_PER_GROUP_MBA_HOUR,
    PRODUCTION_PER_TYPE_MUNICIPALITY_HOUR,
    DatasetConfig,
)
from elhub.labels import (
    ANALYSE_TYPE_LABELS,
    label_consumption_group,
    label_production_group,
)

PRODUCTION_COLORS: dict[str, str] = {
    "solar": "#f4a523",
    "hydro": "#1a6b8a",
    "wind": "#5ba85a",
    "thermal": "#c0543a",
    "other": "#8a7a9b",
}

CONSUMPTION_COLORS: dict[str, str] = {
    "household": "#2d6a4f",
    "cabin": "#52b788",
    "primary": "#b7e4c7",
    "secondary": "#1b4332",
    "tertiary": "#40916c",
    "industry": "#1b4332",
    "private": "#52b788",
    "business": "#40916c",
}

# Maps geo level to available analyse types
GEO_LEVEL_ANALYSE_TYPES: dict[str, list[str]] = {
    "price-areas": ["production", "consumption", "exchange", "loss"],
    "municipalities": ["production", "consumption"],
}

# Maps (geo_level, analyse_type) to dataset config
ANALYSE_DATASET_MAP: dict[tuple[str, str], DatasetConfig] = {
    ("price-areas", "production"): PRODUCTION_PER_GROUP_MBA_HOUR,
    ("price-areas", "consumption"): CONSUMPTION_PER_GROUP_MBA_HOUR,
    ("price-areas", "exchange"): EXCHANGE_PER_MBA_HOUR,
    ("price-areas", "loss"): LOSS_PER_MBA_HOUR,
    ("municipalities", "production"): PRODUCTION_PER_TYPE_MUNICIPALITY_HOUR,
    ("municipalities", "consumption"): CONSUMPTION_PER_GROUP_MUNICIPALITY_HOUR,
}


def render_analyse_tab(
    geo_level: str,
    all_price_areas: list[str],
    all_municipalities: pd.DataFrame,
) -> None:
    """Render the full Analyse tab with controls and chart."""

    available_types = GEO_LEVEL_ANALYSE_TYPES.get(geo_level, [])
    if not available_types:
        st.info("Ingen analysedata tilgjengelig for dette geografiske nivået.")
        return

    col_controls, col_chart = st.columns([1, 3])

    with col_controls:
        # Analyse type selector
        analyse_type = st.selectbox(
            "Type analyse",
            options=available_types,
            format_func=lambda x: ANALYSE_TYPE_LABELS.get(x, x),
        )

        dataset = ANALYSE_DATASET_MAP[(geo_level, analyse_type)]

        # Entity selector
        if geo_level == "price-areas":
            entity_options = ["Alle", *all_price_areas]
            entity_label = st.selectbox("Prisområde", options=entity_options)
            entity_id = None if entity_label == "Alle" else entity_label
        else:
            entity_name = st.selectbox(
                "Kommune",
                options=all_municipalities["municipality_name"].tolist(),
            )
            entity_id = all_municipalities.loc[
                all_municipalities["municipality_name"] == entity_name,
                "municipality_id",
            ].values[0]

        # Date range
        st.markdown("**Periode**")
        col_fra, col_til = st.columns(2)
        with col_fra:
            start = st.date_input("Fra", value=date.today().replace(day=1))
        with col_til:
            end = st.date_input("Til", value=date.today())

        # Aggregation
        agg_options = _valid_aggregations(dataset.resolution)
        aggregation = st.selectbox(
            "Aggreger per",
            options=agg_options,
            format_func=lambda x: AGGREGATION_LABELS.get(x, x),
        )

        # Theoretical max toggle (production + price area only)
        show_theoretical = False
        if analyse_type == "production" and geo_level == "price-areas":
            show_theoretical = st.toggle(
                "Vis teoretisk maks (100% kapasitetsfaktor)",
                value=False,
            )

        load = st.button("Last inn data", type="primary")

    with col_chart:
        if not load:
            st.info("Velg parametere og klikk **Last inn data**.")
            return

        with st.spinner("Henter data…"):
            df = fetch_volume(dataset.id, geo_level, start, end, entity_id)

        if df.empty:
            st.info("Ingen data funnet for valgte parametere.")
            return

        # Aggregate time
        group_col = _group_col_for(analyse_type, geo_level)
        df = aggregate_time(df, "time", dataset.value_field, [group_col], aggregation)

        # Scale units
        df, unit = auto_scale_unit(df, dataset.value_field, dataset.unit)

        title = _chart_title(analyse_type, entity_label if geo_level == "price-areas" else entity_name)

        if analyse_type == "exchange":
            fig = _exchange_chart(df, unit, title)
        elif analyse_type == "loss":
            fig = _loss_chart(df, unit, title)
        elif analyse_type == "production":
            fig = _production_chart(df, group_col, dataset.value_field, unit, title)
            if show_theoretical:
                _add_theoretical_max(fig, start, end, entity_id, unit)
        else:
            fig = _consumption_chart(df, group_col, dataset.value_field, unit, title)

        st.plotly_chart(fig, use_container_width=True)

        # Disclosure for municipality consumption groups
        if analyse_type == "consumption" and geo_level == "municipalities":
            st.caption(
                "ℹ️ Forbruksgrupper på kommunenivå er grovere enn på prisområdenivå. "
                "Elhub aggregerer til industri, privat og næringsliv for kommunedata."
            )


def _valid_aggregations(resolution: str) -> list[str]:
    """Return valid aggregation options based on dataset resolution."""
    if resolution in ("hourly", "15min"):
        return ["hour", "day", "month", "year"]
    elif resolution == "daily":
        return ["day", "month", "year"]
    return ["month", "year"]


def _group_col_for(analyse_type: str, geo_level: str) -> str:
    if analyse_type == "production":
        return "productionGroup" if geo_level == "price-areas" else "meteringPointTypeCode"
    elif analyse_type == "consumption":
        return "consumptionGroup"
    return "entity_id"


def _chart_title(analyse_type: str, entity: str) -> str:
    type_label = ANALYSE_TYPE_LABELS.get(analyse_type, analyse_type)
    return f"{type_label} — {entity}"


def _production_chart(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    unit: str,
    title: str,
) -> go.Figure:
    df = df.copy()
    df["gruppe"] = df[group_col].map(label_production_group)
    fig = px.bar(
        df,
        x="time",
        y=value_col,
        color="gruppe",
        color_discrete_map={label_production_group(k): v for k, v in PRODUCTION_COLORS.items()},
        labels={"time": "", value_col: f"Produksjon ({unit})", "gruppe": "Produksjonstype"},
        title=title,
    )
    fig.update_layout(**CHART_LAYOUT, legend_title_text="", barmode="stack")
    return fig


def _add_theoretical_max(
    fig: go.Figure,
    start: date,
    end: date,
    entity_id: str | None,
    unit: str,
) -> None:
    """Overlay theoretical max production line from installed capacity snapshot."""
    snapshot = fetch_latest_snapshot()
    if snapshot.empty:
        return

    hours = int((pd.Timestamp(end) - pd.Timestamp(start)).total_seconds() / 3600)
    theo = theoretical_max_production(snapshot, hours)

    # Scale to match current unit
    scale = {"kWh": 1, "MWh": 1_000, "GWh": 1_000_000, "TWh": 1_000_000_000}.get(unit, 1)
    theo["theoretical_max_kwh"] = theo["theoretical_max_kwh"] / scale

    total_theo = theo["theoretical_max_kwh"].sum()
    fig.add_hline(
        y=total_theo,
        line_dash="dot",
        line_color="#333333",
        annotation_text=f"Teoretisk maks ({unit})",
        annotation_position="right",
    )


def _consumption_chart(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    unit: str,
    title: str,
) -> go.Figure:
    df = df.copy()
    df["gruppe"] = df[group_col].map(label_consumption_group)
    fig = px.bar(
        df,
        x="time",
        y=value_col,
        color="gruppe",
        color_discrete_map={label_consumption_group(k): v for k, v in CONSUMPTION_COLORS.items()},
        labels={"time": "", value_col: f"Forbruk ({unit})", "gruppe": "Forbruksgruppe"},
        title=title,
    )
    fig.update_layout(**CHART_LAYOUT, legend_title_text="", barmode="stack")
    return fig


def _exchange_chart(df: pd.DataFrame, unit: str, title: str) -> go.Figure:
    fig = go.Figure()
    if "exchangeInQuantityKwh" in df.columns:
        fig.add_trace(go.Bar(
            x=df["time"], y=df["exchangeInQuantityKwh"],
            name="Import", marker_color="#1a6b8a",
        ))
    if "exchangeOutQuantityKwh" in df.columns:
        fig.add_trace(go.Bar(
            x=df["time"], y=-df["exchangeOutQuantityKwh"],
            name="Eksport", marker_color="#c0543a",
        ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=title,
        barmode="relative",
        yaxis_title=f"Mengde ({unit})",
        xaxis_title="",
        legend_title_text="",
    )
    return fig


def _loss_chart(df: pd.DataFrame, unit: str, title: str) -> go.Figure:
    fig = px.area(
        df,
        x="time",
        y=df.columns[df.columns.str.contains("loss", case=False)][0] if any(
            df.columns.str.contains("loss", case=False)
        ) else df.columns[-1],
        labels={"time": "", "y": f"Nettap ({unit})"},
        title=title,
        color_discrete_sequence=["#8a7a9b"],
    )
    fig.update_layout(**CHART_LAYOUT)
    return fig
