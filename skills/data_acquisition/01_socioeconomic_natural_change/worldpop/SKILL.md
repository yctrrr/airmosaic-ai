---
name: worldpop
description: Discover and optionally download WorldPop population files with worldpop_download. Use for country, year and product acquisition; zonal analysis requires separate implementation.
---

# WorldPop Data Acquisition

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


> Invocation status: `worldpop_download` supports metadata discovery and optional download through `run-tool`. Zonal statistics have no standalone executable tool.

Current local status: official Hub metadata and a direct Global2 small-file acquisition are verified. Runner preflight passes, but the real catalog call has not passed. See [interface status](references/worldpop-api.md). The year filter matches popyear exactly, accepting integer values or integer text and rejecting missing, boolean, floating-point or non-exact years. Check other product conditions separately.

Read the [WorldPop method](../../../../methods/01_socioeconomic_natural_change/worldpop.md) for products, provenance, uncertainty and normalization. Follow the [public-catalog small-file example](references/first-download-example.md) for first acquisition; no account or token is required.

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md) and [execution guide](../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `output/<run_id>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

Use this skill to acquire WorldPop population products on demand for AirMosaic AI. Download only requested countries, years, and products. Keep raster files and derived tables in the local workspace, not in GitHub.

## Official Interfaces

- Current data catalog and script endpoint: `https://hub.worldpop.org/rest/data`; the script does not start from the legacy redirecting address.
- Separate Global2 regional statistics service: `https://api.worldpop.org/v2/`; no registered adapter or live statistics validation here.
- Data file host commonly returned by metadata: `https://data.worldpop.org`

WorldPop documents an API rate limit. Cache metadata and downloaded files locally rather than repeatedly querying the same products.

## Results and cache

`run-tool` writes this task to `${AIRMOSAIC_LOCAL_WORKSPACE}/output/<run_id>/worldpop_download/`: metadata JSON/CSV under `metadata/`, downloaded files under `raw/<iso3>/<project>/<year>/`. The receipt is under `runs/<run_id>/record.json` and omits parameter values and filenames.

`${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/worldpop/` is the reusable cache location, not the runner's output destination. Publishing validated task files into that cache is a separate authorized operation; no automatic cache promotion, raster resampling or zonal statistics is implemented.

## Registered execution

Use `worldpop_download` from the repository root. Inspect its manifest with `describe-tool`; the tool ID is the CLI argument, not a key in the parameter JSON.

```powershell
python -m airmosaic_core.cli describe-tool worldpop_download
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run
# Discovery also uses the network and writes metadata; execute only within task authorization.
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --allow-network
```

The public example contains:

```json
{"project":"wpgp","iso3":"CHN","year":2020,"download":false,"limit":1}
```

Only `project` is required from the caller; the runner supplies `root`. `year` and `limit` are integers, `download` is boolean, and `contains` / `extensions` are comma-separated strings, not arrays. Use an explicit non-secret JSON in CONFIG_DIR for task-specific parameters. Set `download` to `true` only for an authorized file download; even `false` still performs remote metadata discovery. A dry-run without `--allow-network` reports a permission blocker and performs no request.

## Agent execution boundary

Call only the registered ID through `run-tool`; do not invoke the script directly to bypass a rejected path or permission check. Metadata filters are not proof of year/product suitability. A schema-valid ISO3 or project alias may still be unavailable remotely. No automatic download-result, raster CRS, population-total or scientific validation is provided; complete the checklist below on local task artifacts before sharing or reuse.

## Product Selection Notes

Use exact WorldPop project/product names when known. For ambiguous requests, first run metadata discovery and inspect product titles, file names, years, and resolution before downloading.

Population discovery uses project aliases under the `pop` API group, for example `wpgp` for Global per country 2000-2020.

Current Global2 products are a separate family. The verified small example uses `G2_CN_POP_R25A_1km`, LIE, `popyear = 2020`, R2025A v1, constrained and UN-adjusted. Query actual aliases and inspect metadata rather than infer Global2 support from an old alias or date match.

Typical filtering dimensions:

- country ISO3 code;
- product/project alias;
- year;
- file extension such as `.tif`, `.tiff`, `.zip`, `.csv`;
- sex/age-specific wording in `title`, `data_file`, or metadata fields;
- UN-adjusted versus unadjusted product wording;
- constrained versus unconstrained product wording.

## Validation Checklist

- Confirm files are non-empty and match expected extension.
- Preserve metadata sidecars next to downloaded files.
- Record WorldPop project/product alias, country, year, and download URL.
- Verify the explicit `popyear`, unit, product version, constraint/adjustment choice, CRS, grid, NoData and finite nonnegative valid values; metadata release dates and a text match are insufficient.
- Do not unzip or resample rasters unless the caller requests it.
- Do not commit raw rasters, derived rasters, cache manifests, or local paths to GitHub.

## References

- `references/worldpop-api.md`: API endpoint notes and metadata fields.
- `references/privacy-redaction-rules.md`: sanitization checklist.
