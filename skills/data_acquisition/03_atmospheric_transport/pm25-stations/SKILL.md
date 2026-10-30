---
name: pm25-station-acquisition
description: Select PM2.5 station sources and prepare observation tables with explicit time, station-history and quality rules. Reference guidance without a downloader or run-tool adapter.
---

# PM2.5 station acquisition and preparation

**English** | [中文](SKILL_ZH.md)

Select original hourly publication records or a processed daily product before acquisition. This reference has no tool ID or downloader. Use the [station method](../../../../methods/03_atmospheric_transport/pm25_stations.md) for provenance, concentration state and completeness, the [source table](../../../../methods/03_atmospheric_transport/pm25_stations_sources.md) for coverage, and the [homogenized method](../../../../methods/03_atmospheric_transport/pm25_homogenized.md) for adjusted daily values.

## Acquire

Define network, dates, pollutants, station scope, product type and destination. Public routes with historical checks on 2026-10-26:

- [Quotsoft single-day CSV](references/single-day-example.md): 2024-01-01 station archive, hourly PM2.5 reshaped to long form; time-zone/hour-interval semantics and historical station coordinates remain unresolved.
- [PANGAEA homogenized release](references/homogenized-download-example.md): 2015–2019 release and one seven-day series sample; series IDs are not confirmed national station codes.

Both require no account/API key. Follow the selected example for actual HTTPS/file handling and bounded requests; neither is a `run-tool` entry. Preserve original files, source/version/license, acquisition time and checksums. Review the original request state after failure rather than silently switching providers.

## Prepare and check

1. Verify the actual schema and missing symbols. Select hourly `PM2.5` explicitly, excluding `PM2.5_24h` and AQI. Reshape with string station IDs and retain original date/hour labels.
2. Define unique source/network/station/time/observation-type keys; report conflicting duplicates. Count finite, valid, unique observed intervals rather than rows.
3. Join station history by explicit ID and validity period; check uniqueness and unmatched rows. Unknown historical coordinates remain unknown.
4. Resolve time zone, hour start/end and day assignment before aggregation. Use the selected dated completeness policy; under the GB 3095 20-hour daily rule, keep insufficient days missing with counts and reasons. Do not count imputation toward observed hours.
5. Deliver long tables, mappings, station-history version and duplicate/missingness/coverage summaries using the [preparation method](../../../../methods/03_atmospheric_transport/pm25_stations_preparation.md). Existing daily homogenized products do not pass through hourly aggregation.

Store plans in `AIRMOSAIC_CONFIG_DIR/pm25-stations/` and task artifacts under `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/03_atmospheric_transport/pm25-stations/`, separating raw, processed, metadata and quality. Reviewed reusable data use `data/03_atmospheric_transport/PM25_Stations/<source>/<version>/`. Keep authentication separate in AUTH_DIR when a selected provider requires it. Historical scripts require manual adaptation; see [legacy interface notes](references/preparation-adaptation.md).
