# Elhub Energy Data API — Skill

## Overview
Elhub is Norway's electricity data hub. The Energy Data API provides open, public datasets
about electricity production, consumption, and metering at various geographic levels.
No authentication required.

**Base URL:** `https://api.elhub.no/energy-data/v0`

---

## Municipality Endpoints

### All municipalities
```
GET /municipalities?dataset={DATASET}&startDate={ISO8601}&endDate={ISO8601}
```

### Single municipality
```
GET /municipalities/{municipalityNumber}?dataset={DATASET}&startDate={ISO8601}&endDate={ISO8601}
```
- `municipalityNumber`: 4-digit string, zero-padded (e.g. `0301` for Oslo)

### Date format
ISO 8601 with timezone, e.g. `2023-05-03T00:00:00+02:00`
URL-encode the `+` as `%2B`.

---

## Dataset: INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY

Daily installed capacity (kW) per production type and metering point category, per municipality.

### Response schema
```json
{
  "meta": {
    "created": "ISO8601",
    "lastUpdated": "ISO8601"
  },
  "links": { "self": "string" },
  "data": [
    {
      "type": "municipality",
      "id": "1822",
      "attributes": {
        "municipalityNumber": "1822",
        "name": "Leirfjord",       // may have UTF-8 encoding issues — use nameNo as fallback
        "nameNo": "Leirfjord",
        "installedCapacityPerMeteringPointTypeGroupMunicipalityDaily": [
          {
            "usageDateId": 20230503,          // int, YYYYMMDD
            "municipalityId": "1822",
            "meteringPointTypeCode": "E18",   // E18=grid-connected, E19=local/small-scale
            "productionGroup": "hydro",       // solar | hydro | wind | thermal | other
            "installedCapacity": 26200.0,     // float, unit: kW
            "lastUpdatedTime": "ISO8601"
          }
        ]
      }
    }
  ]
}
```

### meteringPointTypeCode values
| Code | Meaning |
|------|---------|
| E18  | Grid-connected production (large scale) |
| E19  | Local/small-scale production |

### productionGroup values
`solar`, `hydro`, `wind`, `thermal`, `other`

---

## Known issues
- Municipality names (`name`, `nameNo`) sometimes have UTF-8 mojibake (e.g. `SnÃ¥sa` instead of `Snåsa`).
  Always decode response bytes explicitly: `response.content.decode("utf-8")` or set `httpx` to handle this.
- The `data` array is unordered.
- A municipality only appears in the response if it has at least one record for the queried period.

---

## Python client pattern

```python
import httpx
from datetime import date

BASE_URL = "https://api.elhub.no/energy-data/v0"
DATASET = "INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY"

def fetch_municipalities(start: date, end: date) -> dict:
    params = {
        "dataset": DATASET,
        "startDate": f"{start.isoformat()}T00:00:00+02:00",
        "endDate": f"{end.isoformat()}T00:00:00+02:00",
    }
    r = httpx.get(f"{BASE_URL}/municipalities", params=params)
    r.raise_for_status()
    return r.json()

def fetch_municipality(municipality_number: str, start: date, end: date) -> dict:
    params = {
        "dataset": DATASET,
        "startDate": f"{start.isoformat()}T00:00:00+02:00",
        "endDate": f"{end.isoformat()}T00:00:00+02:00",
    }
    r = httpx.get(f"{BASE_URL}/municipalities/{municipality_number}", params=params)
    r.raise_for_status()
    return r.json()
```

## Flattening response to DataFrame

```python
import pandas as pd

def flatten_response(data: dict) -> pd.DataFrame:
    rows = []
    for municipality in data["data"]:
        attrs = municipality["attributes"]
        for record in attrs["installedCapacityPerMeteringPointTypeGroupMunicipalityDaily"]:
            rows.append({
                "municipality_id": attrs["municipalityNumber"],
                "municipality_name": attrs["nameNo"],
                "usage_date": pd.to_datetime(str(record["usageDateId"]), format="%Y%m%d"),
                "metering_type": record["meteringPointTypeCode"],  # E18 or E19
                "production_group": record["productionGroup"],
                "installed_capacity_kw": record["installedCapacity"],
            })
    return pd.DataFrame(rows)
```

---

## Geography join
Municipality IDs from Elhub join 1:1 with `kommunenummer` in Kartverket GeoJSON.
GeoJSON source: https://github.com/robhop/fylker-og-kommuner (WGS84, coastal-clipped, updated 2024)
