# Elhub Energy Data API — Skill

## Overview
Elhub is Norway's electricity data hub. The Energy Data API provides open, public datasets
about electricity production, consumption, and metering at various geographic levels.
No authentication required for open datasets.

**Base URL:** `https://api.elhub.no/energy-data/v0`
**Accepted methods:** `GET`, `POST`

---

## Required Headers
Every request must include (usually automatic via httpx/requests):
- `Accept` — e.g. `application/json`
- `User-Agent` — any non-empty string; missing this returns `403 Forbidden`

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

---

## Date Format & Rules

### Format
- Basic: `yyyy-MM-dd` (defaults to midnight)
- Full: `yyyy-MM-dd'T'HH:mm:ssXXX` — must URL-encode `+` as `%2B`
- Example: `2023-05-03T00:00:00%2B02:00`

### Behaviour
- Both `startDate` and `endDate` are **inclusive**
- If `endDate` omitted → inferred from dataset date policy
- If `startDate` omitted → inferred from dataset date policy
- If both omitted → API infers a valid default range

### Date Policy Terms
| Term | Meaning |
|------|---------|
| Default Window | Time span used when one or both dates are missing |
| Max Window | Largest allowed time span per request |
| Max Age From Now | How far back in time data may be requested |

All limits apply simultaneously — a request must satisfy all of them at once.

### Dataset: INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY
- **Max Window:** 1 month
- **Default Window:** 1 month
- **Max Age From Now:** no explicit limit documented (data goes back several years)
- Requests exceeding 1 month return `400 Bad Request`
- When paginating history, step strictly by calendar month

### Common date errors
- `400 Bad Request` → date window exceeds Max Window (most common: >1 month)
- `400 Bad Request` → malformed date string or unencoded `+`
- `404 Not Found` → municipality ID doesn't exist or has no data for that period

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
        "name": "Leirfjord",       // may have UTF-8 encoding issues — use nameNo
        "nameNo": "Leirfjord",
        "installedCapacityPerMeteringPointTypeGroupMunicipalityDaily": [
          {
            "usageDateId": 20230503,          // int, YYYYMMDD
            "municipalityId": "1822",
            "meteringPointTypeCode": "E18",   // E18=grid-connected, E19=local/prosumer
            "productionGroup": "hydro",       // solar | hydro | wind | thermal | other
            "installedCapacity": 26200.0,     // float, kW
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
| E19  | Local/small-scale production (prosumers) |

### productionGroup values
`solar`, `hydro`, `wind`, `thermal`, `other`

---

## Access Control

### Open datasets (no auth needed)
All datasets without `_RESTRICTED` suffix. This project only uses open datasets.

### Protected datasets (_RESTRICTED suffix)
Requires Maskinporten authentication — not used in this project.
Headers required: `Authorization: Bearer {TOKEN}`, `X-Elhub-GLN`, optionally `On-Behalf-Of`.

---

## Known Issues
- Municipality names (`name`, `nameNo`) sometimes have UTF-8 mojibake (e.g. `SnÃ¥sa` → `Snåsa`).
  httpx handles this correctly by default; don't use `response.text` with manual decoding.
- The `data` array is unordered.
- A municipality only appears if it has at least one record for the queried period.
- No `meteringPointCount` field in this dataset — only aggregated `installedCapacity`.

---

## Python Client Pattern

```python
import httpx
from datetime import date
from calendar import monthrange

BASE_URL = "https://api.elhub.no/energy-data/v0"
DATASET = "INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY"


def _date_param(d: date) -> str:
    return f"{d.isoformat()}T00:00:00+02:00"


def _month_window(year: int, month: int) -> tuple[date, date]:
    """Return (first, last) day of a calendar month — stays within 1-month limit."""
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def fetch_all_municipalities(start: date, end: date) -> dict:
    """Max window: 1 month. Will 400 if range exceeds this."""
    params = {
        "dataset": DATASET,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    r = httpx.get(f"{BASE_URL}/municipalities", params=params)
    r.raise_for_status()
    return r.json()


def fetch_municipality(municipality_id: str, start: date, end: date) -> dict:
    """Returns 404 if municipality has no data for the period."""
    params = {
        "dataset": DATASET,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    r = httpx.get(f"{BASE_URL}/municipalities/{municipality_id}", params=params)
    if r.status_code == 404:
        return {"data": []}
    r.raise_for_status()
    return r.json()
```

---

## Geography Join
Municipality IDs from Elhub join 1:1 with `kommunenummer` in Kartverket GeoJSON.
- GeoJSON source: `https://github.com/robhop/fylker-og-kommuner`
- File used: `Kommuner-S.geojson` (S = simplified, good for web maps)
- Property keys in GeoJSON: `kommunenummer`, `kommunenavn`, `name`
- CRS: WGS84, coastal-clipped
