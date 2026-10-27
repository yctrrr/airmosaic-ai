# First GBD download: login, minimal query and export

<!-- README-I18N:START -->

**English** | [中文](first-download-guide_ZH.md)

<!-- README-I18N:END -->

Reviewed: 2026-10-26. See the [GBD method](../../../../../methods/04_integrated_impacts/ihme_gbd.md) for provenance, uncertainty and normalization. This guide stores no personal session and does not accept terms on the user's behalf.

## 1. Open the official page

1. Open [GBD Results](https://vizhub.healthdata.org/gbd-results/) and verify the official domain.
2. The user personally decides on terms and completes login, registration or verification. Do not request passwords, verification codes, account screenshots or tokens.
3. Return to the query page before the agent reads public controls. Pause inspection during authentication; do not export cookies or copy a profile.
4. Check the displayed release round separately from the selected data year. Visible controls or old rows do not prove a new query or download works.

## 2. One-record query

| Dimension | Selection |
|---|---|
| Displayed round | GBD 2023 |
| Estimate type | Cause of death or injury |
| Measure | Deaths |
| Metric | Number |
| Cause | All causes |
| Location | Global |
| Age | All ages |
| Sex | Both |
| Year | 2023 |

1. Inspect every selected item in multiselect controls and remove unintended measures, metrics or locations.
2. Select by readable labels. Do not guess current mappings from historical IDs or option order. Missing options require checking the page state.
3. Review all conditions and submit one search. Keep measure and metric distinct.
4. Wait for completion and verify one matching combination with its estimate and bounds. Rows containing other measures or metrics do not match this query.
5. If loading stalls or an error appears, record the state and inspect the original request before retrying. Do not repeatedly submit, blindly refresh or save old rows as new results.

Hand access-verification prompts to the user and pause further query actions. Do not solve or bypass verification, or substitute internal endpoints.

## 3. Export and validate locally

1. Once fresh results match, click Download and select Both to include IDs and names. Review the scope; the user handles additional terms or verification.
2. Submit the export once. Follow the progress link in the success message without reading the user's mailbox. The user may instead use the platform email link.
3. Wait until the download is ready and obtain the ZIP from the data-file link. The observed page offered files for seven days after creation; follow the current page's expiry.
4. Preserve the ZIP under `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/ihme-gbd/raw/`. Check that it belongs to this request. Keep email addresses, task references and temporary URLs out of shared documentation.
5. Save non-secret plans under `AIRMOSAIC_CONFIG_DIR/gbd/` and receipts under workspace `runs/<run_id>/`. Check archive integrity, CSV schema, IDs/names, units, row counts, duplicate keys, missingness and uncertainty ordering. Store summaries separately in `quality`.
6. Keep the original and write transformations separately in `processed`. File acquisition is verified only after the new file is saved and checked.

Record actual start, submission, completion/failure and validation times with a time zone. Leave steps that have not occurred unset.

## 4. Separate run-tool prerequisites

`ihme_gbd_fetch_results` requires an authorized task-owned loopback CDP endpoint and current parameters. In-app browser access does not establish that port 9222 exists. Do not scan unrelated sessions, expose arbitrary debug endpoints or copy authentication state.

Once the user or system owner has prepared the browser and endpoint ownership is verified, follow [SKILL.md](../SKILL.md) for dry-run and execution. Session attestation is not login verification; dependency checks or a successful preflight do not prove export works.

The script depends on internal page state and may need adaptation after UI updates. Historical defaults are syntax examples, not current mappings. Do not run the raw script or internal PHP requests to bypass missing prerequisites.

## Verified status

The one-record query, ZIP download and CSV checks passed on 2026-10-26. All times below are Beijing time (UTC+8).

| Step | Time and result |
|---|---|
| Fresh result checked | 21:00; one matching record |
| Export submitted | 21:02; IDs and names retained |
| File acquisition confirmed | 21:05; 717-byte ZIP, one CSV, one record, 18 columns |
| Validation completed | 21:05:42; intact archive, matching dimensions and year, finite nonnegative values, `lower ≤ val ≤ upper` |

Observed dimension IDs were `population_group=1`, `measure=1`, `location=1`, `sex=3`, `age=22`, `cause=294`, `metric=1`, `year=2023`. They identify all population, deaths, global, both sexes, all ages, all causes, number and the year. Preserve IDs with names. This CSV does not supply the adapter's version ID; do not infer it from these fields.

No task CDP endpoint was verified for the real adapter call, so run-tool execution remains untested. See the [data-range guide](../../../../../methods/04_integrated_impacts/ihme_gbd_availability.md) for other products and candidate scopes.
