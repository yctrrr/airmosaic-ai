# Comparing the original implementation and candidate results

**English** | [中文](README_ZH.md)

This experiment applies `compare_existing` from the [model_reproduction workflow](../../../../workflows/model_reproduction/README.md), using the [first independent attempt](../../prediction.md) as the frozen candidate and auditing authorized original code, saved models and final figures. Numerical checks, source evidence and scientific review remain distinct.

## Task and execution

1. Copy [task.example.json](task.example.json) to personal CONFIG and select the existing candidate and a fresh reference snapshot. Replace illustrative batch names; the example contains no server location.
2. The agent verifies the authorized endpoint and collects relevant code/results read-only. Trace code, tuning archives, saved models and final figures. Keep actual location mappings in CONFIG and do not execute the complete legacy script.
3. The reference input has the same hash as shared AQ-Bench. Prepare reference features under audited source rules: country counts `>=50`, climate-label exclusions, population density divided by 1000, cleaned column names and original row order. Retain independent sample keys and verify both feature-set cohorts.
4. If final station predictions are absent, use the [recovery functions](../../../../skills/model/shared/model_reproduction/scripts/reference_ranger.R) through a reviewed study caller in the minimal R environment. Label outputs `recovered_from_saved_model`. Do not train, rewrite models or export serialized calls/environments. Saved figures check metrics only at their displayed precision.
5. Seal snapshots and derived views, retain the audit matrix and run the [comparison entry](../../../../skills/model/shared/model_reproduction/SKILL.md). Check common/unmatched IDs, truths, reported-metric assertions, station prediction differences and unchanged-source receipts.
6. Report implementation correctness, numerical reproducibility, historical provenance gaps and scientific scope. Any necessary controlled experiments require a fixed budget and fresh outputs; similarity to old scores is not a tuning objective.

```sh
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <personal-config.json> --batch-id <fresh-comparison>
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <personal-config.json> --batch-id <fresh-comparison> --execute
```

## Status and storage

Read-only source/forest inspection, prediction recovery and frozen-side comparison are complete for this case. Engineering and numerical checks are complete; historical training-version linkage and scientific review of explanation figures retain evidence gaps. This does not establish a full historical tuning rerun or a new general automatic reproduction engine.

External `assets/results/ozone_environmental_drivers/` retains the first candidate, reference snapshot and new comparison batch separately. Actual audit matrices, scores, predictions, models, timestamps, source evidence and human decisions remain there, with this task's chosen internal layout. The example does not automatically load settings or connect to a server; results are not automatically overwritten, committed or promoted.
