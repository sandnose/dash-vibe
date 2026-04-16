# dash-vibe — Claude Code Context

## Project overview
Interactive dashboard visualising open electricity datasets from [Elhub](https://api.elhub.no),
Norway's electricity data hub. Built with Streamlit + Folium + Plotly.

**Repo:** `https://github.com/sandnose/dash-vibe`
**Owner:** sandnose (Christoffer)

## Current state (as of 2026-04-16)
- ✅ Map tab — choropleth of installed capacity per municipality, working
- ✅ History tab — monthly line chart per municipality, lazy-loaded with button
- ✅ Leaders tab — top N municipalities per production group
- ✅ Test suite — 14 passing tests (pytest)
- ✅ Linting — ruff configured
- 🔧 Active issues being tracked on GitHub Issues

## Stack
| Layer | Choice |
|---|---|
| Frontend | Streamlit |
| Maps | Folium + streamlit-folium |
| Charts | Plotly |
| Data fetching | httpx + st.cache_data |
| Geo data | robhop/fylker-og-kommuner GeoJSON (Kommuner-S.geojson) |
| Models | Pydantic v2 |
| Testing | pytest + pytest-httpx |
| Linting | ruff |
| Task runner | just |

## Repo structure
```
dash-vibe/
├── app.py                  # Streamlit entrypoint — 3 tabs: Map, History, Leaders
├── elhub/
│   ├── client.py           # API client, st.cache_data caching, month pagination
│   ├── models.py           # Pydantic models + DataFrame flattening
│   └── geo.py              # GeoJSON loader
├── components/
│   ├── map.py              # Folium choropleth
│   └── charts.py           # Plotly history + leaders charts
├── skills/
│   └── elhub.md            # Elhub API reference — read before touching data logic
├── tests/                  # pytest suite
├── CLAUDE.md               # This file — read first
├── AGENTS.md               # Agent roles and onboarding
├── TESTING.md              # Testing checklist
└── justfile                # just init / just run / just test / just lint / just check
```

## How to run
```bash
just init    # create venv + install deps
just run     # start app at localhost:8501
just test    # run pytest
just check   # lint + test
```

## Key data decisions
- **Dataset:** `INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY`
- **Unit:** installed capacity in kW
- **Production groups:** solar, hydro, wind, thermal, other
- **Metering types:** E18 (grid-scale), E19 (prosumers)
- **API constraint:** max 1 month per request — history tab paginates month by month
- **GeoJSON join key:** `kommunenummer` (4-digit string, zero-padded)
- **No auth required** for Elhub open datasets

## Architecture decisions (context for why things are the way they are)
- History tab uses a **Load button** (not auto-fetch) to avoid triggering 12 API calls on tab switch
- GeoJSON is fetched at runtime (not committed) — cached 24h via st.cache_data
- Snapshot always shows **latest available date** (looks back 7 days for data lag)
- Month pagination steps back calendar month by calendar month, never exceeding 1-month window
- Tile layer: CartoDB no-labels (URL-based) to keep map clean

## Agent roles

### 🏗️ Architecture agent (backend)
Owns: `elhub/`, `components/charts.py`, `app.py` data logic, `tests/`
Reads issues tagged `data` or `bug` with backend root cause.
Coordinates with frontend agent on component interfaces.

### 🎨 UX/Frontend agent
Owns: `app.py` layout, `components/map.py`, `components/charts.py` styling
Reads issues tagged `ux`.
Does not touch data fetching logic in `elhub/`.

### 🧪 Test agent
Runs the app and works through `TESTING.md`.
Files GitHub Issues using the PAT in `.env`.
Tags issues: `bug`, `ux`, or `data`.

## GitHub
- PAT stored in `.env` as `GITHUB_TOKEN` (gitignored)
- File issues at: `https://github.com/sandnose/dash-vibe/issues`
- Use `curl` with the PAT to create issues via GitHub API

## Conversation history summary
This project was planned and built in a single Claude chat session (claude.ai).
Key decisions made together with Christoffer:
- Chose Streamlit for free hosting on Streamlit Community Cloud
- Chose folium over Plotly maps for lighter weight
- Dropped count-of-metering-points toggle (not in this dataset)
- E18/E19 toggle kept as meaningful split (grid vs prosumer scale)
- Log scale rejected in favour of keeping UX simple
- Snapshot-only map (no date picker) since installed capacity is slow-changing
- History tab shows development over time per municipality
- Leaders tab shows top N per production group
