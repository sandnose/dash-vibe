from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FilterConfig:
    name: str           # API filter parameter name
    values: list[str]   # allowed values
    label_no: str       # Norwegian label for this filter dimension


@dataclass(frozen=True)
class DatasetConfig:
    id: str                          # Elhub dataset name constant
    label_no: str                    # Norwegian display name
    description_no: str              # Norwegian description for UI
    geo_levels: list[str]            # endpoints: "municipalities", "price-areas"
    dataset_type: str                # "snapshot" | "volume"
    resolution: str                  # "daily" | "hourly" | "15min" | "monthly"
    max_window_days: int             # max date range in days
    value_field: str                 # response field to extract as value
    unit: str                        # "kW" | "kWh"
    filters: list[FilterConfig] = field(default_factory=list)
    supports_entity_id: bool = True  # whether single-entity endpoint exists


# ── Snapshot datasets ──────────────────────────────────────────────────────────

INSTALLED_CAPACITY_MUNICIPALITY = DatasetConfig(
    id="INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY",
    label_no="Installert kapasitet",
    description_no="Maksimal produksjonskapasitet per kommune og produksjonstype (kW).",
    geo_levels=["municipalities"],
    dataset_type="snapshot",
    resolution="daily",
    max_window_days=31,
    value_field="installedCapacity",
    unit="kW",
    filters=[
        FilterConfig(
            "productionGroup",
            ["solar", "hydro", "wind", "thermal", "other"],
            "Produksjonstype",
        ),
        FilterConfig("meteringPointType", ["E18", "E19"], "Målerpunktkategori"),
    ],
)

INSTALLED_CAPACITY_MUNICIPALITY_BSU = DatasetConfig(
    id="INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_BASIC_STATISTICAL_UNIT_DAILY",
    label_no="Installert kapasitet (grunnkrets)",
    description_no="Maksimal produksjonskapasitet per grunnkrets og produksjonstype (kW).",
    geo_levels=["municipalities"],
    dataset_type="snapshot",
    resolution="daily",
    max_window_days=31,
    value_field="installedCapacity",
    unit="kW",
    filters=[
        FilterConfig(
            "productionGroup",
            ["solar", "hydro", "wind", "thermal", "other"],
            "Produksjonstype",
        ),
        FilterConfig("meteringPointType", ["E18", "E19"], "Målerpunktkategori"),
    ],
)

INSTALLED_CAPACITY_MBA = DatasetConfig(
    id="INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MBA_DAILY",
    label_no="Installert kapasitet",
    description_no="Maksimal produksjonskapasitet per prisområde og produksjonstype (kW).",
    geo_levels=["price-areas"],
    dataset_type="snapshot",
    resolution="daily",
    max_window_days=31,
    value_field="installedCapacity",
    unit="kW",
    filters=[
        FilterConfig(
            "productionGroup",
            ["solar", "hydro", "wind", "thermal", "other"],
            "Produksjonstype",
        ),
        FilterConfig("meteringPointType", ["E18", "E19"], "Målerpunktkategori"),
    ],
)

# ── Volume datasets — Production ───────────────────────────────────────────────

PRODUCTION_PER_GROUP_MBA_HOUR = DatasetConfig(
    id="PRODUCTION_PER_GROUP_MBA_HOUR",
    label_no="Produksjon per produksjonstype",
    description_no="Faktisk kraftproduksjon per time og produksjonstype for prisområde (kWh).",
    geo_levels=["price-areas"],
    dataset_type="volume",
    resolution="hourly",
    max_window_days=31,
    value_field="quantityKwh",
    unit="kWh",
    filters=[
        FilterConfig(
            "productionGroup",
            ["solar", "hydro", "wind", "thermal", "other"],
            "Produksjonstype",
        ),
    ],
)

PRODUCTION_PER_GROUP_MBA_15MIN = DatasetConfig(
    id="PRODUCTION_PER_GROUP_MBA_15MIN",
    label_no="Produksjon per produksjonstype (15 min)",
    description_no="Faktisk kraftproduksjon per 15 minutter og produksjonstype for prisområde (kWh).",
    geo_levels=["price-areas"],
    dataset_type="volume",
    resolution="15min",
    max_window_days=31,
    value_field="quantityKwh",
    unit="kWh",
    filters=[
        FilterConfig(
            "productionGroup",
            ["solar", "hydro", "wind", "thermal", "other"],
            "Produksjonstype",
        ),
    ],
)

