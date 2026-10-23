---
name: csmar-downloader
description: Guide authorized CSMAR browser downloads and process an existing listed-company basic-information ZIP with csmar_process_company_info. Browser download is not automated by run-tool.
---

# CSMAR Data Downloader

> Invocation status: `csmar_browser_download` is a non-executable browser-workflow reference. Only `csmar_process_company_info` is enabled in `run-tool` for an existing company-info ZIP.

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md) and [execution guide](../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `output/<run_id>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

Download CSMAR (China Stock Market & Accounting Research) data tables from `https://data.csmar.com/` for socioeconomic driver analysis (workflow Layer 1).

## Workflow Layer

01_socioeconomic — provides listed-company activity data for industrial output, energy consumption, and end-of-pipe technology analysis.

## Prerequisites

- An authorized browser tool, or Node.js Playwright for the JavaScript example below
- CSMAR account with institutional access
- Python 3.10+ with pandas, openpyxl

## Browser download reference: csmar_browser_download

This catalogued reference has `execution_supported: false`; `run-tool` rejects it. Use `describe-tool csmar_browser_download` for metadata, then follow the authorized browser workflow with a tool actually available in the host, or perform it manually. No project browser-launch/login adapter is registered.

1. Use the member's own profile under `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`. Configure the browser explicitly; setting the root variable alone does not launch or select a profile.
2. Let the member authenticate and verify institutional table access. Do not export cookies or automate password entry.
3. Select the requested table, dates, records and needed fields. Select all fields only when the task requires the complete table; verify the selection and query size before submission.
4. Submit the query to create a download record, then open that record and use the final local-save action. Keep signed download links and account details local.
5. Save the export in the authorized data cache and retain its field description. Existing download records are not proof that a file was saved successfully.

CSV/TXT may be alternatives for browser exports, but the processor below specifically expects a ZIP containing an XLSX workbook; other formats require a separate adaptation. Browser operations have their own authorization and do not inherit runner path enforcement.

## Core Table: Listed Company Basic Information

Entry point:
```
https://data.csmar.com/csmar.html#/datacenter/singletable/search?databaseId=176
```

Key fields to include:
- Stock code, stock short name
- Statistical cutoff date
- Industry name and code (CSRC classification)
- Unified social credit code
- Chinese full name
- Province, city
- Main business
- Listing status

## Registered local processing: csmar_process_company_info

Use the existing downloaded ZIP; this step needs pandas/openpyxl and no browser login. [The public parameter example](../../../../examples/run-tool/csmar.json) is a flat JSON object:

```json
{"zip":"${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/csmar/company_basic.zip"}
```

Map that filename to the authorized input, then run from the repository root:

```powershell
python -m airmosaic_core.cli describe-tool csmar_process_company_info
python -m airmosaic_core.cli run-tool csmar_process_company_info --params-file examples/run-tool/csmar.json --dry-run
python -m airmosaic_core.cli run-tool csmar_process_company_info --params-file examples/run-tool/csmar.json
```

The runner supplies `out_dir`. The script reads the workbook directly inside the ZIP, without extracting next to or modifying the input. Results go under `output/<run_id>/csmar_process_company_info/`:

- `csmar_target_industry_company_candidates.csv`: sector-matched rows.
- `csmar_target_industry_company_list_latest.csv`: latest company records.
- `csmar_target_industry_company_list_latest.xlsx`: both sheets.

The fixed keyword groups cover thermal power, district heating, iron/steel, nonferrous metals, cement, lime, brick/tile, glass and chemicals. Review matches and required columns; unsupported tables and formats need adaptation. Company identity alone establishes neither cost payer nor physical production boundary. This is not a general financial-statement processor.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Excel export missing fields | Review browser-export alternatives; the local ZIP/XLSX processor needs adaptation for CSV/TXT |
| Download canceled by browser | Check `chrome://downloads/`; retry the final page click |
| Wrong account logged in | Use user menu logout, ask user to re-login |
| Field count mismatch | Re-select the task-required fields and verify the final export |

## References

- `references/csmar-api.md`: API endpoints and network flow
- `examples/csmar_company_query.json`: Example query parameters
