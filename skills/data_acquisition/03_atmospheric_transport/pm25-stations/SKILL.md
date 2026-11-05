---
name: pm25-station-acquisition
description: Select PM2.5 station sources and prepare observation tables with explicit time, station-history and quality rules. Includes direct Python preparation helpers; no downloader or run-tool adapter.
compatibility: "Direct preparation requires Python with NumPy and pandas; no downloader or registered execution adapter"
metadata:
  version: "1.1.0"
  reviewed: "2026-11-01"
---

# PM2.5 station acquisition and preparation

**English** | [中文](SKILL_ZH.md)

Select original hourly publication records or a processed daily product before acquisition. This skill has direct Python helpers in [`scripts/prepare_hourly.py`](scripts/prepare_hourly.py) and [`scripts/prepare_daily_product.py`](scripts/prepare_daily_product.py), but no tool ID, downloader or `run-tool` adapter. Use the [station method](../../../../methods/03_atmospheric_transport/pm25_stations.md) for provenance, concentration state and completeness, the [source table](../../../../methods/03_atmospheric_transport/pm25_stations_sources.md) for coverage, and the [homogenized method](../../../../methods/03_atmospheric_transport/pm25_homogenized.md) for adjusted daily values.

## Acquire

Define network, dates, pollutants, station scope, product type and destination. Public routes with historical checks on 2026-10-26:

- [Quotsoft single-day CSV](references/single-day-example.md): 2024-01-01 station archive, hourly PM2.5 reshaped to long form; time-zone/hour-interval semantics and historical station coordinates remain unresolved.
- [PANGAEA homogenized release](references/homogenized-download-example.md): 2015–2019 release and one seven-day series sample; series IDs are not confirmed national station codes.

Both require no account/API key. Follow the selected example for actual HTTPS/file handling and bounded requests; neither is a `run-tool` entry. Preserve original files, source/version/license, acquisition time and checksums. Review the original request state after failure rather than silently switching providers.

## Prepare and check

For existing legacy daily tables, use [daily-product preparation](references/daily-product.md). It preserves the requested calendar without reaggregation; legacy row counts are not verified valid hours. Explicit user-accepted date/CRS/history assumptions permit engineering pilots only.

For executable `importlib` loading, local CSV extraction, configuration and result checks, read [hourly preparation](references/hourly-preparation.md). The helper does not acquire files or verify source metadata. A reviewed time declaration is required for daily computation; a synthetic example is not evidence of Quotsoft semantics.

1. Verify the actual schema and missing symbols. Select hourly `PM2.5` explicitly, excluding `PM2.5_24h` and AQI. Reshape with string station IDs and retain original date/hour labels.
2. Define unique source/network/station/time/observation-type keys; report conflicting duplicates. Count finite, valid, unique observed intervals rather than rows.
3. Join station history by explicit ID and validity period; check uniqueness and unmatched rows. Unknown historical coordinates remain unknown.
4. Resolve time zone, hour start/end and day assignment before aggregation. Use the selected dated completeness policy; under the GB 3095 20-hour daily rule, keep insufficient days missing with counts and reasons. Do not count imputation toward observed hours.
5. Deliver long tables, mappings, station-history version and duplicate/missingness/coverage summaries using the [preparation method](../../../../methods/03_atmospheric_transport/pm25_stations_preparation.md). Existing daily homogenized products do not pass through hourly aggregation.

Keep non-secret task settings under `${AIRMOSAIC_CONFIG_DIR}/projects/<project_id>/`. Keep originals, checksums, actual code/settings, derived tables and review evidence with the corresponding project's `results/`, following the [project convention](../../../../projects/README.md). Private project results stay outside Git. Current registered adapters retain their implemented output boundaries; this direct helper does not create an adapter. Only a human scientific decision can admit selected outputs to `assets/`, following the [review contract](../../../../harness/assets.md); no internal asset layout is prescribed here. Keep authentication separate when a selected provider requires it. Historical scripts require manual adaptation; see [legacy interface notes](references/preparation-adaptation.md).

The [Quotsoft source page](https://quotsoft.net/air/) documents dated station-list filenames and longitude/latitude fields, with complete lists linked through a cloud drive. It does not establish historical coordinate validity, a coordinate reference system, timezone or midnight label mapping. Obtain those separately before spatial matching or daily aggregation; do not substitute current coordinates for historical positions.
