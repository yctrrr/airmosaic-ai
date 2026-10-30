---
name: era5-acquisition
description: Acquire scoped ERA5 meteorological fields through the CDS website or official cdsapi client and check their physical metadata. Reference guidance without a run-tool adapter.
---

# ERA5 acquisition

**English** | [中文](SKILL_ZH.md)

Use the CDS form or official Python client. This skill has no executable tool ID. Select variables and averaging with the [ERA5 method](../../../../methods/01_socioeconomic_natural_change/era5.md).

## Configure and acquire

1. Choose single levels, pressure levels, ERA5-Land or daily statistics explicitly; fix variables, levels, dates, UTC times and north/west/south/east bounds.
2. The user signs into [CDS](https://cds.climate.copernicus.eu/), accepts applicable dataset terms and prepares official-client credentials. The client may internally use an explicitly authorized existing `.cdsapirc`; do not inspect or copy it. Hidden token input remains an option in the existing [first-use guide](../../../../harness/usage/era5-first-api.md).
3. For the website route, submit the reviewed form and save its output to a fresh task folder. For API code and non-secret request configuration, use [official-client operations](references/operations.md). Confirm the request against the current product form before submitting.
4. Start with a bounded request; check its existing server state after interruption before resubmitting. Expand date/variable/level batches after the first content check.

## Check and deliver

Decode GRIB with ecCodes or NetCDF with a compatible reader. Check parameter identity, level, units, UTC/valid times, grid, finite values and missing time steps against the request. File size and download completion alone are insufficient.

The [2026-10-26 single-level example](references/api-download-example.md) checked one `2m_temperature` field for 2024-01-01 00:00 UTC: K, 0.25°, 21×21 points, no missing values. It is a historical content check, not a daily statistic or independent accuracy evaluation.

Keep non-secret requests in `AIRMOSAIC_CONFIG_DIR/copernicus/` and new downloads in `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/era5/`. Reusable versions use `data/01_socioeconomic_natural_change/ERA5/<version>/` after review. Keep configuration, assets and authentication roots separate outside Git; exclude tokens and signed URLs from records. ERA5 files require separate adaptation to GEOS-Chem input contracts.
