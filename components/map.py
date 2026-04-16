from __future__ import annotations

import folium
import pandas as pd
from branca.colormap import LinearColormap


def _build_colormap(max_val: float) -> LinearColormap:
    """Perceptually uniform blue sequential colormap."""
    return LinearColormap(
        colors=["#eaf4fb", "#9ecae1", "#3182bd", "#08519c", "#08306b"],
        vmin=0,
        vmax=max_val,
        caption="Installed capacity (kW)",
    )


def build_choropleth(
    df: pd.DataFrame,
    geojson: dict,
    production_groups: list[str],
    metering_type: str,  # "E18", "E19", or "Both"
) -> folium.Map:
    """
    Build a folium choropleth of installed capacity (kW) per municipality.

    Args:
        df: Snapshot DataFrame from fetch_latest_snapshot().
        geojson: Norwegian municipality GeoJSON (robhop/fylker-og-kommuner).
        production_groups: List of production groups to include.
        metering_type: "E18", "E19", or "Both".
    """
    filtered = df.copy()

    if metering_type != "Both":
        filtered = filtered[filtered["metering_type"] == metering_type]

    if production_groups:
        filtered = filtered[filtered["production_group"].isin(production_groups)]

    agg: pd.DataFrame = (
        filtered.groupby("municipality_id")["installed_capacity_kw"]
        .sum()
        .reset_index()
    )

    m = folium.Map(
        location=[68, 15],
        zoom_start=4,
        tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> &copy; <a href='https://carto.com/'>CARTO</a>",
    )

    if agg.empty:
        return m

    max_val = float(agg["installed_capacity_kw"].max())
    colormap = _build_colormap(max_val)

    capacity_lookup: dict[str, float] = dict(
        zip(agg["municipality_id"], agg["installed_capacity_kw"], strict=False)
    )

    def style_fn(feature: dict) -> dict:
        muni_id: str = feature["properties"].get("kommunenummer", "")
        val: float = capacity_lookup.get(muni_id, 0.0)
        if val == 0.0:
            return {
                "fillColor": "#e8e8e8",
                "color": "#cccccc",
                "weight": 0.5,
                "fillOpacity": 0.4,
            }
        return {
            "fillColor": colormap(val),
            "color": "#ffffff",
            "weight": 0.5,
            "fillOpacity": 0.75,
        }

    def highlight_fn(_feature: dict) -> dict:
        return {"weight": 2, "color": "#333333", "fillOpacity": 0.85}

    folium.GeoJson(
        geojson,
        style_function=style_fn,
        highlight_function=highlight_fn,
        zoom_on_click=False,
        tooltip=folium.GeoJsonTooltip(
            fields=["kommunenummer", "kommunenavn"],
            aliases=["ID:", "Municipality:"],
            localize=True,
        ),
    ).add_to(m)

    colormap.add_to(m)
    return m
