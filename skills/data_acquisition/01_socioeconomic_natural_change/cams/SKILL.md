---
name: cams-acquisition
description: Acquire CAMS EAC4 reanalysis or global forecasts through ADS or official cdsapi, preserving species, levels, forecast initialization and valid time. Reference guidance without a run-tool adapter.
compatibility: "Official cdsapi client or ADS browser access; GRIB verification requires ecCodes"
metadata:
  version: "1.1.0"
  reviewed: "2026-10-30"
---

# CAMS acquisition

**English** | [中文](SKILL_ZH.md)

Use ADS for historical EAC4 or global composition forecasts; this skill has no executable tool ID. Choose the product and physical interpretation with the [CAMS method](../../../../methods/01_socioeconomic_natural_change/cams.md).

## Configure and acquire

1. Fix product, species, surface/model/pressure level, region and UTC sampling. Forecasts additionally need initialization, leads and an overlap rule for valid times. European regional products need their own requests.
2. The user signs into [ADS](https://ads.atmosphere.copernicus.eu/), accepts applicable terms and prepares credentials. The official client may use the user's authorized existing secret file internally, without agent inspection or file changes.
3. Generate a request from the current ADS form. Use the website directly or the [official-client code](../era5/references/operations.md), selecting `cams-eac4` or `cams-forecast`. The code fixes `https://ads.atmosphere.copernicus.eu/api`; CDS cannot substitute for ADS.
4. Validate a small batch before expansion. After interruption, check the original task state before retrying.

## Check and deliver

Decode each field and compare species, vertical coordinate, units, grid and sampling against the request. Retain initialization, lead and `valid_time` separately. Convert PM2.5 from kg/m³ to µg/m³ only when those are the declared source units, multiplying by `10^9` and saving a derived field.

Historical checks on 2026-10-26: [EAC4](references/eac4-api-download-example.md) checked one surface PM2.5 field at 2024-01-01 00:00 UTC, 0.75°, 8×8; [forecast](references/forecast-api-download-example.md) checked initialization 2026-10-25 00:00 UTC, leads 0/3/6 hours, 0.4°, 11×11. Both had finite values without missing points; neither establishes full-day coverage or station accuracy.

For total 550 nm AOD, use the separate [variable/request guide](references/eac4-aod.md). Its public form option and request example were checked on 2026-10-30; actual AOD retrieval/decoding remains unverified. Do not identify EAC4 AOD as an ERA5 field.

Store requests in `AIRMOSAIC_CONFIG_DIR/copernicus/`, downloads under `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/cams/`, reviewed reusable products under `data/01_socioeconomic_natural_change/<product-name>/<version>/`. Keep assets/configuration/authentication roots separate outside Git and exclude tokens/signed URLs from records. GEOS-Chem species/grid/boundary conversion requires separate adaptation.
