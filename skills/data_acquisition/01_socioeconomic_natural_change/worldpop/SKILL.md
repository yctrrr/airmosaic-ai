---
name: worldpop
description: Discover and optionally download WorldPop population products through worldpop_download; select country, exact population year and release. Raster analysis is separate.
---

# WorldPop acquisition

**English** | [中文](SKILL_ZH.md)

Use `worldpop_download` for public catalog discovery and optional file download. Python 3.10+, the installed project and `requests` are required. Set separate existing `AIRMOSAIC_ASSETS_DIR`, `AIRMOSAIC_CONFIG_DIR` and `AIRMOSAIC_AUTH_DIR` roots outside Git; public WorldPop requests need no account or token.

Historical status (2026-10-26): official Hub metadata and a direct Global2 small-file acquisition passed; runner preflight passed but its real catalog call failed. See [interface status](references/worldpop-api.md) and [direct example](references/first-download-example.md). These routes have distinct evidence.

## Configure and run

Choose product, country, `popyear`, release, resolution, constrained/unconstrained and adjustment scheme using the [WorldPop method](../../../../methods/01_socioeconomic_natural_change/worldpop.md). The included [parameter file](../../../../config/examples/run-tool/worldpop.json) is:

```json
{"project":"wpgp","iso3":"CHN","year":2020,"download":false,"limit":1}
```

Copy and adapt it into CONFIG_DIR. `project` is the WorldPop alias, not the AirMosaic project ID; the runner supplies `root`. `year` and `limit` are integers (limit 1–100), `download` is boolean, `contains`/`extensions` are comma-separated strings. Year filtering matches `popyear` exactly, accepting integer/integer-text metadata but excluding missing, boolean or floating years. Check other product conditions separately; `limit` acts after filtering, not on the remote response.

```sh
python -m runtime.cli describe-tool worldpop_download
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --allow-network --dry-run
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --allow-network
```

Check `can_execute` and `blockers`. Dry-run sends no request; `download=false` during actual execution still uses the network and writes metadata. Set `download=true` for scoped file acquisition. Run from the repository root; use the personal parameter path for your task.

## Check outputs

Outputs: `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/worldpop_download/`, with JSON/CSV under `metadata/` and files under `raw/<iso3>/<project>/<year>/`. Check actual result status, metadata count and matches, filenames/nonempty downloads, then decode requested rasters to check units, CRS, grid, NoData, finite nonnegative valid values and coverage. No matches is not a successful requested acquisition.

The [verified direct example](references/first-download-example.md) used `G2_CN_POP_R25A_1km`, LIE, 2020, R2025A v1, constrained and UN-adjusted; it does not validate the legacy `wpgp` alias for Global2. Regional-statistics API v2, resampling and zonal statistics have no registered adapter here. Reusable cache `data/01_socioeconomic_natural_change/WorldPop/<version>/` is populated only after separate review; the runner does not promote files automatically.
