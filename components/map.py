from __future__ import annotations

import branca
import folium
import numpy as np
import pandas as pd
from branca.colormap import LinearColormap


def _build_colormap(max_val: float) -> LinearColormap:
    """
    Perceptually uniform blue-green sequential colormap.
    Avoids yellow/green which clashes with dashboard theme.
    """
    colormap = LinearColormap(
        colors=["#eaf4fb", "#9ecae1", "#3182bd", "#08519c", "#08306b"],
        vmin=0,
        vmax=max_val,
        caption="Installed capacity (kW)",
    )
    # Reduce to 5 clean ticks to avoid overlap
    ticks = np.linspace(0, max_val, 5)
    colormap.tick_labels = [f"{int(v):,}" for v in ticks]
    return colormap


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

    # Base layer without labels, so our overlay doesn't obscure city names
    m = folium.Map(
        location=[65, 15],
        zoom_start=5,
        tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        attr="&copy; OpenStreetMap &copy; CARTO",
    )

    if not agg.empty:
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

        folium.GeoJson(
            geojson,
            style_function=style_fn,
            highlight_function=lambda _: {},  # disable click/hover highlight box
            tooltip=folium.GeoJsonTooltip(
                fields=["kommunenummer", "kommunenavn"],
                aliases=["ID:", "Municipality:"],
                localize=True,
            ),
        ).add_to(m)

        colormap.add_to(m)

    # Label layer rendered on top so city names are always visible
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png",
        attr="&copy; OpenStreetMap &copy; CARTO",
        overlay=True,
        name="Labels",
        control=False,
    ).add_to(m)

    return m
