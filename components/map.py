import folium
import pandas as pd
from branca.colormap import linear


PRODUCTION_COLORS = {
    "solar":   "#f4a523",
    "hydro":   "#1a6b8a",
    "wind":    "#5ba85a",
    "thermal": "#c0543a",
    "other":   "#8a7a9b",
    "total":   "#2d6a4f",
}


def build_choropleth(
    df: pd.DataFrame,
    geojson: dict,
    production_groups: list[str],
    metering_type: str,  # "E18", "E19", or "Both"
) -> folium.Map:
    """
    Build a folium choropleth map of installed capacity per municipality.
    """
    filtered = df.copy()

    if metering_type != "Both":
        filtered = filtered[filtered["metering_type"] == metering_type]

    if production_groups:
        filtered = filtered[filtered["production_group"].isin(production_groups)]

    agg = (
        filtered.groupby("municipality_id")["installed_capacity_kw"]
        .sum()
        .reset_index()
    )

    if agg.empty:
        m = folium.Map(location=[65, 15], zoom_start=5, tiles="CartoDB positron")
        return m

    max_val = agg["installed_capacity_kw"].max()
    color_key = "total" if len(production_groups) != 1 else production_groups[0]
    hex_color = PRODUCTION_COLORS.get(color_key, "#2d6a4f")

    colormap = linear.YlGn_09.scale(0, max_val)
    colormap.caption = "Installed capacity (kW)"

    # Patch colormap color to match production group
    # Use a single-hue scale derived from the group color
    capacity_lookup = dict(zip(agg["municipality_id"], agg["installed_capacity_kw"]))

    m = folium.Map(location=[65, 15], zoom_start=5, tiles="CartoDB positron")

    def style_fn(feature):
        muni_id = feature["properties"].get("kommunenummer", "")
        val = capacity_lookup.get(muni_id, 0)
        if val == 0:
            return {
                "fillColor": "#e8e8e8",
                "color": "#aaaaaa",
                "weight": 0.5,
                "fillOpacity": 0.4,
            }
        return {
            "fillColor": colormap(val),
            "color": "#ffffff",
            "weight": 0.5,
            "fillOpacity": 0.8,
        }

    def highlight_fn(feature):
        return {"weight": 2, "color": "#333333", "fillOpacity": 0.9}

    folium.GeoJson(
        geojson,
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["kommunenummer", "navn"],
            aliases=["Municipality ID:", "Name:"],
            localize=True,
        ),
    ).add_to(m)

    colormap.add_to(m)
    return m
