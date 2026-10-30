# Paper prediction and evaluation experiment

**English** | [中文](prediction_ZH.md)

This experiment combines external AQ-Bench inputs, the [regression skill](../../skills/model/shared/machine_learning_model/SKILL.md) and [mlr3 skill](../../skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL.md), following Section 2, Table 1 and Figure 3 of the [final published article](https://doi.org/10.1016/j.atmosres.2026.108869). The scientific question belongs to this project; the general data/skill recipe remains in the [workflow](../../workflows/ml_regression/README.md).

Read and freeze the [agent prompt](prediction_prompt.md) and [protocol](prediction.json). Retain countries/regions with strictly more than 50 observations, reduce climate labels to dry, moist or wet, and exclude unknown or unmapped labels. Combine released train and val into 4077 development stations and preserve 1009 test stations. Both feature sets share stations, ten-fold assignments and complete-case conditions.

The article specifies random forests, both feature sets and ten-fold RMSE tuning but does not supply the complete search space, original seed or all implementation details. This attempt prespecifies 20 unique candidates per model, 500 trees, one thread and the protocol's search ranges. Save selected settings before final assessment and refit on all development stations. Matching counts or qualitative patterns alone does not establish numerical reproduction of the paper.

## Execution

Run from the repository root. Explicitly set `AIRMOSAIC_ASSETS_DIR`, `AIRMOSAIC_CONFIG_DIR`, `AIRMOSAIC_AUTH_DIR` and `AIRMOSAIC_R_LIBRARY` under the storage contract. No configuration/authentication files are opened and no installation or network requests are performed. Dependencies are R, jsonlite, mlr3, mlr3learners and ranger. Settings use portable relative paths.

```powershell
# Check paths, hashes and dictionary without parsing data rows or fitting.
python projects/0001_ozone_environmental_drivers/run_prediction.py --batch-id paper_prediction_attempt01

# Check cohort rules, invalid inputs, metrics, OOF prediction and test isolation.
python projects/0001_ozone_environmental_drivers/run_prediction.py --batch-id paper_prediction_checks01 --self-test --timeout 180

# Authorized real-data run; choose a fresh batch name on every execution.
python projects/0001_ozone_environmental_drivers/run_prediction.py --batch-id paper_prediction_attempt01 --execute --timeout 1800
```

This is a study launcher, not a new tool ID or a ten-fold tuning option of generic `run-tool`. It reuses core path checks, separated roots, the minimal child environment, process-tree time limits and the fixed R launch protocol. R reuses the regression skill's metric function and uses mlr3 for study-specific resampling and fitting. These controls are not an OS sandbox.

## Storage and review

This experiment chooses external `assets/results/ozone_environmental_drivers/<batch_id>/` and retains:

- Prompt, protocol, executable source and skill snapshots with hashes.
- Exclusion counts, common cohort, station folds, all candidates/fold scores and selected settings.
- Development OOF and final test predictions, mean baseline, RMSE, MAE and explicitly defined out-of-sample R².
- Both models, reload checks, prediction plots and impurity importance; impurity importance is a biased predictive diagnostic, not a causal effect.
- Software versions, start/end times, sanitized progress, independent Python checks and artifact hashes.

Development OOF scores participate in tuning and are not unbiased final performance estimates. Test assessment follows frozen selection; random station splits do not establish spatial transfer. Results are neither committed nor automatically promoted. The first attempt has been compared against original code, saved models and final results through the [reproduction workflow](experiments/reference_comparison/README.md). Historical training provenance retains gaps and scientific review remains pending. New runs require their own comparison batch.
