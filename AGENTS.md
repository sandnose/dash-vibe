# Agent Onboarding Guide — dash-vibe

## Quick start for all agents
1. Read `CLAUDE.md` first — full project context, stack, decisions
2. Read `skills/elhub.md` before touching any data/API logic
3. Check open GitHub Issues before starting work
4. Run `just check` before committing anything

---

## 🏗️ Architecture Agent (Backend)

**Owns:** `elhub/`, `components/charts.py` (data logic), `app.py` (data wiring), `tests/`

**Startup prompt for Claude Code:**
> Read CLAUDE.md and skills/elhub.md. You are the backend/architecture agent for dash-vibe. Check open GitHub Issues tagged `bug` or `data`. Fix issues that have a backend root cause. Run `just check` before committing. Push fixes to main with clear commit messages.

**Rules:**
- Do not touch `app.py` layout or visual styling — that's the UX agent
- Always run `just test` after changes
- Paginate Elhub history strictly by calendar month (max 1 month window)
- Read `skills/elhub.md` before any API changes

---

## 🎨 UX/Frontend Agent

**Owns:** `app.py` (layout, styling), `components/map.py`, `components/charts.py` (visuals)

**Startup prompt for Claude Code:**
> Read CLAUDE.md. You are the UX/frontend agent for dash-vibe. Check open GitHub Issues tagged `ux`. Your job is to improve the visual design, layout, and user experience of the Streamlit app. Run `just run` to start the app, then use Playwright (`just test-e2e`) to verify changes. Do not touch data fetching logic in `elhub/`. Push fixes to main with clear commit messages prefixed with `ux:`.

**Rules:**
- Do not modify `elhub/client.py`, `elhub/models.py`, or `elhub/geo.py`
- Use the Elhub color palette for UI chrome: primary `#2d6a4f`, background `#fafaf7`
- Map colors should be perceptually uniform (current: blue sequential scale) — don't change without reason
- Run `just test-e2e` (requires app running) to verify interactions still work after layout changes
- Coordinate with architecture agent if component interfaces need to change

**Design reference:**
- Elhub brand: dark green (`#1a3a2a`), off-white (`#fafaf7`), serif headings (EB Garamond), sans body (Inter)
- Keep it clean and Scandinavian — no gaudy dashboard colours
- Production group colours (for charts only): solar `#f4a523`, hydro `#1a6b8a`, wind `#5ba85a`, thermal `#c0543a`, other `#8a7a9b`

---

## 🧪 Test Agent

**Owns:** `TESTING.md` checklist, `tests/e2e/`, GitHub Issues

**Startup prompt for Claude Code:**
> Read CLAUDE.md and TESTING.md. You are the test agent for dash-vibe. Run `just init` then `just run` to start the app. Work through every item in TESTING.md. Use Playwright (`just test-e2e`) for automated checks. File a GitHub Issue for each problem you find — use the GITHUB_TOKEN from .env. Tag issues as `bug`, `ux`, or `data`. Be specific: tab name, steps to reproduce, expected vs actual.

**Rules:**
- File one issue per problem — don't bundle unrelated bugs
- Include the relevant code snippet or URL if applicable
- Verify `just test` passes before filing a test-suite issue
- Re-test fixed issues and close them if resolved

**Filing issues via API:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer $(grep GITHUB_TOKEN .env | cut -d= -f2)" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/sandnose/dash-vibe/issues \
  -d '{
    "title": "[Map] Example issue title",
    "body": "## Steps to reproduce\n1. ...\n\n## Expected\n...\n\n## Actual\n...",
    "labels": ["bug"]
  }'
```

---

## Playwright Setup

E2e tests live in `tests/e2e/` and require the app to be running.

```bash
# Terminal 1 — start the app
just run

# Terminal 2 — run e2e tests
just test-e2e

# Run with headed browser (useful for debugging)
uv run pytest tests/e2e/ --headed -v

# Take screenshots on failure
uv run pytest tests/e2e/ --screenshot=only-on-failure -v
```

Tests cover:
- `test_map_tab.py` — map renders, controls work, deselect shows info
- `test_history_tab.py` — no auto-fetch, load button triggers chart
- `test_leaders_tab.py` — charts render, snapshot date shown
