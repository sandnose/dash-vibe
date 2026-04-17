# Testing Checklist — dash-vibe

## Setup
1. Clone repo, run `just init && just run`
2. App opens at `http://localhost:8501`
3. Read `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, and `skills/elhub.md` before starting

## How to report issues
File a GitHub Issue at `https://github.com/sandnose/dash-vibe/issues`:
- **Title**: prefix with `[backend]` or `[frontend]`
- **Label**: `bug`, `ux`, or `data`
- **Body**: steps to reproduce, expected, actual

---

## Navigation structure

The app has two navigation levels:
1. **Sidebar** — switches between modes: *Kapasitet* and *Volum*
2. **Tabs** — secondary navigation within each mode

### Kapasitet mode tabs: Kart · Historikk · Topp kommuner · Forklaring
### Volum mode tabs: Analyse · Forklaring

---

## Sidebar

- [ ] Sidebar renders with app name "Norsk Elektrisitet"
- [ ] Mode radio shows "⚡ Kapasitet" and "📊 Volum"
- [ ] Kapasitet description text shown when Kapasitet selected
- [ ] Volum description text shown when Volum selected
- [ ] Footer shows latest data date, data sources, GitHub link
- [ ] Switching mode changes the tab set in main area

---

## Kapasitet mode

### Kart tab
- [ ] Map renders without errors on load
- [ ] Snapshot date label shown above controls (styled, not plain text)
- [ ] All production groups shown in multiselect: solkraft, vannkraft, vindkraft, varmekraft, annet
- [ ] Målerpunktkategori radio shows: Begge, Produksjon, Plusspunkt (not E18/E19)
- [ ] Norway is reasonably visible without heavy panning on load
- [ ] Municipalities are coloured — not all grey
- [ ] Legend is readable — no NaN, no overlapping numbers
- [ ] Hovering a municipality shows tooltip with ID and Norwegian name
- [ ] Clicking a municipality does NOT show a bounding box square
- [ ] Map pan/zoom position is preserved when changing production group filter
- [ ] Map pan/zoom position is preserved when changing målerpunktkategori
- [ ] Deselecting all production groups shows info message, not error

### Historikk tab
- [ ] Municipality selectbox defaults to Oslo
- [ ] Months slider works (1–60)
- [ ] Chart auto-fetches on load — no button required
- [ ] Lines are coloured by Norwegian production group label
- [ ] X-axis shows dates, Y-axis shows capacity in kW
- [ ] Switching municipality updates chart
- [ ] Municipality with no history shows info message, not error

### Topp kommuner tab
- [ ] Snapshot date label shown (styled, not plain text)
- [ ] One chart per production group
- [ ] Bars sorted descending (highest capacity at top)
- [ ] Top N slider (5–20) updates all charts
- [ ] Chart titles use Norwegian production group names
- [ ] Chart colours match DESIGN.md production group colours

### Forklaring tab
- [ ] All expanders render without errors
- [ ] Content is in Norwegian
- [ ] No raw API codes (E18/E19/solar/hydro etc.) visible to user

---

## Volum mode

### Analyse tab
- [ ] Geo level radio shows: Prisområde, Kommune
- [ ] Selecting Prisområde shows: Produksjon, Forbruk, Utveksling, Nettap analyse types
- [ ] Selecting Kommune shows: Produksjon, Forbruk analyse types
- [ ] Prisområde entity selector shows "Alle" + NO1–NO5
- [ ] Kommune entity selector shows municipality names
- [ ] Date range pickers (Fra/Til) render
- [ ] Aggregation selector shows: Per time, Per dag, Per måned, Per år
- [ ] "Last inn data" button triggers fetch
- [ ] Before loading: placeholder message shown (not error)
- [ ] After loading: Plotly chart renders
- [ ] Units scale automatically (kWh → MWh → GWh → TWh based on magnitude)
- [ ] Produksjon chart: stacked bar, coloured by production group, Norwegian labels
- [ ] Forbruk chart: stacked bar, coloured by consumption group, Norwegian labels
- [ ] Utveksling chart: import positive, export negative
- [ ] Nettap chart: area chart
- [ ] Teoretisk maks toggle visible for produksjon + prisområde only
- [ ] Municipality consumption shows disclosure note about coarser groups

### Forklaring tab (Volum mode)
- [ ] Same content as Kapasitet Forklaring tab
- [ ] Kapasitetsfaktor expander present

---

## Cross-cutting

### Performance
- [ ] Initial load completes in < 15 seconds
- [ ] Switching sidebar mode does not re-fetch snapshot data
- [ ] Switching tabs within a mode does not re-fetch snapshot data

### Design
- [ ] Background is off-white (#fafaf7), not pure white
- [ ] Sidebar background is warmer (#ede9e0)
- [ ] Headings use EB Garamond serif font
- [ ] Primary buttons are dark green (#1a3a2a), not Streamlit default blue
- [ ] No raw API codes visible anywhere in the UI
- [ ] All user-facing text is in Norwegian

### Automated tests
- [ ] `just test` passes with 0 failures
- [ ] `just lint` passes with 0 errors
