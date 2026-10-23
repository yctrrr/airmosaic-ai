---
name: ihme-gbd-results
description: Fetch IHME GBD Results with ihme_gbd_fetch_results through an existing user-authenticated browser. Use for scoped mortality or population exports after checking current page version and dimension IDs.
---

# IHME GBD Results

> Invocation status: `ihme_gbd_fetch_results` is enabled in `run-tool` for an existing authorized loopback browser session. It does not launch a browser or authenticate the user.

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md) and [execution guide](../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `output/<run_id>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

Use this skill for IHME GBD Results acquisition and local processing. The skill does not store credentials, cookies, tokens, browser profiles, or personal paths. Raw exports and processed mortality tables must stay under the AirMosaic local workspace.

## Results and cache boundary

`run-tool` writes `output/<run_id>/ihme_gbd_fetch_results/results.csv` and its JSON sidecar. Raw/processed health tables stay local. Publishing a validated export into `${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/gbd_health/` is a separate authorized operation, not automatic runner behavior. Do not commit exports, account identity or browser artifacts.

## Workflow

1. Open `https://vizhub.healthdata.org/gbd-results/` in a Chromium browser with remote debugging enabled.
2. Let the user log in and complete any verification manually.
3. Prefer the page's own search flow over direct `fetch` or `requests` calls. Direct calls to internal PHP endpoints can be blocked or return stale/error state.
4. Invoke `ihme_gbd_fetch_results` through `run-tool` to drive the loaded page and collect `tableData`; do not call the raw script to bypass runner checks.
5. Save raw IHME output separately from project-specific processed outputs.
6. Map IHME display names to local schemas explicitly; do not infer endpoint or age mappings from sort order alone.
7. Validate every processed output against raw IHME rows by key columns and numeric values.

## Browser Setup

Use a locally configured Chromium executable or browser tool and a member-specific profile under `${AIRMOSAIC_AUTH_DIR}/browser_profiles/ihme-gbd/`, separate from data and personal configuration. Let the user authenticate in that profile. Enable a loopback-only CDP endpoint on a task-owned port, and check that the port belongs to this browser before connecting.

Keep the executable path mapping in `${AIRMOSAIC_CONFIG_DIR}`; keep the profile in the authentication root. Do not commit the executable path, profile path, cookies or account identity. See the repository's classified data-acquisition guide for the complete sequence.

## Registered execution

From the repository root, inspect `ihme_gbd_fetch_results`. [The public example](../../../../examples/run-tool/gbd.json) and the local `examples/gbd_mortality_rate_request.json` are parameter-only JSON. They contain historical example IDs, not a validated current request. Confirm version and all dimensions in the current page, then save a reviewed non-secret copy under CONFIG_DIR.

```powershell
python -m airmosaic_core.cli describe-tool ihme_gbd_fetch_results
$gbdParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gbd-task.json"
python -m airmosaic_core.cli run-tool ihme_gbd_fetch_results --params-file $gbdParams --dry-run --allow-network --confirm-browser-session
# Execute only after the parameter file and the existing authorized session have been checked.
python -m airmosaic_core.cli run-tool ihme_gbd_fetch_results --params-file $gbdParams --allow-network --confirm-browser-session --timeout 300
```

Required caller fields: `years`, `locations`, `causes`, `ages`, `sexes`, `measures`, `metrics`; each is a comma-separated string of numeric IDs. Use `"ages":"10,11"`, not a JSON array or colon range. Optional fields include integer `port`, `version`, `population_group`, `wait_ms` and string `context`; `out` is automatically allocated. No field accepts cookies, passwords, profile paths or login tokens.

`--allow-network` permits the declared operation; `--confirm-browser-session` attests that the loopback CDP port belongs to the authorized task. Neither validates login or semantic correctness of dimension IDs. The runner does not launch a browser, log in, or export its authentication state.

Check both CSV and JSON sidecar for returned dimensions, row counts and error state. A zero exit code is not proof of a complete export. Never use stale browser rows after an error.

## Version and ID checks

The script's historical defaults include version `8352`, context `cause`, population group `1` and CDP port `9222`. The public example uses these as syntax examples only. Check the page's current version, location, cause, age, sex, measure and metric selections before an actual request; no mapping to the latest release is automatic.

Distinguish counts, rates per 100000 and proportions by the selected metric. The numeric schema validates shape, not availability, labeling or scientific suitability of an ID. Age-group harmonization needs an explicit mapping and compatible population denominators; never infer it from sorted row positions.

## Processing Rules

Keep project-specific processing in local project code, not in this skill. Recommended pattern:

1. Keep historical rows only through the last trustworthy year.
2. Use real GBD rows for newly available years.
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
