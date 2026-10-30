---
name: ihme-gbd-results
description: Fetch scoped IHME GBD cause results through ihme_gbd_fetch_results using an existing authorized local browser session and verified round/dimension IDs.
---

# IHME GBD Results

**English** | [中文](SKILL_ZH.md)

Use `ihme_gbd_fetch_results` for cause-result tables in an existing task-owned loopback CDP browser session. It does not launch a browser or authenticate. Python 3.10+, the installed project, `pandas`, `requests` and `websocket-client` are required.

Select indicators using the [GBD method](../../../../methods/04_integrated_impacts/ihme_gbd.md) and [availability table](../../../../methods/04_integrated_impacts/ihme_gbd_availability.md): deaths, YLLs, YLDs, DALYs, incidence/prevalence have cause selections; risk attribution, SEV, HALE, population, fertility and life tables need their own verified route/dimensions. `context` alone does not supply missing risk/topic parameters; `population_group` does not request population counts.

## Prepare and run

1. The user opens [GBD Results](https://vizhub.healthdata.org/gbd-results/), handles terms/login/verification and confirms scope. For ordinary website exports, follow the [first-download guide](references/first-download-guide.md); no CDP is required.
2. For the adapter, use a task-owned Chromium profile in `AIRMOSAIC_AUTH_DIR/browser_profiles/ihme-gbd/` with a loopback-only CDP port. Verify port ownership and current page selections. Keep executable mappings and non-secret task JSON in CONFIG_DIR; do not inspect/copy authentication state.
3. Adapt the [example JSON](../../../../config/examples/run-tool/gbd.json). Required `years`, `locations`, `causes`, `ages`, `sexes`, `measures`, `metrics` are comma-separated numeric strings (for example `"ages":"10,11"`), not arrays/ranges. Set verified integer `version`, `port`, `population_group`, `wait_ms` and string `context` as needed; runner allocates `out`.

```powershell
python -m runtime.cli describe-tool ihme_gbd_fetch_results
$gbdParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gbd-task.json"
python -m runtime.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --dry-run --allow-network --confirm-browser-session
python -m runtime.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --allow-network --confirm-browser-session --timeout 300
```

Run from the repository root with separate existing asset/configuration/authentication roots outside Git. Check `can_execute`/`blockers`; session confirmation does not verify login or IDs. Historical defaults (`version=8352`, `context=cause`, `population_group=1`, `port=9222`) are syntax examples, not a current release mapping.

## Check and deliver

The runner writes `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/04_integrated_impacts/ihme_gbd_fetch_results/results.csv` and `results.csv.json`. Check sidecar error/freshness, returned dimensions, actual rows, duplicate keys, missing combinations, finite values and `lower ≤ val ≤ upper` where bounds exist. Never accept stale rows retained after errors. Source-to-derived checks are in [processing validation](references/processing-validation.md).

Historical evidence on 2026-10-26: the website route acquired a 717-byte ZIP containing one global/all-cause/2023/all-age/both-sex/deaths/number record with 18 columns. The real runner call remains unverified pending task CDP ownership checks. The [availability table](../../../../methods/04_integrated_impacts/ihme_gbd_availability.md) preserves product coverage and unexecuted China/baseline plans.

Keep raw, processed and quality artifacts separate, preserving round and all dimensions. Cache publication to `data/04_integrated_impacts/GBD_MortalityRates/<version>/` follows separate review. Do not export account details, cookies or temporary task links.
