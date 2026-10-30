# Exposure–response data: versions, provenance and readiness

**English** | [中文](exposure_response_ZH.md)

Use this record to select a version and inspect the external source receipt. Scientific interpretation is in the [method](../../../../../methods/04_integrated_impacts/health_impacts.md). Shared version directories are relative to `AIRMOSAIC_ASSETS_DIR`: `data/04_integrated_impacts/ExposureResponse/<version>/`. Raw ER assets are separate from GBD baseline mortality; acquiring one does not acquire the other. Do not auto-download data when reading this skill.

## Acquired source records (2026-10-29)

| External version | Actual content and source | Readiness |
|---|---|---|
| `gemm-2018-c0640d8-20261029` | `gemm_fit_parameter_cells.csv`: 988 nonempty cells from the author's workbook parameter sheet, with exact cell coordinates, values and formula text; `provenance.json`. [DataGEMM pinned source](https://github.com/mszyszkowicz/DataGEMM/tree/c0640d86a852e2e3565392ba014964bd43edb8ff), `GEMM Calculator (PNAS)_ab.zip` → `GEMM Calculator (PNAS)_ab.xlsx` → `GEMM fit parameters`. | Actual numeric fit data acquired; not a normalized or validated RR curve. |
| `who-hrapie-2013-pm25-20261029` | `loglinear_parameters.csv`: one actual recommendation, RR **1.062**, 95% CI **1.040–1.083**, per **10 µg/m³**, annual mean PM2.5, natural-cause mortality **30+**, pooled sexes. [WHO 2013](https://iris.who.int/handle/10665/153692), Table 1 printed p5; corroborated in [HRAPIE author summary Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4480843/). | Historical reproduction/sensitivity entry; reference exposure still requires a task choice. |
| `who-hrapie2-2025-pm25-20261029` | `loglinear_parameters.csv`: RR **1.10**, 95% CI **1.06–1.13**, per **10 µg/m³**, annual mean PM2.5, natural mortality **A00–R99**, adults, pooled sexes. [WHO 2025 official record](https://www.who.int/publications/i/item/9789289062633); Table 2 printed p14/PDF p22 and adult eligibility printed p13/PDF p21. Source/permission page and the two relevant pages retained as text with hashes. | Current guideline entry to consider for a new HIA; adult minimum age and reference exposure still require task choices. |

The WHO 2025 report is available from the [Swiss TPH institutional copy](https://www.swisstph.ch/fileadmin/user_upload/SwissTPH/Institute/Ludok/Aktuelle_Berichte/WHO2025_HRAPIE-2_UpdatedGuidanceCRFunctionsHRAAirPollution.pdf), with ISBN 9789289062633, title and copyright verified. The table's proposed rounded coefficient **1.10/10** differs from the underlying meta-analysis forest plot **1.095/10** and Annex 1 **1.046/5**. Keep a selected record's precision and CI together; do not mix these with the adjusted multipollutant example. This source record does not adopt an O3 function.

For 2025 the recommended **5–70 µg/m³** range refers to mean/median exposures of HRA populations (p13); it is not a universal per-grid cap. Most contributing adults were 25+, but WHO explicitly leaves the target minimum adult age dependent on available population/mortality data and region. Do not silently impose the 2013 30+ rule. Regional transfer, high exposure and demographic applicability require justification. Neither increment RR supplies a biological threshold; select and record reference exposure and below-reference handling. The 5 µg/m³ guideline level is not automatically a TMREL.

## GEMM-specific unresolved items

The paper's [data deposition statement](https://doi.org/10.1073/pnas.1803222115) identifies the author repository. Pinned commit: `c0640d86a852e2e3565392ba014964bd43edb8ff`. Parameter blocks cover NCD+LRI, IHD, stroke, COPD, lung cancer and LRI; including/excluding Chinese cohort fits; aggregate 25+ and finer ages through 80+. These alternatives must not be mixed or added.

Only parameter worksheet cell values were inspected/retained; baseline, population and exposure worksheets were not read. Source ZIP/workbook hashes are recorded, but the entire workbook was not retained because it also contains baseline/exposure sheets. Greek parameter headers are drawing objects rather than cell text; coefficient-column mapping remains unconfirmed. Source age label `30-35` overlaps `35-39`; retain it as evidence and stop age normalization pending source/author clarification. Excluded-China LRI uses within-sheet formula references, retained without execution. These are reasons to stop, not to silently infer parameters. No GEMM confidence limits or risk-at-concentration values were fabricated; standard-error cells are not RR confidence bounds. No complete IER data were acquired.

## License and storage

No LICENSE file was found in the pinned DataGEMM repository root; public availability does not prove redistribution permission. Keep this research extraction external and review rights before any redistribution. The 2013 report's redistribution license was not established in this task. The 2025 report states **CC BY-NC-SA 3.0 IGO**: noncommercial use, attribution, share-alike, no WHO endorsement/logo, with third-party rights separately checked. External page extracts preserve that notice. No source PDF, workbook or parameter table is included in Git. Reuse outside the permitted scope needs rights review. General schema and source descriptions do not establish permissions for downloaded assets.

## Small coefficient contract and read-only check

`loglinear_parameters.csv` contains `parameter_id`, `pollutant`, `exposure_metric`, `concentration_unit`, `endpoint`, `age_min_years`, `age_max_years` (blank for open upper bound), `sex`, `function_type`, `rr`, `rr_lower`, `rr_upper`, `ci_level`, `increment`, `source_url`, `source_version`, `source_locator`; unresolved adult eligibility additionally uses `age_rule=adult_task_selection_required`. `provenance.json` records source/version, license status, file SHA256, exact applicability and an explicit counterfactual object (`value`, `unit`, `status`, `meaning`). An unresolved reference has null `value` and `status=task_selection_required`; do not turn it into zero.

From repository root, after selecting an external version:

```sh
python skills/model/04_integrated_impacts/health_impact_analysis/scripts/validate_loglinear_er.py "<external-version-directory>" --assets-dir "<external-assets-root>"
```

Python standard library only. This direct, read-only helper verifies hashes, required fields, RR/CI/increment ordering and finiteness, source consistency and explicit age/reference gaps. It accepts only the bounded pooled natural-cause annual PM2.5 coefficient contract. It is not a registered tool, converter, GEMM validator or mortality calculator; success reports `scientifically_approved=false` and `health_adapter_executable=false`. Failure exits 2; missing/mismatched sources must be corrected before task-copy adaptation. It does not read exposure, population or baseline mortality.

The external receipt is an acquisition record, not a promotion to a validated dataset. Use [operations](operations.md) and [input requirements](data_requirements.md) before any authorized calculation.

Pass `--assets-dir` or set `AIRMOSAIC_ASSETS_DIR` explicitly; the version must be a direct child of the ER subtree above. Linked/junction paths, Git ancestors and configured auth/config directories are rejected. Failure output reports an error category without local paths. These bounded checks do not replace run-tool or scientific review.
