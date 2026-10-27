---
name: ihme-gbd-results
description: Fetch scoped IHME GBD cause and mortality results with ihme_gbd_fetch_results through an existing user-authenticated browser after checking the round and dimension IDs. Population products require their own verified source and workflow.
---

# IHME GBD Results

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->

> Invocation status: `ihme_gbd_fetch_results` is enabled in `run-tool` for an existing authorized loopback browser session. It does not launch a browser or authenticate the user.

Read the [GBD method](../../../../methods/04_integrated_impacts/ihme_gbd.md) for provenance, uncertainty, counts/rates, age alignment and uncertainty intervals. Follow the [first-download guide](references/first-download-guide.md), keeping website access, fresh results, file acquisition and run-tool validation distinct.

Consult the [data-range guide](../../../../methods/04_integrated_impacts/ihme_gbd_availability.md) before selecting a product. Risk, exposure, population and life-table products require dedicated entry points. The adapter has no independent risk or other topic ID parameter; changing `context` alone does not establish support.

## Available GBD data

Use this table to select a product; verify valid rounds, locations, ages and measures on the current page or product record. GBD 2023 disease and risk estimates primarily cover 1990–2023. Check demographic and special-topic coverage separately. Sources are listed in the [data-range guide](../../../../methods/04_integrated_impacts/ihme_gbd_availability.md).

| Product | Common outputs | Route and project status |
|---|---|---|
| Deaths | Counts, rates and applicable proportions | Results → Cause; one global all-cause count export verified |
| YLLs | Years of life lost, counts and rates | Results → Cause; measure parameter supported, not individually verified |
| YLDs | Years lived with disability, counts and rates | Results → Cause; not individually verified |
| DALYs | Disability-adjusted life years, counts and rates | Results → Cause; not individually verified |
| Incidence / Prevalence | Counts and applicable rates/proportions | Results → Cause; check cause and age combinations |
| Risk-attributable burden | Attributable deaths, YLLs, YLDs, DALYs and applicable PAFs | Results → Risk; use the website or adapt risk-specific parameters |
| SEV | Summary exposure values | Dedicated selection; verify separately, not a PM2.5 concentration |
| HALE | Healthy life expectancy in years | Dedicated selection; verify product dimensions |
| All-cause mortality and life expectancy | Demographic mortality rates and life expectancy | Corresponding GHDx product; verify separately |
| Population, life tables and fertility | Age/sex population, life-table and fertility indicators | Results navigation or GHDx product; adapter export not verified |
| Other topics | Etiology, injury nature and impairment results where provided | Topic-specific selection; additional adapter parameters required |

