# Design reference — dash-vibe

Single source of truth for visual design decisions. Update this file when changing the design, and keep `components/theme.py` in sync.

---

## Language

- **All user-facing text is in Norwegian** — labels, tab names, axis titles, tooltips, captions, error messages.
- **Code stays in English** — variable names, function names, comments, commit messages.
- Never expose raw API codes in the UI. Use the label mapping in `elhub/labels.py`:
  | API code | Norwegian label |
  |---|---|
  | `solar` | Solkraft |
  | `hydro` | Vannkraft |
  | `wind` | Vindkraft |
  | `thermal` | Varmekraft |
  | `other` | Annet |
  | `E18` | Produksjon |
  | `E19` | Plusspunkt |

---

## Color palette

| Role | Hex | Usage |
|---|---|---|
| Primary dark | `#1a3a2a` | Headings, active tab underline, primary buttons, chart titles |
| Primary mid | `#2d6a4f` | Button hover state |
| Background | `#fafaf7` | Page background (`.stApp`), chart backgrounds |
| Border / divider | `#ddd9d0` | Tab list border, `st.divider()` |
| Body text | `#333333` | Chart body text |
| Muted label | `#999999` | Small uppercase labels (e.g. "Data per" above dates) |

### Production group chart colors

These are fixed. Do not change them without a deliberate design decision.

| Group | Hex |
|---|---|
| Solkraft (solar) | `#f4a523` |
| Vannkraft (hydro) | `#1a6b8a` |
| Vindkraft (wind) | `#5ba85a` |
| Varmekraft (thermal) | `#c0543a` |
| Annet (other) | `#8a7a9b` |
| Remainder (privacy bucket) | `#b0b0b0` |

### Consumption group chart colors

| Group | Hex |
|---|---|
| household | `#2d6a4f` |
| cabin | `#52b788` |
| primary | `#b7e4c7` |
| secondary / industry | `#1b4332` |
| tertiary / business | `#40916c` |
| private | `#52b788` |

### Map choropleth colors

Blue sequential scale — **do not change without a clear reason**.

```
["#eaf4fb", "#9ecae1", "#3182bd", "#08519c", "#08306b"]
```

Zero-value municipalities render as `#e8e8e8` (light grey), not on the color scale.

---

## Typography

| Role | Font | Weight |
|---|---|---|
| Headings (`h1`–`h3`) | EB Garamond | 400 (regular), 600 (semibold) |
| Body / UI | Inter | 300 (light), 400 (regular), 500 (medium) |

Both fonts are loaded from Google Fonts in the `app.py` CSS block.

`h1` overrides: `font-size: 1.9rem`, `font-weight: 400`, `letter-spacing: -0.01em`.

---

## Chart defaults

The canonical Plotly layout dict lives in `components/theme.py` as `CHART_LAYOUT`. Import and use it in every chart function:

```python
from components.theme import CHART_LAYOUT
fig.update_layout(**CHART_LAYOUT, ...)
```

**Never** define a local `_LAYOUT` dict in a component file — it will drift.

Current values:

```python
CHART_LAYOUT = {
    "plot_bgcolor": "#fafaf7",
    "paper_bgcolor": "#fafaf7",
    "font_family": "Inter, sans-serif",
    "font_color": "#333333",
    "title_font_family": "EB Garamond, serif",
    "title_font_size": 16,
    "title_font_color": "#1a3a2a",
    "hovermode": "x unified",
    "margin": {"l": 0, "r": 16, "t": 48, "b": 0},
}
```

---

## Component patterns

### Snapshot date label

Used above controls panels in Map and Leaders tabs. Renders a small uppercase label + a serif date:

```python
st.markdown(
    f'<div style="margin-bottom:1.25rem">'
    f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;color:#999;margin-bottom:3px">Data per</div>'
    f'<div style="font-family:\'EB Garamond\',serif;font-size:1.1rem;color:#1a3a2a">{date.strftime("%d. %b %Y")}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
```

Do **not** replace this with `st.markdown(f"**Data per:** {date}")` + `st.divider()`.

### Empty chart state

Used when a chart area has no data loaded yet (before the user clicks a load button). A centred italic placeholder instead of a grey `st.info()` box:

```python
st.markdown(
    '<div style="display:flex;align-items:center;justify-content:center;'
    'height:320px;color:#ccc;font-family:\'EB Garamond\',serif;'
    'font-size:1.15rem;font-style:italic;">'
    'Velg parametere for å laste inn data'
    '</div>',
    unsafe_allow_html=True,
)
```

### Primary buttons

All load/action buttons use `type="primary"`. The CSS block in `app.py` overrides Streamlit's default blue with brand green `#1a3a2a` (hover: `#2d6a4f`).

---

## Layout principles

### Navigation hierarchy
The app has two levels of navigation:
1. **Sidebar** — primary mode switch: *Kapasitet* (installed capacity, kW) vs *Volum* (energy volume, kWh). These are fundamentally different datasets and the sidebar makes the distinction explicit.
2. **Tabs** — secondary navigation within each mode.

The sidebar also carries the app identity (name + description), mode-specific context text, and app info at the bottom (data sources, last date, GitHub link). This frees the main canvas from repeated header/meta clutter.

### Sidebar background
`#ede9e0` — slightly warmer and darker than the main canvas `#fafaf7`. Creates visual hierarchy without being heavy.

### Column split
Within tabs that have controls, use `[1, 3]` columns: controls left, visualisation right.

### Load buttons
Lazy-load patterns (Historikk, Analyse) use explicit `st.button(..., type="primary")` — never auto-fetch on tab switch. Prevents triggering multiple API calls unintentionally.

### Map tile layer
CartoDB no-labels. Keeps the map clean and lets the choropleth data speak.

### Clean and Scandinavian
No gaudy dashboard colours. No decorative elements that don't carry data.

---

## What not to do

- Do not add English strings to any user-visible element.
- Do not change the map choropleth color scale without a reason documented here.
- Do not define a local `_LAYOUT` dict in any component file — use `CHART_LAYOUT` from `components/theme.py`.
- Do not replace the snapshot date label component with plain markdown bold + divider.
- Do not add log scale toggles or other complexity toggles unless explicitly agreed — keep UX simple.
