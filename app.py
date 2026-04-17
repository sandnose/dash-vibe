from __future__ import annotations

import streamlit as st
from streamlit_folium import st_folium

from components.analyse import render_analyse_tab
from components.charts import history_chart, leaders_chart
from components.map import build_choropleth
from elhub.client import fetch_history, fetch_latest_snapshot
from elhub.geo import load_kommuner_geojson
from elhub.labels import (
    PRODUCTION_GROUP_LABELS,
    label_metering_type,
    label_production_group,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Norsk Elektrisitet",
    page_icon="⚡",
    layout="wide",
)

# ── Theme ──────────────────────────────────────────────────────────────────────
# Design reference: DESIGN.md
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600&family=Inter:wght@300;400;500&display=swap');

    /* Brand background */
    .stApp { background-color: #fafaf7; }

    /* Sidebar — slightly warmer shade to distinguish from main canvas */
    [data-testid="stSidebar"] { background-color: #ede9e0; }
    [data-testid="stSidebar"] h2 {
        font-family: 'EB Garamond', serif;
        color: #1a3a2a;
        font-size: 1.3rem;
        font-weight: 400;
        margin-bottom: 0.1rem;
    }

    /* Typography */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'EB Garamond', serif; color: #1a3a2a; }
    h1 { font-size: 1.9rem !important; font-weight: 400 !important; letter-spacing: -0.01em; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #ddd9d0; gap: 0; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #999;
        padding: 0.6rem 1.5rem;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1a3a2a !important;
        border-bottom: 2px solid #1a3a2a !important;
        font-weight: 600;
    }

    /* Dividers */
    [data-testid="stDivider"] { border-color: #ddd9d0; }

    /* Primary button — brand green */
    .stButton > button[kind="primary"] {
        background-color: #1a3a2a !important;
        border-color: #1a3a2a !important;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2d6a4f !important;
        border-color: #2d6a4f !important;
    }

    /* Hide Streamlit decoration bar */
    [data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Load shared data ───────────────────────────────────────────────────────────
with st.spinner("Laster inn data…"):
    snapshot_df = fetch_latest_snapshot()
    geojson = load_kommuner_geojson()

if snapshot_df.empty:
    st.error("Kunne ikke laste data fra Elhub. Prøv igjen senere.")
    st.stop()

latest_date = snapshot_df["usage_date"].max()
all_groups = sorted(snapshot_df["production_group"].unique().tolist())
all_municipalities = (
    snapshot_df[["municipality_id", "municipality_name"]]
    .drop_duplicates()
    .sort_values("municipality_name")
)
all_price_areas = ["NO1", "NO2", "NO3", "NO4", "NO5"]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Norsk Elektrisitet")
    st.markdown(
        "Utforsk installert kapasitet og faktisk kraftvolum "
        "fra norske kommuner og prisområder. "
        "Data fra [Elhub](https://api.elhub.no) — åpent og gratis."
    )

    st.divider()

    mode = st.radio(
        "Datatype",
        options=["capacity", "volume"],
        format_func=lambda x: {"capacity": "⚡ Kapasitet", "volume": "📊 Volum"}[x],
        label_visibility="collapsed",
    )

    if mode == "capacity":
        st.caption(
            "**Installert kapasitet** (kW) — hva som er bygget. "
            "Viser det maksimale kraftpotensialet per kommune, "
            "fordelt på produksjonstype og målerpunktkategori."
        )
    else:
        st.caption(
            "**Kraftvolum** (kWh) — hva som faktisk skjer. "
            "Utforsk produksjon, forbruk, nettap og kraftutveksling "
            "per prisområde eller kommune, time for time."
        )

    # ── Sidebar footer ─────────────────────────────────────────────────────────
    st.markdown("<div style='flex:1;min-height:2rem'></div>", unsafe_allow_html=True)
    st.divider()
    st.caption(f"Siste tilgjengelige data: {latest_date.strftime('%d. %b %Y')}")
    st.caption(
        "Kraftdata: [Elhub Energy Data API](https://api.elhub.no)  \n"
        "Kart: [robhop/fylker-og-kommuner](https://github.com/robhop/fylker-og-kommuner)  \n"
        "(Kartverket, CC BY 4.0)  \n"
        "[Kildekode](https://github.com/sandnose/dash-vibe)"
    )


# ── Helpers ────────────────────────────────────────────────────────────────────
def _snapshot_label(d: object) -> str:
    return (
        f'<div style="margin-bottom:1.25rem">'
        f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'
        f'color:#999;margin-bottom:3px">Data per</div>'
        f'<div style="font-family:\'EB Garamond\',serif;font-size:1.1rem;color:#1a3a2a">'
        f'{d.strftime("%d. %b %Y")}</div>'
        f'</div>'
    )


def _render_forklaring() -> None:
    st.markdown("## Hva viser dashbordet?")
    st.markdown(
        "Dette dashbordet visualiserer åpne data fra Elhub — "
        "Norges datahub for elektrisitetsmålinger."
    )

    st.divider()

    with st.expander("⚡ Hva er installert kapasitet?"):
        st.markdown("""
**Installert kapasitet** er den maksimale effekten et kraftanlegg kan produsere,
målt i **kilowatt (kW)**.

Det er ikke det samme som faktisk produksjon — et vannkraftverk med 100 MW installert kapasitet
produserer ikke alltid 100 MW. Kapasiteten viser *potensialet*, ikke det *faktiske* uttaket.

Tenk på det som motorkraften i en bil: du har 200 hk, men kjører ikke alltid for fullt.
        """)

    with st.expander("🏭 Produksjonstyper"):
        descriptions = {
            "solar": "Solcellepaneler som omdanner sollys til elektrisitet.",
            "hydro": "Vannkraftverk som utnytter rennende eller fallende vann.",
            "wind": "Vindturbiner som omdanner vindenergi til elektrisitet.",
            "thermal": "Kraftverk som bruker varme som energikilde (inkl. biomasse, avfall).",
            "nuclear": "Kjernekraftverk — Norge har ingen per i dag.",
            "other": "Andre eller uspesifiserte produksjonsteknologier.",
        }
        for group_id, label in PRODUCTION_GROUP_LABELS.items():
            st.markdown(f"**{label}** — {descriptions.get(group_id, '')}")

    with st.expander("📍 Målerpunktkategorier"):
        st.markdown("""
**Produksjon** *(tidligere E18)*
Store, nettilkoblede kraftanlegg som leverer strøm direkte til nettet.
Typisk vannkraft, vindparker og større solcelleinstallasjoner.

**Plusspunkt** *(tidligere E19)*
Mindre anlegg hos forbrukere som også produserer strøm — såkalte *prosumenter*.
Typisk solcellepaneler på hus og hytter.
        """)

    with st.expander("🗺️ Geografiske nivåer"):
        st.markdown("""
- **Kommune** — Norges 356 kommuner. Brukes i kartvisningen.
- **Prisområde** — Norge er delt i 5 prisområder (NO1–NO5) basert på strømnettets kapasitet.
  Prisområdene bestemmer strømprisen i ulike deler av landet.
- **Grunnkrets** — Statistisk undernivå av kommunen. Mer detaljert, men vanskeligere å tolke.

Forbruksgruppene er grovere på kommunenivå (industri, privat, næringsliv) enn på prisområdenivå
(husholdning, hytte, primær-, sekundær- og tertiærnæring). Dette er Elhubs valg, ikke dashbordets.
        """)

    with st.expander("🔬 Kapasitetsfaktor og teoretisk maks"):
        st.markdown("""
I analysevisningen kan du slå på **teoretisk maks** for produksjonsdata.

Dette beregner hvor mye strøm som *kunne* vært produsert hvis alle kraftanlegg gikk for fullt
i hele perioden. Formelen er enkel: installert kapasitet (kW) × antall timer = teoretisk maks (kWh).

Forholdet mellom faktisk produksjon og teoretisk maks kalles **kapasitetsfaktor**.
- Vannkraft: typisk 40–60 %
- Vindkraft: typisk 25–45 %
- Solkraft: typisk 10–20 % i Norge
        """)

    with st.expander("📅 Datoer og oppdatering"):
        st.markdown("""
- Dataene oppdateres daglig av Elhub.
- Kartet viser alltid **siste tilgjengelige dag** (typisk 1–3 dager forsinket).
- Historikk og analyse henter én måneds data om gangen på grunn av API-begrensninger.
- Installert kapasitet endrer seg sakte — store hopp skyldes vanligvis nye anlegg eller nedleggelser.
        """)

    st.divider()
    st.caption(
        "Data: [Elhub Energy Data API](https://api.elhub.no) · "
        "Kart: [robhop/fylker-og-kommuner](https://github.com/robhop/fylker-og-kommuner) "
        "(Kartverket, CC BY 4.0)"
    )


# ════════════════════════════════════════════════════════════════════════════════
# KAPASITET — Kart, Historikk, Topp kommuner
# ════════════════════════════════════════════════════════════════════════════════
if mode == "capacity":
    tab_map, tab_history, tab_leaders, tab_explain = st.tabs([
        "🗺️ Kart", "📈 Historikk", "🏆 Topp kommuner", "📖 Forklaring",
    ])

    # ── Kart ──────────────────────────────────────────────────────────────────
    with tab_map:
        col_controls, col_map = st.columns([1, 3])

        with col_controls:
            st.markdown(_snapshot_label(latest_date), unsafe_allow_html=True)

            selected_groups = st.multiselect(
                "Produksjonstype",
                options=all_groups,
                default=all_groups,
                format_func=label_production_group,
            )

            metering_raw = st.radio(
                "Målerpunktkategori",
                options=["Both", "E18", "E19"],
                format_func=label_metering_type,
                index=0,
            )

        with col_map:
            if not selected_groups:
                st.info("Velg minst én produksjonstype.")
            else:
                m = build_choropleth(snapshot_df, geojson, selected_groups, metering_raw)
                st_folium(m, use_container_width=True, height=850, returned_objects=[])

    # ── Historikk ─────────────────────────────────────────────────────────────
    with tab_history:
        col_sel, col_chart = st.columns([1, 3])

        with col_sel:
            muni_names = all_municipalities["municipality_name"].tolist()
            selected_name = st.selectbox(
                "Kommune",
                options=muni_names,
                index=muni_names.index("Oslo") if "Oslo" in muni_names else 0,
            )
            selected_id = all_municipalities.loc[
                all_municipalities["municipality_name"] == selected_name, "municipality_id"
            ].values[0]

            months_back = st.slider("Måneder historikk", min_value=1, max_value=60, value=12)

        with col_chart:
            with st.spinner(f"Laster historikk for {selected_name}…"):
                hist_df = fetch_history(selected_id, months=months_back)
            if hist_df.empty:
                st.info("Ingen historiske data funnet for denne kommunen.")
            else:
                st.plotly_chart(
                    history_chart(hist_df, selected_name),
                    use_container_width=True,
                )

    # ── Topp kommuner ─────────────────────────────────────────────────────────
    with tab_leaders:
        st.markdown(_snapshot_label(latest_date), unsafe_allow_html=True)

        top_n = st.slider("Antall kommuner", min_value=5, max_value=20, value=10)

        cols = st.columns(2)
        for i, group in enumerate(["hydro", "solar", "wind", "thermal", "other"]):
            if group not in all_groups:
                continue
            with cols[i % 2]:
                st.plotly_chart(
                    leaders_chart(snapshot_df, group, top_n=top_n),
                    use_container_width=True,
                )

    # ── Forklaring ────────────────────────────────────────────────────────────
    with tab_explain:
        _render_forklaring()


# ════════════════════════════════════════════════════════════════════════════════
# VOLUM — Analyse
# ════════════════════════════════════════════════════════════════════════════════
else:
    tab_analyse, tab_explain = st.tabs(["🔬 Analyse", "📖 Forklaring"])

    # ── Analyse ───────────────────────────────────────────────────────────────
    with tab_analyse:
        geo_level = st.radio(
            "Geografisk nivå",
            options=["price-areas", "municipalities"],
            format_func=lambda x: {"price-areas": "Prisområde", "municipalities": "Kommune"}[x],
            horizontal=True,
        )

        st.divider()

        render_analyse_tab(
            geo_level=geo_level,
            all_price_areas=all_price_areas,
            all_municipalities=all_municipalities,
        )

    # ── Forklaring ────────────────────────────────────────────────────────────
    with tab_explain:
        _render_forklaring()
