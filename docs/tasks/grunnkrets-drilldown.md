# Task: Grunnkrets drill-down from municipality map click

## Overview
When a user clicks a municipality polygon on the Kart tab, show a drill-down
choropleth of that municipality's installed capacity broken down by grunnkrets
(basic statistical unit / BSU).

This is a two-phase feature. Both phases should be separate PRs.

---

## Phase 1 — Preprocess grunnkrets GeoJSON (backend PR)

### Goal
Convert the bulk Kartverket GeoJSON into per-municipality files joinable
against Elhub BSU data.

### Input
`data/raw/grunnkretser.zip` — Kartverket "Statistiske enheter grunnkretser",
EUREF89 UTM sone 33 (EPSG:25833). See `data/raw/README.md`.

### Output
`data/grunnkretser/{kommunenummer}.geojson` — one file per municipality,
WGS84 (EPSG:4326), gitignored (generated at build time).

### Script to write
`scripts/build_grunnkretser.py` — run once, or via `just build-grunnkretser`.

Pseudocode:
```python
import geopandas as gpd, zipfile, json
from pathlib import Path

with zipfile.ZipFile("data/raw/grunnkretser.zip") as z:
    geojson_name = [f for f in z.namelist() if f.endswith(".geojson")][0]
    gdf = gpd.read_file(z.open(geojson_name))

# IMPORTANT: inspect gdf.columns and gdf.head() first to confirm exact field names
# Expected: grunnkretsnummer (8-digit), grunnkretsnavn (name)

gdf = gdf.to_crs(epsg=4326)

Path("data/grunnkretser").mkdir(exist_ok=True)
for kommunenummer, group in gdf.groupby(gdf["grunnkretsnummer"].str[:4]):
    group.to_file(f"data/grunnkretser/{kommunenummer}.geojson", driver="GeoJSON")
```

### Add to justfile
```
# Build per-municipality grunnkrets GeoJSON from raw source (run once)
build-grunnkretser:
    uv run python scripts/build_grunnkretser.py
```

### Add to dev dependencies
Add `geopandas` to `[project.optional-dependencies] dev` in `pyproject.toml`.

### CRITICAL — verify name matching before proceeding to Phase 2
After building, check Oslo (0301) against known Elhub BSU names:

```python
import geopandas as gpd
gdf = gpd.read_file("data/grunnkretser/0301.geojson")
print(gdf["grunnkretsnavn"].sort_values().tolist())
```

Known Elhub names for Oslo to check against:
`"Ensjø sør"`, `"Maridalen"`, `"Lofsrud"`, `"Nydalen vest"`, `"Nedre Kaldbakken"`

If they do not match — stop. File an issue and do not proceed to Phase 2.

---

## Phase 2 — Drill-down map feature

### Prerequisites
- Phase 1 complete
- Name matching verified for Oslo (0301)

### Key facts about the Elhub BSU response
Verified from actual API response for Oslo:
- Field name is `basicStatisticalUnit` — a **name string** (e.g. `"Ensjø sør"`)
- There is NO numeric BSU ID in the response
- Some records have no `basicStatisticalUnit` field — these are unassigned metering
  points. Skip them silently, do not crash.
- Join to GeoJSON is: Elhub `basicStatisticalUnit` ↔ GeoJSON `grunnkretsnavn`

### `elhub/models.py` — BSU models
```python
class BsuCapacityRecord(BaseModel):
    usageDateId: int
    municipalityId: str
    basicStatisticalUnit: str | None = None  # name string; None = unassigned
    meteringPointTypeCode: str
    productionGroup: str
    installedCapacity: float
    lastUpdatedTime: str

class MunicipalityBsuAttributes(BaseModel):
    municipalityNumber: str
    name: str
    nameNo: str
    installedCapacityPerMeteringPointTypeGroupMunicipalityBasicStatisticalUnitDaily: list[BsuCapacityRecord]

class MunicipalityBsu(BaseModel):
    type: str
    id: str
    attributes: MunicipalityBsuAttributes

class ElhubBsuResponse(BaseModel):
    data: list[MunicipalityBsu]

def bsu_response_to_df(response: ElhubBsuResponse) -> pd.DataFrame:
    rows: list[dict] = []
    for muni in response.data:
        attrs = muni.attributes
        for record in attrs.installedCapacityPerMeteringPointTypeGroupMunicipalityBasicStatisticalUnitDaily:
            if record.basicStatisticalUnit is None:
                continue  # skip unassigned records
            rows.append({
                "municipality_id": attrs.municipalityNumber,
                "municipality_name": attrs.nameNo,
                "bsu_name": record.basicStatisticalUnit,
                "usage_date": pd.to_datetime(str(record.usageDateId), format="%Y%m%d"),
                "metering_type": record.meteringPointTypeCode,
                "production_group": record.productionGroup,
                "installed_capacity_kw": record.installedCapacity,
            })
    return pd.DataFrame(rows)
```

