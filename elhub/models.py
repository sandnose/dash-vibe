from __future__ import annotations

import pandas as pd
from pydantic import BaseModel


class CapacityRecord(BaseModel):
    usageDateId: int
    municipalityId: str
    meteringPointTypeCode: str  # E18 = grid-connected, E19 = local/prosumer
    productionGroup: str        # solar | hydro | wind | thermal | other
    installedCapacity: float    # kW
    lastUpdatedTime: str


class MunicipalityAttributes(BaseModel):
    municipalityNumber: str
    name: str
    nameNo: str
    installedCapacityPerMeteringPointTypeGroupMunicipalityDaily: list[CapacityRecord]


class Municipality(BaseModel):
    type: str
    id: str
    attributes: MunicipalityAttributes


class ElhubResponse(BaseModel):
    data: list[Municipality]


def response_to_df(response: ElhubResponse) -> pd.DataFrame:
    """Flatten an ElhubResponse into a tidy DataFrame."""
    rows: list[dict] = []
    for municipality in response.data:
        attrs = municipality.attributes
        for record in attrs.installedCapacityPerMeteringPointTypeGroupMunicipalityDaily:
            rows.append(
                {
                    "municipality_id": attrs.municipalityNumber,
                    "municipality_name": attrs.nameNo,
                    "usage_date": pd.to_datetime(
                        str(record.usageDateId), format="%Y%m%d"
                    ),
                    "metering_type": record.meteringPointTypeCode,
                    "production_group": record.productionGroup,
                    "installed_capacity_kw": record.installedCapacity,
                }
            )
    return pd.DataFrame(rows)
