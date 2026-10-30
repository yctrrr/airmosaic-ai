---
name: spatial-analysis
description: Match spatial points and polygons, transform verified coordinates and build maps through separate R or Python paths; guide raster and provider-specific geocoding tasks with explicit accuracy and privacy requirements.
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
| Nearest/distance and raster transfer | Library guidance; task-specific adaptation and verification required |
| Geocoding | Local-gazetteer/provider guidance; no default online client or live verification |

No new tool ID, run-tool/MCP adapter, automatic configuration loader or geocoder is registered. Direct helpers do not inherit runner path/credential protections and do not read data or export files when loaded.

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

Each language checks one matched point, one ambiguous boundary and one unmatched point, coordinate round-trip, four plot builds and refusal cases. Python was checked in an isolated dependency environment; the main project environment was not changed. No real geocoding request or raster validation was performed.

Keep shared data in external `AIRMOSAIC_ASSETS_DIR/data/<stage>/<dataset>/<version>/`, non-secret settings in `AIRMOSAIC_CONFIG_DIR` and project outputs under external `assets/results/<project_id>/`. Do not expose residential/private addresses, exact sensitive locations, tokens, provider URLs containing credentials or personal filesystem paths. Online requests require the selected provider and authorized scope; a client library does not grant service access.
