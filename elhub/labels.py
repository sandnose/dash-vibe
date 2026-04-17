from __future__ import annotations

# Norwegian display labels for all Elhub API codes.
# Always use these in the UI — never expose raw API codes to users.

PRODUCTION_GROUP_LABELS: dict[str, str] = {
    "solar": "Solkraft",
    "hydro": "Vannkraft",
    "wind": "Vindkraft",
    "thermal": "Varmekraft",
    "nuclear": "Kjernekraft",
    "other": "Annet",
}

PRODUCTION_GROUP_DESCRIPTIONS: dict[str, str] = {
    "solar": "Solcellepaneler som omdanner sollys til elektrisitet.",
    "hydro": "Vannkraftverk som utnytter rennende eller fallende vann.",
    "wind": "Vindturbiner som omdanner vindenergi til elektrisitet.",
    "thermal": "Kraftverk som bruker varme som energikilde (inkl. biomasse, avfall).",
    "nuclear": "Kjernekraftverk — Norge har ingen per i dag.",
    "other": "Andre eller uspesifiserte produksjonsteknologier.",
}

# Source: dok.elhub.no — official term is "målepunkttype", values "E18" and "E19"
METERING_TYPE_LABELS: dict[str, str] = {
    "E18": "Produksjon",
    "E19": "Plusspunkt",
    "Both": "Begge",
}

CONSUMPTION_GROUP_LABELS: dict[str, str] = {
    "household": "Husholdning",
    "cabin": "Hytte/fritidsbolig",
    "primary": "Primærnæring",
    "secondary": "Sekundærnæring",
    "tertiary": "Tertiærnæring",
    "industry": "Industri",
    "private": "Privat",
    "business": "Næringsliv",
}

CONSUMPTION_GROUP_DESCRIPTIONS: dict[str, str] = {
    "household": "Husholdninger med NACE-kode XX eller borettslag.",
    "cabin": "Hytter og fritidsboliger (NACE XY).",
    "primary": "Jordbruk, skogbruk og fiske (NACE 1–3).",
    "secondary": "Industri og byggevirksomhet (NACE B–F).",
    "tertiary": "Tjenesteyting og øvrig næringsliv (NACE G–U).",
    "industry": "Primær- og sekundærnæring samlet.",
    "private": "Husholdning og hytte samlet.",
    "business": "Samme som tertiærnæring.",
}

GEO_LEVEL_LABELS: dict[str, str] = {
    "price-areas": "Prisområde",
    "municipalities": "Kommune",
    "basic-statistical-units": "Grunnkrets",
}

ANALYSE_TYPE_LABELS: dict[str, str] = {
    "production": "Produksjon",
    "consumption": "Forbruk",
    "exchange": "Utveksling",
    "loss": "Nettap",
}


def label_production_group(group: str) -> str:
    return PRODUCTION_GROUP_LABELS.get(group, group.capitalize())


def label_metering_type(code: str) -> str:
    """Return Norwegian display name for a målepunkttype code (E18/E19)."""
    return METERING_TYPE_LABELS.get(code, code)


def label_consumption_group(group: str) -> str:
    return CONSUMPTION_GROUP_LABELS.get(group, group.capitalize())


def label_geo_level(level: str) -> str:
    return GEO_LEVEL_LABELS.get(level, level)


def label_analyse_type(analyse_type: str) -> str:
    return ANALYSE_TYPE_LABELS.get(analyse_type, analyse_type.capitalize())
