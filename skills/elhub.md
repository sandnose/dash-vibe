# Elhub Energy Data API — Skill

## Overview
Elhub is Norway's electricity data hub. The Energy Data API provides open, public datasets
about electricity production, consumption, and metering at various geographic levels.
No authentication required for open datasets.

**Base URL:** `https://api.elhub.no/energy-data/v0`
**Accepted methods:** `GET`, `POST`

---

## Required Headers
Every request must include (usually automatic via httpx):
- `Accept` — e.g. `application/json`
- `User-Agent` — any non-empty string; missing → `403 Forbidden`

---

## Geographic Levels
Elhub organises data across three geographic levels. Each has its own endpoint and dataset set.

| Level | Norwegian | Endpoint | Notes |
|---|---|---|---|
| Price area | Prisområde | `/price-areas` | 5 areas in Norway: NO1–NO5 |
| Municipality | Kommune | `/municipalities` | 4-digit zero-padded ID e.g. `0301` |
| Basic stat. unit | Grunnkrets | `/municipalities/{id}` with BSU dataset | Sub-municipality; routes via municipality endpoint |

---

## Endpoints

### Price areas
```
GET /price-areas?dataset={DATASET}&startDate={ISO8601}&endDate={ISO8601}
GET /price-areas/{priceAreaId}?dataset={DATASET}&startDate={ISO8601}&endDate={ISO8601}
```

### Municipalities
```
GET /municipalities?dataset={DATASET}&startDate={ISO8601}&endDate={ISO8601}
GET /municipalities/{municipalityNumber}?dataset={DATASET}&startDate={ISO8601}&endDate={ISO8601}
```
- `municipalityNumber`: 4-digit string, zero-padded (e.g. `0301` for Oslo)

### Meta (dataset discovery)
```
GET /meta/price-areas        → lists all datasets available for price areas
GET /meta/municipalities     → lists all datasets available for municipalities
```

### Reference data
```
GET /production-groups       → list of production group IDs and descriptions
GET /price-areas             → list of price area IDs (NO1–NO5)
```

---

## Date Format & Rules

### Format
- Basic: `yyyy-MM-dd` (defaults to midnight)
- Full: `yyyy-MM-dd'T'HH:mm:ssXXX` — URL-encode `+` as `%2B`
- Example: `2023-05-03T00:00:00%2B02:00`

### Behaviour
- Both `startDate` and `endDate` are **inclusive**
- If omitted, dates are inferred from the dataset's date policy
- All policy limits (Max Window, Max Age From Now) apply simultaneously

### Date Policy Terms
| Term | Meaning |
|---|---|
| Default Window | Time span used when one or both dates are missing |
| Max Window | Largest allowed time span per request |
| Max Age From Now | How far back in time data may be requested |

### Common errors
- `400 Bad Request` → date window exceeds Max Window, or malformed/unencoded date
- `404 Not Found` → entity ID doesn't exist or has no data for period
- `403 Forbidden` → missing `Accept` or `User-Agent` header

---

## Production Groups

From `/production-groups` endpoint:

| ID | Name | Description |
|---|---|---|
| `solar` | Solar | Solar energy converted to electricity |
| `hydro` | Hydro | Moving water energy converted to electricity |
| `wind` | Wind | Wind energy converted to electricity |
| `thermal` | Thermal | Heat energy converted to electricity |
| `nuclear` | Nuclear | Nuclear reactor as heat source |
| `other` | Other | Other unspecified technology |
| `*` | (wildcard) | Filter value only — not a real group |

Norwegian display names (use these in UI):
| ID | Norsk |
|---|---|
| `solar` | Solkraft |
| `hydro` | Vannkraft |
| `wind` | Vindkraft |
| `thermal` | Varmekraft |
| `nuclear` | Kjernekraft |
| `other` | Annet |

---

## Metering Point Types

| Code | English | Norsk | Description |
|---|---|---|---|
| E18 | Grid production | Produksjon | Large-scale grid-connected production |
| E19 | Prosumer | Plusspunkt | Local/small-scale combined production+consumption |

**Never show raw codes (E18, E19) in the UI. Always use Norwegian display names.**

---

## Open Datasets — Price Areas (`/price-areas`)

| Dataset name | Description | Resolution | Max window |
|---|---|---|---|
| `INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MBA_DAILY` | Installed capacity per metering type and production group | Daily | 1 month |
| `PRODUCTION_PER_GROUP_MBA_HOUR` | Production per production group | Hourly | 1 month |
| `PRODUCTION_PER_GROUP_MBA_15MIN` | Production per production group | 15 min | 1 month |
| `PRODUCTION_PER_MBA_15MIN` | Total production | 15 min | 1 month |
| `CONSUMPTION_PER_GROUP_MBA_HOUR` | Consumption per consumption group | Hourly | 1 month |
| `LOSS_PER_MBA_HOUR` | Network loss | Hourly | 1 month |
| `EXCHANGE_PER_MBA_HOUR` | Exchange with adjacent price areas | Hourly | 1 month |
| `EXCHANGE_PER_MBA_15MIN` | Exchange with adjacent price areas | 15 min | 1 month |
| `COMPLETENESS_DAILY_PER_MBA` | Data completeness (metering read counts) | Daily | 1 month |
| `METERING_VALUE_COMPARISON_EAC_PER_MONTH` | Estimated monthly consumption by EAC | Monthly | 3 years + 41 days |
| `NORGESPRIS_CONSUMPTION_PER_GROUP_EAC_MBA` | Norgespris consumption by EAC range | Yearly | 3 years + 41 days |