Fix round, years, locations, cause/risk, ages, sexes, measure and metric before downloading. Start with a small query and expand only for a scoped task. Do not default to all combinations. Keep counts, rates and proportions distinct and preserve available `val`, `lower` and `upper` fields.

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md) and [execution guide](../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_ASSETS_DIR` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `results/<project_id>/<run_id>/04_integrated_impacts/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

Use this skill for IHME GBD Results acquisition and local processing. The skill does not store credentials, cookies, tokens, browser profiles, or personal paths. Raw exports and processed mortality tables must stay under the AirMosaic local workspace.

## Results and cache boundary

`run-tool` writes `results/<project_id>/<run_id>/04_integrated_impacts/ihme_gbd_fetch_results/results.csv` and its JSON sidecar. Raw/processed health tables stay local. Publishing a validated export into `${AIRMOSAIC_ASSETS_DIR}/data/04_integrated_impacts/GBD_MortalityRates/<version>/` is a separate authorized operation, not automatic runner behavior. Do not commit exports, account identity or browser artifacts.

## Workflow

1. Open `https://vizhub.healthdata.org/gbd-results/`. Let the user decide on terms, log in and complete any verification personally.
2. Check the visible round and all selected dimensions; start with the one-record example in the [first-download guide](references/first-download-guide.md).
3. Choose the website download procedure below, or the registered adapter route after verifying a task-owned loopback CDP session. Ordinary website downloads do not require remote debugging.
4. For the registered route, invoke `ihme_gbd_fetch_results` through `run-tool` as described under Registered execution; do not call the raw script to bypass runner checks. Internal PHP calls are not a fallback for blocked or stale results.
5. Save raw output separately from project-specific processed outputs. Neither route automatically publishes a cache.
6. Map IHME IDs and display names to local schemas explicitly; do not infer endpoint or age mappings from sort order alone.
7. Validate every processed output against raw IHME rows by key columns and numeric values, following the [processing checklist](references/processing-validation.md).

## Website download procedure

1. **Prepare the session:** open [GBD Results](https://vizhub.healthdata.org/gbd-results/). The user handles terms, login and access verification, then returns to the query page. Do not request credentials or account screenshots.
2. **Set the scope:** inspect every selected dimension. For the first test select GBD 2023, 2023, Global, All causes, All ages, Both sexes, Deaths and Number. Expect one record.
3. **Search and check:** submit once, wait for fresh results and verify labels and row counts. Hand verification prompts to the user. Do not accept old rows retained during loading or after an error.
4. **Submit the export:** click Download and select Both to retain IDs and names. This field option is separate from the Both-sexes selection. Review the scope and submit once.
5. **Obtain the file:** follow the progress link in the success message. When ready, download the ZIP from the data-file link. The user may instead use the platform email link; the agent does not need mailbox access. Follow the expiry shown on the page.
6. **Validate locally:** preserve the ZIP under workspace `results/<project_id>/<run_id>/04_integrated_impacts/ihme-gbd/raw/`. Check archive integrity, CSV fields, IDs/names, years, unique keys, row counts and numeric validity, including `lower ≤ val ≤ upper`. Store derived tables in `processed` and summaries in `quality`; do not publish raw files or task links.
7. **Record times:** save actual query-check, export-submission, acquisition and validation times in `results/<project_id>/<run_id>/records/<tool_id>/`. Keep non-secret parameters in CONFIG_DIR and authentication in AUTH_DIR. Do not put private records in shared documentation.

**Verified example:** the one-record website download passed content checks on 2026-10-26 at 21:05:42 Beijing time (UTC+8): a 717-byte ZIP containing one CSV, one record and 18 columns. See the [verified guide](references/first-download-guide.md) for times and IDs. The real run-tool call remains unverified pending task CDP ownership checks.

One possible next query is China, 2019/2023, ischemic heart disease, all ages, both sexes, deaths and counts/rates: up to four records. See the [download plans](../../../../methods/04_integrated_impacts/ihme_gbd_availability.md#suggested-download-scopes) for candidate health-model baselines and adaptation requirements. Neither plan has been executed.

## Browser Setup for run-tool

Use a locally configured Chromium executable or browser tool and a member-specific profile under `${AIRMOSAIC_AUTH_DIR}/browser_profiles/ihme-gbd/`, separate from data and personal configuration. Let the user authenticate in that profile. Enable a loopback-only CDP endpoint on a task-owned port, and check that the port belongs to this browser before connecting.

Keep the executable path mapping in `${AIRMOSAIC_CONFIG_DIR}`; keep the profile in the authentication root. Do not commit the executable path, profile path, cookies or account identity. See the repository's classified data-acquisition guide for the complete sequence.

## Registered execution

From the repository root, inspect `ihme_gbd_fetch_results`. [The public example](../../../../config/examples/run-tool/gbd.json) and the local `examples/gbd_mortality_rate_request.json` are parameter-only JSON. They contain historical example IDs, not a validated current request. Confirm version and all dimensions in the current page, then save a reviewed non-secret copy under CONFIG_DIR.

```powershell
python -m airmosaic.cli describe-tool ihme_gbd_fetch_results
$gbdParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gbd-task.json"
python -m airmosaic.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --dry-run --allow-network --confirm-browser-session
python -m airmosaic.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --allow-network --confirm-browser-session --timeout 300
```

Required caller fields: `years`, `locations`, `causes`, `ages`, `sexes`, `measures`, `metrics`; each is a comma-separated string of numeric IDs. Use `"ages":"10,11"`, not a JSON array or colon range. Optional fields include integer `port`, `version`, `population_group`, `wait_ms` and string `context`; `out` is automatically allocated. No field accepts cookies, passwords, profile paths or login tokens.

`--allow-network` permits the declared operation; `--confirm-browser-session` attests that the loopback CDP port belongs to the authorized task. Neither validates login or semantic correctness of dimension IDs. The runner does not launch a browser, log in, or export its authentication state.

Check both CSV and JSON sidecar for returned dimensions, row counts and error state. A zero exit code is not proof of a complete export. Never use stale browser rows after an error.

## Version and ID checks

The script's historical defaults include version `8352`, context `cause`, population group `1` and CDP port `9222`. The public example uses these as syntax examples only. Check the page's current version, location, cause, age, sex, measure and metric selections before an actual request; no mapping to the latest release is automatic.

Distinguish counts, rates per 100000 and proportions by the selected metric. The numeric schema validates shape, not availability, labeling or scientific suitability of an ID. Age-group harmonization needs an explicit mapping and compatible population denominators; never infer it from sorted row positions.

## Processing Rules

Keep project-specific processing in local project code, not in this skill. Recommended pattern:

1. Prefer one GBD round for the full study period; do not splice different rounds at a historical project-specific year cutoff.
2. For required cross-round harmonization, document revised estimates, methods and explicit mappings rather than treating round differences as observed change.
3. Preserve existing output schemas exactly unless the caller requests a schema change.
4. If GBD omits low-age cause combinations, leave them absent or fill only with a documented method.
5. Write a missing-combination report and provenance summary separately from the main table.

## Agent execution boundary

Use only `ihme_gbd_fetch_results` for this runner task. Browser authentication must already exist in the member's own session. The runner uses a minimal environment and task-owned output directory; the script still depends on the page's internal state and can break after UI changes. Review error/partial outputs before retrying, and preserve raw-to-processed provenance locally.

## Validation Checklist

- Compare raw and processed column names.
- Verify year ranges and row counts.
- Verify there are no unexpected missing values.
- For overlapping raw/final years, join by `year, location, metric, endpoint, agegroup, sex` and confirm numeric values match raw IHME data within tolerance.
- List combinations present in processed output but absent in raw IHME output.
- Confirm no credentials, access tokens, cookies, or personal browser paths were written to reusable files.

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
