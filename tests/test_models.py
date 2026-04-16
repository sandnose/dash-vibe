from __future__ import annotations

import pandas as pd

from elhub.models import (
    CapacityRecord,
    ElhubResponse,
    response_to_df,
)

SAMPLE_RECORD = {
    "usageDateId": 20230503,
    "municipalityId": "0301",
    "meteringPointTypeCode": "E18",
    "productionGroup": "hydro",
    "installedCapacity": 12345.0,
    "lastUpdatedTime": "2026-04-16T08:00:00+02:00",
}

SAMPLE_RESPONSE = {
    "data": [
        {
            "type": "municipality",
            "id": "0301",
            "attributes": {
                "municipalityNumber": "0301",
                "name": "Oslo",
                "nameNo": "Oslo",
                "installedCapacityPerMeteringPointTypeGroupMunicipalityDaily": [
                    SAMPLE_RECORD,
                    {**SAMPLE_RECORD, "productionGroup": "solar", "installedCapacity": 500.0},
                ],
            },
        }
    ]
}


def test_capacity_record_parses() -> None:
    record = CapacityRecord.model_validate(SAMPLE_RECORD)
    assert record.municipalityId == "0301"
    assert record.productionGroup == "hydro"
    assert record.installedCapacity == 12345.0


def test_elhub_response_parses() -> None:
    response = ElhubResponse.model_validate(SAMPLE_RESPONSE)
    assert len(response.data) == 1
    assert response.data[0].attributes.municipalityNumber == "0301"
    records = response.data[0].attributes.installedCapacityPerMeteringPointTypeGroupMunicipalityDaily
    assert len(records) == 2


def test_response_to_df_shape() -> None:
    response = ElhubResponse.model_validate(SAMPLE_RESPONSE)
    df = response_to_df(response)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {
        "municipality_id",
        "municipality_name",
        "usage_date",
        "metering_type",
        "production_group",
        "installed_capacity_kw",
    }


def test_response_to_df_values() -> None:
    response = ElhubResponse.model_validate(SAMPLE_RESPONSE)
    df = response_to_df(response)
    hydro = df[df["production_group"] == "hydro"]
    assert hydro["installed_capacity_kw"].iloc[0] == 12345.0
    assert pd.api.types.is_datetime64_any_dtype(df["usage_date"])


def test_response_to_df_empty_data() -> None:
    response = ElhubResponse.model_validate({"data": []})
    df = response_to_df(response)
    assert df.empty
