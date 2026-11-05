---
name: spatial-analysis
description: Match spatial points and polygons, transform verified coordinates and build maps through separate R or Python paths; guide raster and provider-specific geocoding tasks with explicit accuracy and privacy requirements.
compatibility: "Bilinear: base R or Python with NumPy/pandas; vector and mapping routes require separately declared R/Python packages"
metadata:
  version: "1.1.0"
  reviewed: "2026-11-01"
---

# Spatial analysis and mapping

**English** | [中文](SKILL_ZH.md)

Use the [method](../../../../methods/shared/spatial_analysis.md) to choose relations, CRS, support and precision. [Operations](references/operations.md) supplies common configuration and result checks. Then choose the [R path](references/r-path.md) or [Python path](references/python-path.md); [geocoding](references/geocoding.md) has separate source/provider requirements.

## Current capability

| Capability | Status |
|---|---|
| Projected point/polygon matching | R and Python functions; preserve single, missing and ambiguous matches |
| Verified coordinate transformation | R and Python functions; require a known source CRS and offline PROJ |
| Point/polygon and rectangular grid/facet maps | R patterns generalized from member helpers; corresponding Python functions; both synthetically checked |
| Regional regular-grid bilinear sampling | Pure R and Python functions; explicit EPSG:4326, auditable four-neighbor weights and missing support |
| Conditional angular-grid alignment | Separate Python API requires the explicit unverified-datum assumption; does not transform coordinates or establish EPSG identity; vectorized series retain missing-support rules |
| ERA5 local-day NetCDF | Direct five-variable ZIP/NetCDF reader; exact grid/date/unit checks and bounded unpacking; [daily route](../../../data_acquisition/01_socioeconomic_natural_change/era5/references/daily-statistics.md) |
| Complete local-day grid means | Pure Python function for explicit 1 h/3 h instantaneous samples and Asia/Shanghai days |
| Native GRIB regular grids | Direct ecCodes Python reader; explicit file/variable contracts, bounded selection, default duplicate refusal with opt-in encoded-message SHA256 identity checks, no resampling; [interface](references/grib-grid.md) |
| Nearest/distance and raster transfer | Library guidance; task-specific adaptation and verification required |
| Geocoding | Local-gazetteer/provider guidance; no default online client or live verification |

No new tool ID, run-tool/MCP adapter, automatic configuration loader or geocoder is registered. Direct helpers do not inherit runner path/credential protections and do not read data or export files when loaded.

Direct modules: [Python bilinear](scripts/python/bilinear_helpers.py), [R bilinear](scripts/r/bilinear_helpers.R), [Python daily grids](scripts/python/grid_daily.py), and the [GRIB reader](scripts/python/grib_grid.py). Their references provide explicit arguments and runnable checks.

Additional direct modules: [daily NetCDF](scripts/python/era5_daily.py) and [conditional partition guards](scripts/python/partition_guards.py). The bilinear module additionally exposes `bilinear_weights_under_alignment_assumption(..., assumption="angular_lon_lat_aligned_without_verified_datum")` and `sample_bilinear_series(values, weights)` for explicit engineering alignment and `[time,y,x]` arrays. Keep the returned unverified-metadata declaration; these calls do not establish a datum or scientific acceptance.

## Use the skill

1. Declare authorized input versions, source geometry/CRS, IDs, value units, boundary date, operation and fresh external project outputs. Explain the relation/distance, coordinate accuracy and weighting choices before calculation.
2. Inspect geometry validity, coordinate conventions, keys and match cardinality. Missing CRS or unresolved provider coordinates require source review.
3. Choose R or Python from the supported environment; do not install or download implicitly. Verify engine/library versions. Keep private source paths and credentials in their personal mechanisms.
4. Load only the selected reviewed module, pass data/fields/CRS explicitly, then check returned matches or plot objects. Both routes preserve the same matching fields. Ambiguous and unmatched cases need an explicit resolution policy; no automatic nearest fallback.
5. Check actual source/result identity, keys, distances/units, coverage, scale limits and appropriate totals. Save QA with results, preserve inputs and request scientific review before promoting derived data.

From repository root, run the synthetic check without reading business data or writing outputs:

```sh
Rscript --vanilla skills/model/shared/spatial_analysis/examples/r/synthetic_spatial.R
python skills/model/shared/spatial_analysis/examples/python/synthetic_spatial.py
```

These spatial examples check one matched point, one ambiguous boundary and one unmatched point, coordinate round-trip, four plot builds and refusal cases. Python was checked in an isolated dependency environment; the main project environment was not changed. The language-path pages additionally provide in-memory bilinear examples and a Python daily-grid example. Bilinear helpers have separate synthetic checks; this does not establish real-data integration or scientific acceptance. No real geocoding request was performed; general raster reprojection/conservation remains task-specific.

Keep task inputs and outputs with their authorized external project, non-secret private location mappings in `AIRMOSAIC_CONFIG_DIR` and credentials separately protected. Human scientific review determines asset admission; this skill does not prescribe asset subdirectories. Do not expose residential/private addresses, exact sensitive locations, tokens, provider URLs containing credentials or personal filesystem paths. Online requests require the selected provider and authorized scope; a client library does not grant service access.
