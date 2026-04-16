# Agent Onboarding Guide — dash-vibe

## Quick start for all agents
1. Read `CLAUDE.md` first — full project context, stack, decisions
2. Read `skills/elhub.md` before touching any data/API logic
3. Check open GitHub Issues before starting work
4. **Never push directly to main** — always work on a branch and open a PR
5. Run `just check` before opening a PR

## Branch & PR convention
| Agent | Branch pattern |
|---|---|
| Backend | `backend/issue-{n}-short-description` |
| UX | `ux/issue-{n}-short-description` |
| Test | rarely needs PRs — files issues instead |

PRs are reviewed and merged by Christoffer. Keep PRs focused — one issue per PR.

---

## 🏗️ Architecture Agent (Backend)

**Owns:** `elhub/`, `components/charts.py` (data logic), `app.py` (data wiring), `tests/`

**Startup prompt for Claude Code:**
> Read CLAUDE.md and skills/elhub.md. You are the backend/architecture agent for dash-vibe. Check open GitHub Issues prefixed with `[backend]`. Fix issues that have a backend root cause. Work on a branch named `backend/issue-{n}-description`, run `just check`, then open a PR. Do not push to main.

**Rules:**
- Work on a branch, open a PR — never push directly to main
- Do not touch `app.py` layout or visual styling — that's the UX agent
- Always run `just check` before opening a PR
- Paginate Elhub history strictly by calendar month (max 1 month window)
- Read `skills/elhub.md` before any API changes

---

## 🎨 UX/Frontend Agent

**Owns:** `app.py` (layout, styling), `components/map.py`, `components/charts.py` (visuals)

**Startup prompt for Claude Code:**
> Read CLAUDE.md. You are the UX/frontend agent for dash-vibe. Check open GitHub Issues prefixed with `[frontend]`. Improve the visual design, layout, and user experience of the Streamlit app. Work on a branch named `ux/issue-{n}-description`. Run `just run` to start the app and `just test-e2e` to verify changes. Open a PR when done. Do not push to main. Do not touch data fetching logic in `elhub/`.

**Rules:**
- Work on a branch, open a PR — never push directly to main
- Do not modify `elhub/client.py`, `elhub/models.py`, or `elhub/geo.py`
- Run `just test-e2e` (requires app running) to verify interactions still work
- Coordinate with backend agent if component interfaces need to change

**Design reference:**
- Elhub brand: dark green (`#1a3a2a`), off-white (`#fafaf7`), serif headings (EB Garamond), sans body (Inter)
- Keep it clean and Scandinavian — no gaudy dashboard colours
- Production group colours (for charts only): solar `#f4a523`, hydro `#1a6b8a`, wind `#5ba85a`, thermal `#c0543a`, other `#8a7a9b`
- Map colours: perceptually uniform blue sequential scale — don't change without reason

---

## 🧪 Test Agent

**Owns:** `TESTING.md` checklist, `tests/e2e/`, GitHub Issues

**Startup prompt for Claude Code:**
> Read CLAUDE.md and TESTING.md. You are the test agent for dash-vibe. Run `just init` then `just run` to start the app. Work through every item in TESTING.md. Use Playwright (`just test-e2e`) for automated checks. File a GitHub Issue for each problem — use GITHUB_TOKEN from .env. Prefix titles with `[backend]` or `[frontend]`. Tag as `bug`, `ux`, or `data`. Be specific: tab name, steps to reproduce, expected vs actual. Re-test and close issues that have been fixed.

**Rules:**
- File one issue per problem — don't bundle unrelated bugs
- Prefix issue titles:
  - `[backend]` — data fetching, API errors, wrong values, model/parsing issues
  - `[frontend]` — layout, styling, map rendering, chart visuals, UX interactions
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
    "title": "[frontend] Example issue title",
    "body": "## Steps to reproduce\n1. ...\n\n## Expected\n...\n\n## Actual\n...",
    "labels": ["bug"]
  }'
```

**Closing issues via API:**
```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $(grep GITHUB_TOKEN .env | cut -d= -f2)" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/sandnose/dash-vibe/issues/{issue_number} \
  -d '{"state": "closed"}'
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
