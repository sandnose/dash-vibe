# Agent Onboarding Guide — dash-vibe

## Project overview
Interactive dashboard visualising open electricity datasets from [Elhub](https://api.elhub.no),
Norway's electricity data hub. Built with Streamlit + Folium + Plotly.

## Repo structure
```
dash-vibe/
├── app.py                  # Streamlit entrypoint — 3 tabs: Map, History, Leaders
├── elhub/
│   ├── client.py           # Elhub API client with st.cache_data caching
│   ├── models.py           # Pydantic models + DataFrame flattening
│   └── geo.py              # Norwegian municipality GeoJSON loader
├── components/
│   ├── map.py              # Folium choropleth builder
│   └── charts.py           # Plotly history + leaders charts
├── skills/
│   └── elhub.md            # Elhub API reference (read this first)
├── tests/                  # pytest test suite
├── justfile                # Task runner: just init / just run / just test / just check
└── TESTING.md              # Testing checklist (for test agent)
```

## How to run
```bash
git clone https://github.com/sandnose/dash-vibe
cd dash-vibe
just init
just run
```

## Key decisions & context
- **Data**: Elhub `INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY`
  — installed capacity (kW) per municipality, production group, metering type, daily
- **Production groups**: solar, hydro, wind, thermal, other
- **Metering types**: E18 (grid-scale), E19 (prosumers/small-scale)
- **GeoJSON**: robhop/fylker-og-kommuner `Kommuner-S.geojson` — WGS84, coastal-clipped
- **Map join key**: `kommunenummer` in GeoJSON ↔ `municipality_id` in DataFrame
- **API constraint**: max 1 month date window per request — history tab paginates month by month
- **No auth required** for Elhub open datasets

## Agent roles

### 🧪 Test agent
See `TESTING.md`. Your job is to run the app, work through the checklist,
and file GitHub Issues for anything broken or degraded. Be specific: include
tab name, steps to reproduce, and what you expected vs what happened.

### 🎨 UX agent
(Not yet active.) Will focus on layout, visual consistency, and user experience
improvements across all three tabs.

### 🏗️ Architecture agent (this session)
Owns data logic, API client, models, and overall structure decisions.
