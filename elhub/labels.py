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

METERING_TYPE_LABELS: dict[str, str] = {
    "E18": "Produksjon",
    "E19": "Plusspunkt",
    "Both": "Begge",
}

GEO_LEVEL_LABELS: dict[str, str] = {
    "price-areas": "Prisområde",
    "municipalities": "Kommune",
    "basic-statistical-units": "Grunnkrets",
}


def label_production_group(group: str) -> str:
    """Return Norwegian display name for a production group ID."""
    return PRODUCTION_GROUP_LABELS.get(group, group.capitalize())


def label_metering_type(code: str) -> str:
    """Return Norwegian display name for a metering point type code."""
    return METERING_TYPE_LABELS.get(code, code)


def label_geo_level(level: str) -> str:
    """Return Norwegian display name for a geographic level."""
    return GEO_LEVEL_LABELS.get(level, level)
