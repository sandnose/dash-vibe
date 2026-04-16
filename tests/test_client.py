from __future__ import annotations

from datetime import date

import pandas as pd
from pytest_httpx import HTTPXMock

from elhub.client import _date_param, _fetch_municipalities, _fetch_single_municipality

BASE_URL = "https://api.elhub.no/energy-data/v0"
DATASET = "INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY"

MOCK_RESPONSE = {
    "data": [
        {
            "type": "municipality",
            "id": "0301",
            "attributes": {
                "municipalityNumber": "0301",
                "name": "Oslo",
                "nameNo": "Oslo",
                "installedCapacityPerMeteringPointTypeGroupMunicipalityDaily": [
                    {
                        "usageDateId": 20230503,
                        "municipalityId": "0301",
                        "meteringPointTypeCode": "E18",
                        "productionGroup": "hydro",
                        "installedCapacity": 999.0,
                        "lastUpdatedTime": "2026-04-16T08:00:00+02:00",
                    }
                ],
            },
        }
    ]
}


def test_date_param_format() -> None:
    result = _date_param(date(2023, 5, 3))
    assert result == "2023-05-03T00:00:00+02:00"


def test_fetch_municipalities(httpx_mock: HTTPXMock) -> None:
    # Register without url= so it matches any request (incl. query params)
    httpx_mock.add_response(method="GET", json=MOCK_RESPONSE)
    df = _fetch_municipalities(date(2023, 5, 1), date(2023, 5, 3))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["municipality_id"].iloc[0] == "0301"
    assert df["installed_capacity_kw"].iloc[0] == 999.0

    # Verify correct endpoint + dataset param were used
    request = httpx_mock.get_requests()[0]
    assert "/municipalities" in str(request.url)
    assert DATASET in str(request.url)


def test_fetch_single_municipality(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", json=MOCK_RESPONSE)
    df = _fetch_single_municipality("0301", date(2023, 5, 1), date(2023, 5, 3))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1

    request = httpx_mock.get_requests()[0]
    assert "/municipalities/0301" in str(request.url)


def test_fetch_single_municipality_404(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", status_code=404)
    df = _fetch_single_municipality("9999", date(2023, 5, 1), date(2023, 5, 3))
    assert df.empty
