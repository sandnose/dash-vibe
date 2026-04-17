# Raw source data

## grunnkretser.zip

**Source:** [Geonorge — Statistiske enheter grunnkretser](https://kartkatalog.geonorge.no/metadata/statistiske-enheter-grunnkretser/51d279f8-e2be-4f5e-9f72-1a53f7535ec1)  
**Producer:** Kartverket / SSB  
**License:** [Norge digitalt / CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)  
**Projection:** EUREF89 UTM sone 33 (EPSG:25833)  
**Format:** GeoJSON (inside ZIP)

### Contents
Polygon boundaries for all ~15 000 grunnkretser in Norway.

Key properties per feature:
- `grunnkretsnummer` — 8-digit code, first 4 digits = kommunenummer
- `grunnkretsnavn` — name (used to join against Elhub `basicStatisticalUnit`)

### How to process
Run `just build-grunnkretser` (see justfile) to:
1. Unzip and read the GeoJSON
2. Reproject from EPSG:25833 to WGS84 (EPSG:4326)
3. Split by `grunnkretsnummer[:4]` into per-municipality files
4. Write to `data/grunnkretser/{kommunenummer}.geojson`

Only municipalities that have BSU data in Elhub need to be processed —
check `elhub/datasets.py` for `INSTALLED_CAPACITY_MUNICIPALITY_BSU`.

### Do not commit the processed files
`data/grunnkretser/*.geojson` is gitignored — generated at build time.
`data/raw/grunnkretser.zip` is committed as the canonical source.
