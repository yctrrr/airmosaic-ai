# CSMAR browser-flow implementation notes

<!-- README-I18N:START -->

**English** | [中文](csmar-api_ZH.md)

<!-- README-I18N:END -->

For current access, scoped selection, download and validation, use the [first-download guide](first-download-guide.md). This reference preserves historical interface names for source review. They are not a supported public API, current endpoint verification or an executable AirMosaic download adapter.

## Historical interface names

| Endpoint | Historical purpose |
|---|---|
| `POST /api/csmar-main/single/saveOutline` | Create a query record |
| `POST /api/csmar-main/singleData/pack` | Prepare an export task |
| `GET /api/csmar-single/single/preview/<condition_id>` | Preview a recorded query |

Do not reconstruct requests, copy authentication material or capture raw session traffic as part of first-use verification. An access change or a production adapter requires a separately scoped implementation. Download-record identifiers, authenticated URLs and account-specific parameters stay local.

## Field and format checks

Select only the task's required fields. Use the complete field selection only when the agreed task requires it; compare selected names/count, descriptions and actual exported columns. Moving items to the selected list can empty the available list without losing the selection.

CSV, TXT and XLSX are format choices to verify in the current portal, without a universal reliability ranking. Encoding, header rows, leading zeros, row counts and missing columns need checking for each actual export. The registered local processor supports ZIP/XLSX with a fixed field contract; changing web export format does not adapt that processor.

## Session and execution boundary

A project-launched browser must explicitly use `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`; setting a placeholder variable does not configure a browser. Host-managed sessions keep their own storage and are not relocated or exported. Keep non-secret query plans in CONFIG_DIR, exports in the data workspace, and credentials in the member's protected mechanism.

`csmar_browser_download` remains a reference. `csmar_process_company_info` is the separately authorized local processing tool, available through run-tool and MCP. Neither interface supplies an automated CSMAR login or public API credential mechanism.
