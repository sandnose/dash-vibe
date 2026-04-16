# Testing Checklist — dash-vibe

## Setup
1. Clone repo and run `just init && just run`
2. App opens at `http://localhost:8501`
3. Read `skills/elhub.md` and `AGENTS.md` before starting

## How to report issues
File a GitHub Issue at `https://github.com/sandnose/dash-vibe/issues` with:
- **Title**: short description, prefixed with tab name e.g. `[Map] Legend overlaps at small viewport`
- **Label**: `bug`, `ux`, or `data`
- **Body**:
  - Steps to reproduce
  - Expected behaviour
  - Actual behaviour
  - Screenshot or error message if applicable

---

## Tab 1 — 🗺️ Map

### Initial load
- [ ] Map renders without errors
- [ ] Snapshot date shown in sidebar is recent (within ~7 days of today)
- [ ] All production groups shown in multiselect: solar, hydro, wind, thermal, other
- [ ] Norway is fully visible without panning on initial load

### Choropleth
- [ ] Municipalities are coloured — not all grey
- [ ] Colour scale reflects capacity differences (high hydro areas darker)
- [ ] Municipalities with no data shown in light grey, not missing
- [ ] Legend is readable — no overlapping numbers, no NaN values

### Interactions
- [ ] Hovering over a municipality shows tooltip with ID and name
- [ ] Clicking a municipality does NOT show a bounding box square
- [ ] Deselecting all production groups shows an info message, not an error

### Filters
- [ ] Selecting only "solar" updates the map to solar capacity only
- [ ] Selecting only "hydro" updates the map — hydro should dominate
- [ ] E18 / E19 / Both toggle updates the map
- [ ] Selecting all groups matches "Both" metering type as total

---

## Tab 2 — 📈 History

### Controls
- [ ] Municipality selectbox is populated
- [ ] Months slider works (1–24)
- [ ] "Load history" button triggers fetch (no auto-fetch on tab switch)

### Chart
- [ ] Chart renders after clicking Load history
- [ ] Lines are coloured by production group
- [ ] X-axis shows dates, Y-axis shows capacity in kW
- [ ] Municipality with only one production group shows a single line
- [ ] Selecting a municipality with no history shows info message, not error

### Edge cases
- [ ] Very small municipality (e.g. sparse data) — no crash
- [ ] Switching municipality and reloading works correctly

---

## Tab 3 — 🏆 Leaders

### Initial load
- [ ] Charts render without errors
- [ ] One chart per production group present in data
- [ ] Charts are labelled by group (Hydro, Solar, Wind, etc.)

### Content
- [ ] Top N slider (5–20) updates all charts
- [ ] Bars are sorted descending (highest at top)
- [ ] Municipality names are readable — not truncated
- [ ] Each chart uses the correct colour for its production group

---

## Cross-cutting

### Performance
- [ ] Initial load completes in < 15 seconds
- [ ] Switching tabs does not re-fetch snapshot data
- [ ] History fetch with 12 months completes in < 30 seconds

### Errors
- [ ] No unhandled exceptions visible in the UI on normal usage
- [ ] No Python tracebacks shown to user

### Automated tests
- [ ] `just test` passes with 0 failures
- [ ] `just lint` passes with 0 errors
