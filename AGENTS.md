# Agent Onboarding Guide — dash-vibe

## Quick start for all agents
1. Read `CLAUDE.md` — full project context, stack, decisions
2. Read `skills/elhub.md` — API reference, all datasets, Norwegian label mapping
3. Check open GitHub Issues before starting work
4. **Never push directly to main** — branch and open a PR
5. Run `just check` before opening a PR

## Branch & PR convention
| Agent | Branch pattern |
|---|---|
| Backend | `backend/issue-{n}-short-description` |
| UX | `ux/issue-{n}-short-description` |
| Test | rarely needs PRs — files issues instead |

PRs are reviewed and merged by Christoffer. One issue per PR.

## GitHub authentication
**Always use the token from `.env` for all GitHub operations — never interactive HTTPS.**

```bash
# Read token
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)

# Configure git to use token (run once per session)
git remote set-url origin https://${GITHUB_TOKEN}@github.com/sandnose/dash-vibe.git
```

All `git push`, `git pull`, `git clone` operations must use the token-embedded remote URL above.
Never use `gh auth login` or browser-based OAuth.

## UI language rules
- **All user-facing text is in Norwegian** — labels, tooltips, tab names, error messages, captions
- **Code stays in English** — variable names, function names, comments, commit messages
- **Never show raw API codes** in the UI — use Norwegian display names from `skills/elhub.md`
  - E18 → "Produksjon", E19 → "Plusspunkt"
  - `solar` → "Solkraft", `hydro` → "Vannkraft", `wind` → "Vindkraft"
  - `thermal` → "Varmekraft", `other` → "Annet"

## Component standards
Before building a custom component, check in this order:
1. **Streamlit builtins** — `st.metric`, `st.tabs`, `st.popover`, `st.columns`, etc.
2. **streamlit-extras** — check https://extras.streamlit.app for ready-made components
3. **Plotly Express** — for charts (`px.line`, `px.bar`, `px.choropleth`)
4. **Custom implementation** — only if none of the above fit

Never build a custom Plotly chart when `px` can do the same thing in one call.

---

## 🏗️ Architecture Agent (Backend)

**Owns:** `elhub/`, `components/charts.py` (data logic), `app.py` (data wiring), `tests/`

**Startup prompt for Claude Code:**
> Read CLAUDE.md and skills/elhub.md. You are the backend/architecture agent for dash-vibe. Check open GitHub Issues prefixed with `[backend]`. Fix issues with backend root causes. Work on branch `backend/issue-{n}-description`. Configure git remote with the token from .env (see AGENTS.md auth section). Run `just check` then open a PR. Never push to main.

**Rules:**
- Branch + PR — never push directly to main
- Set git remote URL with token before any push (see GitHub authentication above)
- Do not touch `app.py` layout or visual styling
- Run `just check` before opening a PR
- Paginate Elhub history strictly by calendar month
- Read `skills/elhub.md` before any API changes
- All user-facing strings must be Norwegian

---

## 🎨 UX/Frontend Agent

**Owns:** `app.py` (layout, styling), `components/map.py`, `components/charts.py` (visuals)

**Startup prompt for Claude Code:**
> Read CLAUDE.md and skills/elhub.md (especially the Norwegian label mapping). You are the UX/frontend agent for dash-vibe. Check open GitHub Issues prefixed with `[frontend]`. Work on branch `ux/issue-{n}-description`. Configure git remote with token from .env (see AGENTS.md auth section). Run `just run` to start app, `just test-e2e` to verify. Open a PR when done. Never push to main. Never touch `elhub/` data logic.

**Rules:**
- Branch + PR — never push directly to main
- Set git remote URL with token before any push
- Do not modify `elhub/client.py`, `elhub/models.py`, or `elhub/geo.py`
- All user-facing text in Norwegian — never show E18/E19 or English production group names
- Check streamlit builtins and streamlit-extras before building custom components
- Run `just test-e2e` to verify interactions after layout changes

**Design reference:**
- Elhub brand: dark green `#1a3a2a`, primary `#2d6a4f`, background `#fafaf7`
- Serif headings (EB Garamond), sans body (Inter)
- Production group chart colours: solar `#f4a523`, hydro `#1a6b8a`, wind `#5ba85a`, thermal `#c0543a`, other `#8a7a9b`
- Map: perceptually uniform blue sequential scale — don't change without reason
- Keep it clean and Scandinavian

---

## 🧪 Test Agent

**Owns:** `TESTING.md` checklist, `tests/e2e/`, GitHub Issues

**Startup prompt for Claude Code:**
> Read CLAUDE.md and TESTING.md. You are the test agent for dash-vibe. Run `just init` then `just run`. Work through TESTING.md. Use Playwright (`just test-e2e`) for automated checks. File a GitHub Issue per problem using GITHUB_TOKEN from .env. Prefix titles `[backend]` or `[frontend]`. Tag `bug`, `ux`, or `data`. Re-test and close fixed issues.

**Rules:**
- One issue per problem
- Prefix: `[backend]` for data/API/model issues, `[frontend]` for layout/styling/UX
- Close fixed issues after re-testing

**Filing issues:**
```bash
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2)
curl -s -X POST \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/sandnose/dash-vibe/issues \
  -d '{"title": "[frontend] Issue title", "body": "## Steps\n1. ...\n\n## Expected\n...\n\n## Actual\n...", "labels": ["bug"]}'
```

**Closing issues:**
```bash
curl -s -X PATCH \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/sandnose/dash-vibe/issues/{n} \
  -d '{"state": "closed"}'
```

---

## Playwright Setup

```bash
# Terminal 1
just run

# Terminal 2
just test-e2e                                          # headless
uv run pytest tests/e2e/ --headed -v                  # headed (debug)
uv run pytest tests/e2e/ --screenshot=only-on-failure  # screenshots on failure
```

Tests:
- `test_kapasitet.py` — sidebar, Kart, Historikk, Topp kommuner tabs
- `test_volum.py` — Volum mode, Analyse tab
