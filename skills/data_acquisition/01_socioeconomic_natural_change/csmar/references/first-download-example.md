# Verified CSMAR annual-table download

<!-- README-I18N:START -->

**English** | [中文](first-download-example_ZH.md)

<!-- README-I18N:END -->

Verified on 2026-10-27 using external Chrome after member login: one company, one statistical cutoff date, eight fields, one downloaded ZIP and one validated record. Prepare access and storage with the [first-use guide](first-download-guide.md).

## Query and fields

Open the [official table entry](https://data.csmar.com/csmar.html#/datacenter/singletable/search?databaseId=176), confirming that the annual listed-company basic-information table is selected. This example used security code `600028`, with both date inputs set to `2023-12-31`. The date is the statistical cutoff date, rather than the download or disclosure date.

| Source field | Meaning |
|---|---|
| `Symbol` | Security code |
| `ShortName` | Security short name |
| `EndDate` | Statistical cutoff date |
| `IndustryName` | Industry name under the table's applicable classification |
| `IndustryCode` | Corresponding industry code |
| `FullName` | Full company name |
| `PROVINCE` | Registered province |
| `CITY` | Registered city |

These are source field identifiers, not runner parameters. Personal-contact, management and exact-address fields are not needed for this example.

## Website steps

1. Set both dates and leave the inputs to commit the edits. Recheck the values after the form updates.
2. Open code selection, search for the requested code, wait for its candidate, select that one candidate and confirm. Verify one selected code rather than the all-code default.
3. Keep the three default identity/date fields and add the five remaining fields above. Verify eight selected fields. Keep email delivery and saved-query options off.
4. Preview and confirm one matching record. Close the preview and wait until it has disappeared before continuing.
5. Click the data-download action and wait for the independent summary page. Do not repeatedly submit while it is being prepared; inspect the same task/download record if delayed.
6. Recheck table, code, dates and XLSX format. Expand the field summary, which initially shows only part of the selection. Verify all eight identifiers, then click the final local-save button to obtain the ZIP.
7. Copy only this task's new file into a fresh authorized workspace destination, verify the copy and preserve the browser download. Do not move session files or unrelated downloads. Keep account-specific archive names and authenticated URLs out of shared material.

## Artifact checks

The verified ZIP was 218,974 bytes with three members, including one XLSX workbook and a field-description text. Archive CRC checks passed. The workbook had eight expected columns, two description/unit rows and one effective company/date row. Field descriptions matched the selection; the data matched the requested code/date, with no duplicate key or missing selected values.

Read codes as text. Separate description/unit rows from observations using the actual data-key contract; do not count every workbook row as a company or blindly drop a fixed row count for another version. Validate the archive without extracting member names into filesystem paths. Source files and detailed receipts remain outside Git.

## Recorded times

All times below use `Asia/Shanghai` on 2026-10-27.

| Time | Operation |
|---|---|
| 15:00:19 | Confirmed the bounded sample and requested its preview |
| 15:17:33 | Triggered the Chrome export after checking the scope |
| 15:20:19 | Clicked the final local-save action |
| 15:24:21 | Completed archive, column and data-contract checks |

## Local-processing handoff

`csmar_browser_download` remains a non-executable reference. This eight-column example is not passed to the existing 15-column `csmar_process_company_info` screen. That processor is separately available through run-tool/MCP; no real industry screening was performed here.

Classification changes and normalization belong in [enterprise-source methods](../../../../../methods/01_socioeconomic_natural_change/enterprise_sources.md). A registered region or industry label does not directly identify a production facility or its emissions.
