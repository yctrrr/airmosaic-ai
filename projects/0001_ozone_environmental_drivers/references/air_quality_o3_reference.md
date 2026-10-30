# Air-quality ozone regression reference case

<!-- README-I18N:START -->

**English** | [中文](air_quality_o3_reference_ZH.md)

<!-- README-I18N:END -->

**Evidence: read-only source audit on 2026-10-27.** The authorized server project contains a reusable modeling example in `script/AQ_Bench.r`. Source and directory metadata were inspected; input data contents, fitted model contents and numerical results were not read or recomputed. This is a reference for [requirements-driven model building](../../../methods/shared/requirements_driven_model_building.md), not a registered executable case.

## Confirmed calculation path

| Stage | Source evidence | Reusable responsibility |
|---|---|---|
| Entry | `AQ_Bench.r:1` | Interactive R entry derives its location from the active RStudio document; a command-line entry requires adaptation |
| Data and features | `AQ_Bench.r:33–66` | Read a tabular CSV, select target/features, filter the research sample, recode categories and handle missingness |
| Split | `AQ_Bench.r:67–80` | Hold out rows labeled `test` in `dataset`; put other labels in training |
| Fit and tune | `AQ_Bench.r:84–138` | Two feature-set branches using mlr3 `regr.ranger`, random 10-fold CV, RMSE and random search with 20 evaluations |
| Evaluate | `AQ_Bench.r:140–188` | Test predictions, metrics and scatter plots |
| Explain | `AQ_Bench.r:231–386,479–545` | PDP, ICE, feature interactions, 3D PDP and fastshap/shapviz explanations |

Those split and tuning choices describe this source case; they are not defaults for other users' tasks. The independent `ML_DID.R` entry is exploratory causal-method code and is not evidence of a generally validated causal capability.

## Input contract recovered from source

The bounded directory inventory contains five R source entries, one CSV in the data directory and 24 top-level result files: two RDS models, two CSVs and 20 image files. This is an inventory of the inspected locations, not evidence that every script or output has been validated. Historical scripts and auxiliary folders remain separate from the confirmed main entry.

The primary target is `o3_average_values`. The full feature set names `climatic_zone`, `alt`, `water_25km`, `grasslands_25km`, `croplands_25km`, `urban_and_built-up_25km`, `no2_column`, `population_density` and `nightlight_1km`. The source also uses `country` for sample filtering and `dataset` for splitting. The `anth` branch uses `climatic_zone`, `alt` and `population_density`; this source-defined name is not a universal definition of anthropogenic contribution.

The historical private CSV was inspected only for existence and size (1,531,254 bytes); its contents remain unread. The public input below provides a documented starting point. Equality with the historical private file has not been checked.

## Public input

[AQ-Bench v1](https://b2share.eudat.eu/records/xp9ww-efm51), published on 2020-11-05 under CC-BY-4.0, supplies the target and every feature named above. The [data paper](https://doi.org/10.5194/essd-13-3013-2021) describes station-level ozone metrics aggregated over 2010–2014 from the TOAR database, with environmental metadata. This is a station-level regression input, without hourly time series.

| File | Content |
|---|---|
| `AQbench_dataset.csv` | 5,577 stations, 53 columns; 1,531,254 bytes |
| `AQbench_variables.csv` | Dictionary for 53 columns; 3,933 bytes |

Save the unchanged files under `${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/`. Keep `asset.json` with the source DOI, license, version and file hashes, and `validation.json` with acquisition checks. Public input belongs in the external asset root; repository assets remain synthetic examples.

The dictionary identifies `o3_average_values` as the response in ppb. `id` uniquely identifies stations; `dataset` contains `train` (3,348), `val` (1,114) and `test` (1,115). Preserve these labels before choosing a development protocol. Other ozone response columns must not silently enter the predictor set. Handle the published missing marker `-999` during preparation, leaving source bytes intact. Do not execute dictionary preparation suggestions as code.

On 2026-10-27, both official files were downloaded without login and passed the publisher MD5 checks and local SHA256 verification. All case-required columns were present, with no blank or `-999` values in those columns. No model was fitted. The source paper documents uneven station coverage, measurement uncertainty and time-invariant metadata; performance on this historical benchmark does not establish current coverage or spatial extrapolation.

## Existing outputs and missing receipts

The source has 24 active `library()` declarations, without verified installed versions or compatibility:

```text
ISLR aqfig colorRamps data.table dplyr fastshap future ggplot2 iml
lubridate mlr3 mlr3fselect mlr3tuning mlr3verse mltools paradox
ranger readr reticulate shapviz stringr tictoc tidyverse treeshap
```

Additional namespace calls include RStudio location helpers and plotting/data helpers. Determine the minimal dependencies for each extracted operation rather than installing the entire historical environment. No dependency lockfile was observed in the inspected project-root listing.

The source writes `result/Ranger_AQ.rds` and `result/Ranger_AQ_anth.rds` at lines 132–138. Later lines export test scatter, importance, PDP/ICE, interaction, 3D PDP and SHAP plots. Existing output files were checked only for presence/size.

Lines 168–170 compute mlr3 `regr.rmse` / `regr.rsq` and a separate regression's adjusted R-squared; preserve these definitions and do not merge them into one unspecified R-squared. The current entry does not persist a separate test-prediction table, fold assignment or complete tuning archive. Other CSVs present in the results directory cannot be attributed to this entry without producer evidence.

## Required adaptations before use as a validation template

1. Give the entry explicit data/configuration/output arguments and reusable load, prepare, fit, evaluate and explain functions. Running or sourcing the current top-level script may execute the whole analysis.
2. Preserve a stable row identifier before filtering. The full and subset branches drop missing rows separately but reuse full-branch row positions for splitting (`AQ_Bench.r:58–73`). Different missingness patterns can misalign their samples. Whether this occurs in the existing data was not tested. A validated adaptation needs branch-specific key alignment and a declared comparison cohort.
3. Declare allowed split labels rather than silently training on every non-`test` label. Choose grouping/time/spatial validation for the requested deployment; random row-wise CV is only this reference's choice.
4. Make country selection, category merging, population scaling, target/features, seeds, tuning budget and plot limits explicit. Record original reproduction settings separately from newly selected settings.
5. Configure explanation background and resource limits. The original 3D PDP repeats the whole dataset over a 20×20 grid (`AQ_Bench.r:327–347`), including test predictor support; SHAP uses training background (`493–499`). Declare when test-distribution descriptions are permitted, and keep development/selection separate from the held-out assessment. High-resolution plot exports also need a budget.
6. Persist input/schema versions, split IDs, candidate/tuning records, held-out predictions, metric definitions and a fresh artifact manifest. A saved model or plot alone is insufficient for reproduction acceptance.
7. Bind explanations to the frozen model and feature contract. Lines 206–208 reset learner parameters for an importance filter; review whether that result represents the final selected model. If it uses an auxiliary fit, label it accordingly. Replace positional response extraction with a named response contract.

Keep an unmodified source snapshot and local fingerprint for the legacy case. A corrected/adapted implementation is a separately versioned case, with documented differences and validation. Do not silently alter old data, outputs or reference behavior to produce agreement.

## Capability status

The source audit preserves adaptation evidence for the legacy case. A separate [public-input regression skill](../../../skills/model/shared/machine_learning_model/SKILL.md), exposed as `ml_regression_workflow`, now connects preparation, fitting, evaluation and explanation and has completed an AQ-Bench small-sample run. It uses explicit training, validation and test sets rather than reproducing the legacy random-CV script unchanged. Private source and historical data stay in place; arbitrary models and general orchestration remain unsupported.
