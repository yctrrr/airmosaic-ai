# First CSMAR download and local handoff

<!-- README-I18N:START -->

**English** | [中文](first-download-guide_ZH.md)

<!-- README-I18N:END -->

Use this guide for a member-assisted first download. `csmar_browser_download` remains a non-executable reference; `csmar_process_company_info` processes a compatible, already-downloaded ZIP. The web step is not an MCP download tool.

## 1. Prepare access and scope

Open the [official portal](https://data.csmar.com/). The member completes login and verifies the requested table and time range are included in their access. Registration alone is not evidence of table access. Any registration information, verification code or agreement is handled by the member. Record only access status, without account details.

Start from a single company and one statistical cutoff date. Confirm the exact table title, date meaning, field definitions and expected row count before submitting. The existing [table link](https://data.csmar.com/csmar.html#/datacenter/singletable/search?databaseId=176) is a navigation hint, not a guarantee of the current table identity. If it changes, find the table by title in the portal.

A small acquisition check needs only the authorized company/date, name, industry and region fields. Exclude personal contacts and management information unless separately needed and authorized. Do not expand to all companies, years or fields because a default is selected.

## 2. Keep storage separate

Save new exports and field descriptions under `${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_browser_download/`, without overwriting an old download. Keep the non-secret query plan in `${AIRMOSAIC_CONFIG_DIR}/csmar/`. A browser launched for the task uses `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`; the caller must actually configure this location.

A host-managed browser has its own session storage. Setting these variables does not move that session or prove its storage boundary. Use only the task-authorized session, and do not export or relocate its login state. Neither browser mode inherits the runner's path enforcement.

## 3. Query and save

Set the requested date, company code and fields in the current form. Preview the result where supported. Check the selected field names/count and scope before creating the download task. If access is missing or a challenge appears, leave the current scope intact for member assistance.

Use the resulting download record and its final local-save action. Keep one request while the task is pending; inspect its status before retrying. Do not email a download, copy authenticated links into shared material, or call undocumented endpoints to replace the browser workflow. Retain the field-description file alongside the new export.

Record local times for access confirmation, scope confirmation, submission, completed file save and content validation. Use a consistent time zone such as `Asia/Shanghai`. Pending steps remain pending, without invented timestamps or server task identifiers in public examples.

## 4. Validate the new export

- Confirm the downloaded object is the requested archive/data file, rather than an HTML login or error page. Inspect archive integrity before opening its data members.
- Compare selected fields, field descriptions and actual columns. A preview or download record alone does not prove the saved file is correct.
- Read company codes as text, preserving leading zeros. Check the requested company/date, non-empty records, duplicate keys and missing values; do not assume exactly one row without examining the table's key definition.
- Retain source values and field meanings. Data quality and analysis boundaries are maintained in [enterprise-source methods](../../../../../methods/01_socioeconomic_natural_change/enterprise_sources.md).

Only newly acquired, task-authorized files are inspected during this verification. Existing original datasets remain untouched. Keep exports and detailed validation records outside Git; share status, counts and general field contracts.

## 5. Decide whether local processing applies

The existing processor needs a ZIP containing an XLSX workbook and all of the following exact columns:

```text
Symbol EndDate ShortName FullName
IndustryName IndustryCode IndustryNameC IndustryCodeC
IndustryNameD IndustryCodeD SocialCreditCode PROVINCE CITY
MAINBUSSINESS LISTINGSTATE
```

A smaller acquisition-only export does not meet this contract. Obtain additional fields only within the agreed task scope, or adapt the processor separately; do not invent missing columns or rename fields without a reviewed mapping. Multiple workbooks, alternate schemas, CSV/TXT or a different table need manual review/adaptation. Export format and language must match the source's actual options.

The current screen uses English, case-sensitive keywords and retains each company's latest date before screening. Complete columns do not establish valid industry selection. Chinese/other-language text, capitalization, the intended panel period and empty matches need review. These are current implementation boundaries, not normalization rules to apply silently.

For a compatible authorized ZIP, create a personal task JSON, for example:

```json
{"zip":"${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_browser_download/company_basic.zip"}
```

Use its actual authorized filename. With the project interpreter, inspect `csmar_process_company_info`, dry-run using that personal JSON, then execute within the task authorization. The runner allocates a fresh output directory and records a sanitized receipt. The input ZIP is read without extracting beside it.

Through MCP, use the same tool ID with this preview object:

```json
{"parameters":{"zip":"${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_browser_download/company_basic.zip"},"dry_run":true}
```

Actual MCP processing requires the server to start with `--execute-tool csmar_process_company_info` and a separately authorized call with `dry_run: false`. It needs no network or browser grant. Review `can_execute` and `blockers`, then the actual receipt and three expected output files. Processing success does not establish scientific acceptance of the candidate list.

## Current verification status

On 2026-10-27, the first bounded Chrome download and saved-file content check passed: eight fields and one effective record. Follow the [verified example](first-download-example.md) for website actions and recorded times. The existing ZIP processor and MCP execution boundary also have synthetic checks; the eight-column sample was not used for real industry screening.

Navigation/operation reference: the vendor's [CSMAR Solution manual, sections 3.1 and 3.3.1](https://library.zuel.edu.cn/_upload/article/files/16/da/a36893834ff8978060d5256a93b8/2eb4b7ef-b51f-4606-9535-223c4fe52b90.pdf), hosted by a university library. It documents the general access/query/save flow; current field availability and access are checked in the live portal. Processor contracts above come from the repository implementation.