Consumption groups for price area datasets: `household`, `cabin`, `primary`, `secondary`, `tertiary`

---

## Open Datasets — Municipalities (`/municipalities`)

| Dataset name | Description | Resolution | Max window |
|---|---|---|---|
| `INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_DAILY` | Installed capacity per metering type and production group | Daily | 1 month |
| `INSTALLED_CAPACITY_PER_METERING_POINT_TYPE_GROUP_MUNICIPALITY_BASIC_STATISTICAL_UNIT_DAILY` | Installed capacity per BSU (grunnkrets) | Daily | 1 month |
| `CONSUMPTION_PER_GROUP_MUNICIPALITY_HOUR` | Consumption per consumption group | Hourly | 1 day |
| `PRODUCTION_PER_METERING_POINT_TYPE_MUNICIPALITY_HOUR` | Production per metering type | Hourly | 1 day |
| `CONSUMPTION_PER_GROUP_MUNICIPALITY_BASIC_STATISTICAL_UNIT_HOUR` | Consumption per BSU | Hourly | 1 day |
| `MAX_CONSUMPTION_PER_EAC_MUNICIPALITY_BASIC_STATISTICAL_UNIT_MONTH` | Max hourly consumption per BSU | Monthly | 1 year |

---

## Dataset Response Schema — Installed Capacity (Municipality)

```json
{
  "meta": { "created": "ISO8601", "lastUpdated": "ISO8601" },
  "links": { "self": "string" },
  "data": [
    {
      "type": "municipality",
      "id": "1822",
      "attributes": {
        "municipalityNumber": "1822",
        "name": "Leirfjord",
        "nameNo": "Leirfjord",
        "installedCapacityPerMeteringPointTypeGroupMunicipalityDaily": [
          {
            "usageDateId": 20230503,
            "municipalityId": "1822",
            "meteringPointTypeCode": "E18",
            "productionGroup": "hydro",
            "installedCapacity": 26200.0,
            "lastUpdatedTime": "ISO8601"
          }
        ]
      }
    }
  ]
}
```

## Dataset Response Schema — Installed Capacity (Price Area)

```json
{
  "data": [
    {
      "type": "price-area",
      "id": "NO1",
      "attributes": {
        "priceAreaId": "NO1",
        "installedCapacityPerMeteringPointTypeGroupMbaDaily": [
          {
            "usageDateId": 20230503,
            "priceAreaId": "NO1",
            "meteringPointTypeCode": "E18",
            "productionGroup": "hydro",
            "installedCapacity": 26200.0,
            "lastUpdatedTime": "ISO8601"
          }
        ]
      }
    }
  ]
}
```
Note: price area response schema is inferred — verify against actual response before implementing.

---

## Known Issues
- Municipality `name`/`nameNo` may have UTF-8 mojibake — httpx handles correctly by default
- `data` array is unordered
- A municipality/price area only appears if it has data for the queried period
- No `meteringPointCount` in installed capacity datasets — only `installedCapacity` (kW)
- BSU dataset routes through `/municipalities/{id}` with BSU dataset name — not a separate endpoint

---

## Python Client Pattern

```python
import httpx
from datetime import date
from calendar import monthrange

BASE_URL = "https://api.elhub.no/energy-data/v0"


def _date_param(d: date) -> str:
    return f"{d.isoformat()}T00:00:00+02:00"


def _month_window(year: int, month: int) -> tuple[date, date]:
    """Return (first, last) day of a calendar month — never exceeds 1-month limit."""
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def fetch_geo_level(
    endpoint: str,           # e.g. "municipalities" or "price-areas"
    dataset: str,            # full dataset name constant
    start: date,
    end: date,
    entity_id: str | None = None,
) -> dict:
    """Generic fetch for any geo level and dataset. Max window: 1 month."""
    url = f"{BASE_URL}/{endpoint}"
    if entity_id:
        url += f"/{entity_id}"
    params = {
        "dataset": dataset,
        "startDate": _date_param(start),
        "endDate": _date_param(end),
    }
    r = httpx.get(url, params=params)
    if r.status_code == 404:
        return {"data": []}
    r.raise_for_status()
    return r.json()
```

---

## Geography Join
- Municipality IDs → `kommunenummer` in `Kommuner-S.geojson` (robhop/fylker-og-kommuner)
- Price areas → use `Fylker-S.geojson` or a price area polygon GeoJSON (to be sourced)
- GeoJSON property keys: `kommunenummer`, `kommunenavn`, `name`
- CRS: WGS84, coastal-clipped
