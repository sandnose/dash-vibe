from __future__ import annotations

import folium
import pandas as pd
from branca.colormap import LinearColormap, linear

PRODUCTION_COLORS: dict[str, str] = {
    "solar":   "#f4a523",
    "hydro":   "#1a6b8a",
    "wind":    "#5ba85a",
    "thermal": "#c0543a",
    "other":   "#8a7a9b",
    "total":   "#2d6a4f",
}


def _colormap(max_val: float) -> LinearColormap:
    return linear.YlGn_09.scale(0, max_val)


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

    m = folium.Map(location=[65, 15], zoom_start=5, tiles="CartoDB positron")

    if agg.empty:
        return m

    max_val = float(agg["installed_capacity_kw"].max())
    colormap = _colormap(max_val)
    colormap.caption = "Installed capacity (kW)"

    capacity_lookup: dict[str, float] = dict(
        zip(agg["municipality_id"], agg["installed_capacity_kw"], strict=False)
    )

    def style_fn(feature: dict) -> dict:
        muni_id: str = feature["properties"].get("kommunenummer", "")
        val: float = capacity_lookup.get(muni_id, 0.0)
        if val == 0.0:
            return {"fillColor": "#e8e8e8", "color": "#aaaaaa", "weight": 0.5, "fillOpacity": 0.4}
        return {"fillColor": colormap(val), "color": "#ffffff", "weight": 0.5, "fillOpacity": 0.8}

    def highlight_fn(_feature: dict) -> dict:
        return {"weight": 2, "color": "#333333", "fillOpacity": 0.9}

    folium.GeoJson(
        geojson,
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["kommunenummer", "kommunenavn"],
            aliases=["ID:", "Municipality:"],
            localize=True,
        ),
    ).add_to(m)

    colormap.add_to(m)
    return m
