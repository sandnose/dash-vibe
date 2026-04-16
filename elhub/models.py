from pydantic import BaseModel, field_validator
from typing import Optional
import pandas as pd


class CapacityRecord(BaseModel):
    usageDateId: int
    municipalityId: str
    meteringPointTypeCode: str  # E18 or E19
    productionGroup: str        # solar, hydro, wind, thermal, other
    installedCapacity: float
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


class EhubResponse(BaseModel):
    data: list[Municipality]


def response_to_df(response: EhubResponse) -> pd.DataFrame:
    rows = []
    for m in response.data:
        a = m.attributes
        for r in a.installedCapacityPerMeteringPointTypeGroupMunicipalityDaily:
            rows.append({
                "municipality_id": a.municipalityNumber,
                "municipality_name": a.nameNo,
                "usage_date": pd.to_datetime(str(r.usageDateId), format="%Y%m%d"),
                "metering_type": r.meteringPointTypeCode,
                "production_group": r.productionGroup,
                "installed_capacity_kw": r.installedCapacity,
            })
    return pd.DataFrame(rows)
