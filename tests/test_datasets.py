from __future__ import annotations

from elhub.datasets import (
    ALL_DATASETS,
    DATASETS_BY_ID,
    INSTALLED_CAPACITY_MUNICIPALITY,
    datasets_for_geo_level,
    snapshot_datasets_for_geo_level,
    volume_datasets_for_geo_level,
)


def test_all_datasets_have_required_fields() -> None:
    for ds in ALL_DATASETS:
        assert ds.id
        assert ds.label_no
        assert ds.geo_levels
        assert ds.dataset_type in ("snapshot", "volume")
        assert ds.unit in ("kW", "kWh")
        assert ds.max_window_days > 0


def test_datasets_by_id_complete() -> None:
    assert len(DATASETS_BY_ID) == len(ALL_DATASETS)
    for ds in ALL_DATASETS:
        assert ds.id in DATASETS_BY_ID


def test_datasets_for_geo_level_municipalities() -> None:
    result = datasets_for_geo_level("municipalities")
    assert len(result) > 0
    assert all("municipalities" in ds.geo_levels for ds in result)


def test_datasets_for_geo_level_price_areas() -> None:
    result = datasets_for_geo_level("price-areas")
    assert len(result) > 0
    assert all("price-areas" in ds.geo_levels for ds in result)


def test_snapshot_vs_volume_split() -> None:
    for level in ("municipalities", "price-areas"):
        snapshots = snapshot_datasets_for_geo_level(level)
        volumes = volume_datasets_for_geo_level(level)
        all_for_level = datasets_for_geo_level(level)
        assert len(snapshots) + len(volumes) == len(all_for_level)


def test_installed_capacity_municipality_is_snapshot() -> None:
    assert INSTALLED_CAPACITY_MUNICIPALITY.dataset_type == "snapshot"
    assert INSTALLED_CAPACITY_MUNICIPALITY.unit == "kW"
    assert "municipalities" in INSTALLED_CAPACITY_MUNICIPALITY.geo_levels
