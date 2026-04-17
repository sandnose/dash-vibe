# dash-vibe — Claude Code Context

## Documentation contract

**Any agent that changes the app must update the relevant docs in the same PR.**

| What changed | What to update |
|---|---|
| App layout, navigation, new tab/mode | `CLAUDE.md`, `TESTING.md`, `AGENTS.md` (e2e refs), `tests/e2e/` |
| New component or design pattern | `DESIGN.md`, `CLAUDE.md` repo structure |
| New dataset or API endpoint | `skills/elhub.md` |
| New label or Norwegian translation | `elhub/labels.py` + `DESIGN.md` label table |
| Architecture decision | `CLAUDE.md` architecture decisions section |
| Agent role or workflow change | `AGENTS.md` |

Docs that are out of sync with the code are worse than no docs — they actively mislead other agents.
PRs that change behaviour without updating docs will be sent back.

---

## Quick start for all agents
1. Read this file fully
2. Read `DESIGN.md` before touching anything visual
3. Read `skills/elhub.md` before touching any API or data logic
4. Run `git branch --show-current` + `git status` — verify you are on your own branch
5. Check open GitHub Issues before starting work
6. Never push directly to main — branch and open a PR

---

## Project overview
Interactive dashboard visualising open electricity datasets from [Elhub](https://api.elhub.no),
Norway's electricity data hub. Built with Streamlit + Folium + Plotly.

**Repo:** `https://github.com/sandnose/dash-vibe`
**Owner:** sandnose (Christoffer)

---

## Current state
- ✅ **Navigation:** sidebar mode switch (Kapasitet / Volum) + tabs per mode
- ✅ **Kapasitet mode** — Kart, Historikk, Topp kommuner, Forklaring
  - Choropleth map of installed capacity per municipality
  - History: auto-fetching line chart per municipality (up to 60 months)
  - Leaders: top N municipalities per production group
- ✅ **Volum mode** — Analyse, Forklaring
  - Production, consumption, exchange, loss
  - Geographic level selector: Prisområde / Kommune
  - Time aggregation: per time / dag / måned / år
  - Auto unit scaling: kWh → MWh → GWh → TWh
  - Theoretical max production overlay (price area + production only)
- ✅ Dataset registry — `elhub/datasets.py` drives all client and UI logic
- ✅ Norwegian UI — all labels via `elhub/labels.py`, never raw API codes
- ✅ Central theme — `components/theme.py` + `DESIGN.md`
- ✅ Map preserves pan/zoom across filter changes via `st.session_state`
- ✅ Test suite — 27 passing unit tests
- ✅ Linting — ruff configured
- ✅ Playwright e2e tests — `tests/e2e/`
- 🔧 Active issues on GitHub Issues

---

## Stack
| Layer | Choice |
|---|---|
| Frontend | Streamlit |
| Maps | Folium + streamlit-folium |
| Charts | Plotly Express |
| Data fetching | httpx + `st.cache_data` |
| Geo data | robhop/fylker-og-kommuner (`Kommuner-S.geojson`) |
| Models | Pydantic v2 |
| Testing | pytest + pytest-httpx + Playwright |
| Linting | ruff |
| Task runner | just |

---

## Repo structure
```
dash-vibe/
├── app.py                  # Streamlit entrypoint — sidebar nav + tabs per mode
├── elhub/
│   ├── client.py           # Generic API client — snapshot + volume fetchers, month pagination
│   ├── datasets.py         # Dataset registry — DatasetConfig for every supported dataset
│   ├── models.py           # Pydantic models for snapshot API response + DataFrame flattening
│   ├── aggregator.py       # Unit scaling (kWh→MWh/GWh/TWh) + time aggregation
│   ├── labels.py           # All Norwegian label mappings — use these, never hardcode
│   └── geo.py              # Norwegian municipality GeoJSON loader (cached 24h)
├── components/
│   ├── map.py              # Folium choropleth with pan/zoom state preservation
│   ├── charts.py           # Plotly history + leaders charts
│   ├── analyse.py          # Volum mode — production, consumption, exchange, loss
│   └── theme.py            # CHART_LAYOUT constant — import here, never redefine locally
├── skills/
│   └── elhub.md            # Elhub API reference — all datasets, date rules, schemas
├── tests/
│   ├── test_models.py
│   ├── test_client.py
│   ├── test_charts.py
│   ├── test_datasets.py
│   ├── test_aggregator.py
│   └── e2e/
│       ├── test_kapasitet.py
│       └── test_volum.py
├── CLAUDE.md               # This file — read first
├── AGENTS.md               # Agent roles, onboarding, worktree setup, PR workflow
├── DESIGN.md               # Design system — colors, typography, component patterns
├── TESTING.md              # Testing checklist for test agent
├── .env.example            # Copy to .env and add GITHUB_TOKEN
└── justfile                # just init / just run / just test / just test-e2e / just check
```

---

## How to run
```bash
just init       # create venv + install all deps including dev
just run        # start app at localhost:8501
just test       # run unit tests (excludes e2e)
just test-e2e   # run Playwright tests (requires app running)
just check      # lint + unit tests
just fmt        # auto-format with ruff
just fix        # auto-fix lint issues
```

---

## Key data decisions
- **Multiple datasets** supported via registry in `elhub/datasets.py`
- **Snapshot datasets** (kW) — installed capacity, daily resolution, show latest available date
- **Volume datasets** (kWh) — production, consumption, exchange, loss; hourly or 15min
- **API constraint:** max 1 month per request — client paginates automatically
- **GeoJSON join key:** `kommunenummer` in `Kommuner-S.geojson` ↔ `municipality_id` in DataFrame
- **No auth required** for any open dataset (suffix `_RESTRICTED` = not used)
- **Unit scaling:** automatic based on magnitude — agents should never hardcode units

---

## Terminology rules

**All Norwegian electricity terminology must be verified against official Elhub sources:**
- [elhub.no](https://www.elhub.no) — official portal
- [dok.elhub.no](https://dok.elhub.no) — technical documentation

Do not invent or guess Norwegian electricity terms. If unsure, check the source.

Known correct terms (verified):
| Correct | Wrong | Notes |
|---|---|---|
| målepunkt | målerpunkt | Official Elhub term |
| målepunkttype | målerpunktkategori | E18/E19 classification |
| plusspunkt | — | E19 consumer+producer |
| produksjon | — | E18 large-scale production |
| prisområde | — | NO1–NO5 price areas |

---

## Design system
- **Single source of truth:** `DESIGN.md` — read before touching anything visual
- **Chart layout:** always import `CHART_LAYOUT` from `components/theme.py`, never redefine locally
- **Norwegian labels:** always use functions/constants from `elhub/labels.py`
- **Dataset logic:** always use `elhub/datasets.py` registry, never hardcode dataset IDs

---

## Architecture decisions
- **Sidebar mode switch** separates fundamentally different data types:
  - Kapasitet (kW) → snapshot, map-friendly, slow-changing
  - Volum (kWh) → time series, aggregation-driven, fast-changing
- **History auto-fetches** — no load button needed (single municipality, predictable cost)
- **Analyse tab uses load button** — multiple API calls depending on date range
- **GeoJSON fetched at runtime**, not committed — cached 24h via `st.cache_data`
- **Snapshot always shows latest available** — looks back 7 days to handle data lag
- **Map pan/zoom preserved** in `st.session_state` — filter changes don't reset the view
- **Tile layer:** CartoDB no-labels URL — keeps map clean, labels not obscured by choropleth
- **Theoretical max** only available at price area level — municipality capacity doesn't join cleanly with price area production volume

---

## Agent roles (summary — full detail in AGENTS.md)

### 🏗️ Backend agent
Owns: `elhub/`, `components/charts.py` data logic, `app.py` data wiring, `tests/`
Works in: `~/private/dash-vibe-backend` (git worktree)
Branch pattern: `backend/issue-{n}-description`

### 🎨 UX agent
Owns: `app.py` layout/styling, `components/map.py`, `components/analyse.py` visuals, `DESIGN.md`
Works in: `~/private/dash-vibe-ux` (git worktree)
Branch pattern: `ux/issue-{n}-description`

### 🧪 Test agent
Works in: `~/private/dash-vibe` (main directory, always on main)
Never edits code. Files issues, requests changes on PRs, proposes fixes in comments.
Christoffer merges all PRs.

---

## GitHub
- PAT in `.env` as `GITHUB_TOKEN` (gitignored — see `.env.example`)
- Issues: `https://github.com/sandnose/dash-vibe/issues`
- All git remote operations use token-embedded URL — see `AGENTS.md` auth section

---

## Conversation history summary
Planned and built in a single Claude chat session (claude.ai) with Christoffer.
Key decisions:
- Streamlit for free hosting on Streamlit Community Cloud
- Folium over Plotly maps (lighter weight)
- No count-of-metering-points toggle (not in installed capacity dataset)
- E18/E19 shown as Produksjon/Plusspunkt — never raw codes in UI
- Log scale rejected — UX simplicity preferred
- Sidebar mode switch preferred over a single tab list as datasets are fundamentally different
- Map snapshot-only (no date picker) — installed capacity changes slowly
- Volume datasets get time aggregation + auto unit scaling
- Theoretical max production available at price area level only
