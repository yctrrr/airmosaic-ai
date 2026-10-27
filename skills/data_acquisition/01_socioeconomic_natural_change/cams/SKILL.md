---
name: cams-acquisition
description: Plan CAMS atmospheric composition downloads through the Copernicus ADS web form or cdsapi, separating EAC4 reanalysis from forecasts and checking species, levels and valid time. Documentation only; no run-tool adapter.
---

# CAMS atmospheric-composition acquisition

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status: reference.** Includes website instructions, Python API examples and request JSON; no run-tool adapter.

## Workflow

Read the [EAC4/forecast data method](../../../../methods/01_socioeconomic_natural_change/cams.md) before selecting a product: producer, model/assimilation and representativeness errors, units, initialization/valid times, system versions and daily coverage. Gridded composition fields are not station observations.

1. Read the [method](../../../../methods/01_socioeconomic_natural_change/cams.md) and choose EAC4 historical reanalysis or operational forecasts; do not infer products from old NRT filenames.
2. Define variables, single/model/pressure levels, region, dates and times. Forecasts also require initialization, leadtime and a rule for valid times and overlapping forecasts.
3. Use ADS through the [download guide](../../../../harness/usage/copernicus-downloads.md). The user logs in and accepts applicable terms; generate requests from the current form. A CDS endpoint cannot substitute for ADS.
4. Save reviewed non-secret requests in CONFIG_DIR. Validate a separately authorized small batch before planning bulk acquisition; documentation maintenance does not download/read original data.
5. Check format, species, vertical coordinates, valid times, grid and units; hand off provenance and limitations without labeling reanalysis/forecast as station observations.

## Two acquisition routes

| Route | Sequence |
|---|---|
| Website | User logs into ADS → opens product Download page → checks parameters and terms → submits → waits → saves → decodes and validates |
| Python API | Prepare request JSON → choose `cams-eac4` or `cams-forecast` → fix ADS endpoint → official client uses authorized credentials → submit → save → decode and validate |

The public ADS API endpoint is `https://ads.atmosphere.copernicus.eu/api`. With explicit authorization, the official client may internally reuse the user's existing `.cdsapirc`; code sets ADS explicitly without editing the secret file. User-hidden terminal input is another mode. The user handles access, terms and token storage; the agent does not inspect token pages or file contents.

## Verified EAC4 example

Verified on 2026-10-26: surface `particulate_matter_2.5um`, 2024-01-01 00:00 UTC, north/west/south/east `[40.5, 110.25, 35.25, 115.5]`, GRIB. Accepted 17:57:05, downloaded 17:57:58, validated 17:57:59 Beijing time (UTC+8).

Follow the [EAC4 example](references/eac4-api-download-example.md) with `selection = "cams-eac4"` and `credential_mode = "existing_file"`. The sample is a 0.75°, 8×8 grid in kg/m³.

## Verified global-forecast example

Verified on 2026-10-26: surface PM2.5, initialization 2026-10-25 00:00 UTC, leads 0/3/6 hours, north/west/south/east `[40, 110, 36, 114]`, GRIB. Accepted 18:11:02; downloaded and validated 18:12:23 Beijing time (UTC+8).

Follow the [forecast example](references/forecast-api-download-example.md) with `selection = "cams-forecast"` and `credential_mode = "existing_file"`. Preserve initialization, lead and valid time as separate keys. Three 0.4°, 11×11 fields were checked in kg/m³.

## Boundaries

- Requests: `AIRMOSAIC_CONFIG_DIR/copernicus/`; downloads: `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/cams/`; validated cache: `data_cache/cams/`. Dedicated browser sessions may use `AIRMOSAIC_AUTH_DIR/browser_profiles/copernicus-ads/`; variables do not create sessions or authenticate users.
- Tokens belong in a secret manager. Do not create plaintext secret templates, copy cookies or record signed links. Explicitly select ADS and authorized credentials rather than relying on unreviewed defaults.
- Do not interchange column totals, mixing ratios, surface mass concentrations and AOD, or automatically splice EAC4 and forecasts.
- The [PM2.5 station skill](../../03_atmospheric_transport/pm25-stations/SKILL.md) handles observational provenance and preparation. CAMS remains gridded even for PM2.5. Check station-history validity, periods, units and representativeness before comparison; no automatic matching/correction. Primary stage is 01, referenced by 03/04.
- Conversion to GEOS-Chem species/grids/boundaries and health-model inputs is not implemented. This guide supplies no OS isolation, automatic sanitization or formal scientific acceptance.