### `elhub/client.py` — BSU snapshot fetch
```python
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bsu_snapshot(municipality_id: str) -> pd.DataFrame:
    today = date.today()
    raw = _fetch_raw(
        "municipalities",
        INSTALLED_CAPACITY_MUNICIPALITY_BSU.id,
        today - timedelta(days=7),
        today,
        entity_id=municipality_id,
    )
    if not raw.get("data"):
        return pd.DataFrame()
    df = bsu_response_to_df(ElhubBsuResponse.model_validate(raw))
    if df.empty:
        return df
    return df[df["usage_date"] == df["usage_date"].max()].copy()
```

### `elhub/geo.py` — BSU GeoJSON loader
```python
@st.cache_data(ttl=86400, show_spinner=False)
def load_bsu_geojson(municipality_id: str) -> dict | None:
    path = Path(f"data/grunnkretser/{municipality_id}.geojson")
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)
```

### `components/map.py` — click detection and BSU choropleth

**Click detection — use `last_object_clicked`, NOT popup HTML or regex:**
```python
# Add to returned_objects in st_folium call:
returned_objects=["center", "zoom", "last_object_clicked"]

# Read click:
clicked = map_state.get("last_object_clicked") or {}
muni_id = (clicked.get("properties") or {}).get("kommunenummer")
if muni_id and not filter_changed:
    st.session_state["selected_municipality_id"] = muni_id
```

**BSU choropleth builder:**
```python
def build_bsu_choropleth(
    bsu_df: pd.DataFrame,
    bsu_geojson: dict,
) -> folium.Map:
    agg = (
        bsu_df.groupby("bsu_name")["installed_capacity_kw"]
        .sum()
        .reset_index()
    )
    capacity_exact: dict[str, float] = dict(
        zip(agg["bsu_name"], agg["installed_capacity_kw"], strict=False)
    )
    capacity_lower: dict[str, float] = {
        k.strip().lower(): v for k, v in capacity_exact.items()
    }

    max_val = float(agg["installed_capacity_kw"].max()) if not agg.empty else 1.0
    colormap = LinearColormap(
        colors=["#eaf4fb", "#9ecae1", "#3182bd", "#08519c", "#08306b"],
        vmin=0, vmax=max_val,
        caption="Installert kapasitet (kW)",
    )

    # Centre on bounding box of all features
    import geopandas as gpd
    gdf = gpd.GeoDataFrame.from_features(bsu_geojson["features"])
    bounds = gdf.total_bounds
    center = ((bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2)

    m = folium.Map(
        location=center, zoom_start=11,
        tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        attr="&copy; OpenStreetMap &copy; CARTO",
    )

    def style_fn(feature: dict) -> dict:
        name: str = feature["properties"].get("grunnkretsnavn", "")
        val = capacity_exact.get(name, capacity_lower.get(name.strip().lower(), 0.0))
        if val == 0.0:
            return {"fillColor": "#e8e8e8", "color": "#cccccc", "weight": 0.5, "fillOpacity": 0.4}
        return {"fillColor": colormap(val), "color": "#ffffff", "weight": 0.8, "fillOpacity": 0.8}

    folium.GeoJson(
        bsu_geojson,
        style_function=style_fn,
        zoom_on_click=False,
        tooltip=folium.GeoJsonTooltip(
            fields=["grunnkretsnavn"],
            aliases=["Grunnkrets:"],
        ),
    ).add_to(m)
    colormap.add_to(m)
    return m
```

### `app.py` — wire everything together
After existing map state writes, still inside `with col_map:`:
```python
if not filter_changed:
    clicked = map_state.get("last_object_clicked") or {}
    muni_id = (clicked.get("properties") or {}).get("kommunenummer")
    if muni_id:
        st.session_state["selected_municipality_id"] = muni_id

selected_id = st.session_state.get("selected_municipality_id")
if selected_id:
    muni_name = _muni_name_lookup.get(selected_id, selected_id)
    st.divider()
    st.markdown(f"#### Grunnkretser — {muni_name}")
    st.caption(
        "Installert kapasitet per grunnkrets. "
        "Ikke alle kommuner har grunnkretsdata tilgjengelig."
    )
    bsu_geojson = load_bsu_geojson(selected_id)
    if bsu_geojson is None:
        st.info(f"Ingen grunnkretsdata tilgjengelig for {muni_name}.")
    else:
        with st.spinner(f"Laster grunnkretsdata for {muni_name}…"):
            bsu_df = fetch_bsu_snapshot(selected_id)
        if bsu_df.empty:
            st.info(f"Elhub har ingen BSU-data for {muni_name}.")
        else:
            bsu_map = build_bsu_choropleth(bsu_df, bsu_geojson)
            st_folium(bsu_map, use_container_width=True, height=500, returned_objects=[])
```

---

## Tests to add
- `BsuCapacityRecord` parses with `None` basicStatisticalUnit
- `bsu_response_to_df` skips records where basicStatisticalUnit is None
- `fetch_bsu_snapshot` returns empty DataFrame on 404

## Documentation to update (required — see documentation contract)
- `CLAUDE.md` — repo structure: add `scripts/`, BSU models in `elhub/models.py`
- `DESIGN.md` — BSU choropleth uses same blue sequential colormap as main map
- `TESTING.md` — add BSU drill-down checklist under Kart tab
- `skills/elhub.md` — add BSU dataset schema