PRODUCTION_PER_TYPE_MUNICIPALITY_HOUR = DatasetConfig(
    id="PRODUCTION_PER_METERING_POINT_TYPE_MUNICIPALITY_HOUR",
    label_no="Produksjon per målerpunktkategori",
    description_no="Faktisk kraftproduksjon per time og målerpunktkategori for kommune (kWh).",
    geo_levels=["municipalities"],
    dataset_type="volume",
    resolution="hourly",
    max_window_days=1,
    value_field="quantityKwh",
    unit="kWh",
    filters=[
        FilterConfig("meteringPointType", ["E18", "E19"], "Målerpunktkategori"),
    ],
)

# ── Volume datasets — Consumption ──────────────────────────────────────────────

CONSUMPTION_PER_GROUP_MBA_HOUR = DatasetConfig(
    id="CONSUMPTION_PER_GROUP_MBA_HOUR",
    label_no="Forbruk per forbruksgruppe",
    description_no="Aggregert strømforbruk per time og forbruksgruppe for prisområde (kWh).",
    geo_levels=["price-areas"],
    dataset_type="volume",
    resolution="hourly",
    max_window_days=31,
    value_field="quantityKwh",
    unit="kWh",
    filters=[
        FilterConfig(
            "consumptionGroup",
            ["household", "cabin", "primary", "secondary", "tertiary"],
            "Forbruksgruppe",
        ),
    ],
)

CONSUMPTION_PER_GROUP_MUNICIPALITY_HOUR = DatasetConfig(
    id="CONSUMPTION_PER_GROUP_MUNICIPALITY_HOUR",
    label_no="Forbruk per forbruksgruppe",
    description_no="Aggregert strømforbruk per time og forbruksgruppe for kommune (kWh).",
    geo_levels=["municipalities"],
    dataset_type="volume",
    resolution="hourly",
    max_window_days=1,
    value_field="quantityKwh",
    unit="kWh",
    filters=[
        FilterConfig(
            "consumptionGroup",
            ["industry", "private", "business"],
            "Forbruksgruppe",
        ),
    ],
)

# ── Volume datasets — Exchange & Loss ──────────────────────────────────────────

EXCHANGE_PER_MBA_HOUR = DatasetConfig(
    id="EXCHANGE_PER_MBA_HOUR",
    label_no="Utveksling mellom prisområder",
    description_no="Kraftutveksling inn og ut per time mellom tilgrensende prisområder (kWh).",
    geo_levels=["price-areas"],
    dataset_type="volume",
    resolution="hourly",
    max_window_days=31,
    value_field="exchangeInQuantityKwh",  # also exchangeOutQuantityKwh
    unit="kWh",
    filters=[],
    supports_entity_id=True,
)

LOSS_PER_MBA_HOUR = DatasetConfig(
    id="LOSS_PER_MBA_HOUR",
    label_no="Nettap",
    description_no="Beregnet nettap per time for prisområde (kWh).",
    geo_levels=["price-areas"],
    dataset_type="volume",
    resolution="hourly",
    max_window_days=31,
    value_field="calculatedLossQuantityKwh",
    unit="kWh",
    filters=[],
)

# ── Registry ───────────────────────────────────────────────────────────────────

ALL_DATASETS: list[DatasetConfig] = [
    INSTALLED_CAPACITY_MUNICIPALITY,
    INSTALLED_CAPACITY_MUNICIPALITY_BSU,
    INSTALLED_CAPACITY_MBA,
    PRODUCTION_PER_GROUP_MBA_HOUR,
    PRODUCTION_PER_GROUP_MBA_15MIN,
    PRODUCTION_PER_TYPE_MUNICIPALITY_HOUR,
    CONSUMPTION_PER_GROUP_MBA_HOUR,
    CONSUMPTION_PER_GROUP_MUNICIPALITY_HOUR,
    EXCHANGE_PER_MBA_HOUR,
    LOSS_PER_MBA_HOUR,
]

DATASETS_BY_ID: dict[str, DatasetConfig] = {ds.id: ds for ds in ALL_DATASETS}


def datasets_for_geo_level(geo_level: str) -> list[DatasetConfig]:
    """Return all datasets available for a given geographic level."""
    return [ds for ds in ALL_DATASETS if geo_level in ds.geo_levels]


def snapshot_datasets_for_geo_level(geo_level: str) -> list[DatasetConfig]:
    """Return snapshot datasets for a given geographic level."""
    return [ds for ds in datasets_for_geo_level(geo_level) if ds.dataset_type == "snapshot"]


def volume_datasets_for_geo_level(geo_level: str) -> list[DatasetConfig]:
    """Return volume datasets for a given geographic level."""
    return [ds for ds in datasets_for_geo_level(geo_level) if ds.dataset_type == "volume"]
