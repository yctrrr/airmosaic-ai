---
name: mlr3-modeling
description: Configure mlr3 tasks, learners and validation in reviewed R code, and track the external ml-mlr3 reference project.
compatibility: "R; mlr3; rpart; automatic tuning additionally requires mlr3tuning, paradox and future"
metadata:
  version: "1.1.0"
  reviewed: "2026-10-30"
---

# Use the mlr3 framework

**English** | [中文](SKILL_ZH.md)

This is framework guidance. `mlr3_workflow_reference` is catalogued but not executable through run-tool. For supported numeric regression, use the [regression skill](../../../SKILL.md) and `ml_regression_workflow`.

## Prepare and configure

Use R with `mlr3` and the selected learner backend. The synthetic examples require `rpart`; learned preprocessing uses `mlr3pipelines`, and tuning requires suitable `mlr3tuning`/`paradox` versions and a declared budget.

Write down the target and sample unit, predictors and types, prediction-time availability, split design, metric/direction and resource budget. For classification, specify class levels, positive class and probability/threshold decisions.

Check available APIs in the task environment:

```r
stopifnot(requireNamespace("mlr3", quietly = TRUE))
print(packageVersion("mlr3"))
print(mlr3::mlr_learners$keys())
learner = mlr3::lrn("regr.rpart")
print(learner$packages)
print(learner$param_set$ids())
```

## Use the code

The [synthetic regression/classification examples](examples/basic-model-use.md) provide complete R code for Task creation, three-fold development CV, fitting and new-data prediction. They use in-memory synthetic data and do not write files. They are direct R examples, not registered tools.

1. Create the appropriate Task and learner; keep declared sample roles and split identity.
2. Put learned imputation, encoding, scaling and selection inside the resampling graph.
3. Compare a baseline and bounded candidates. Separate inner tuning from outer performance evaluation.
4. Freeze choices, score the final holdout and use the fitted preprocessing/learner for new inputs.

Use [operations and validation](references/workflow.md) for graph, tuning and final-fit details. Rerunning CV after repeated selection does not create an independent test.

The [automatic-tuning route](../../../references/automatic-tuning.md) adds a concrete direct R helper and [synthetic script](examples/automatic-tuning.R): supplied grouped folds, explicit search ranges, evaluation/fit budgets and final-test separation. Only base-R contract checks passed in the inspected default environment; the full tuning example requires the missing dependencies. Existing registered tools still use their original fixed-candidate contracts.

## Check and save

Check failed folds, finite predictions, matching sample IDs and target units; for probabilities check class order and row sums. Save the fitted learner/graph, settings, split keys, predictions, metrics and dependency versions in a fresh external project result directory. Read back the model and compare predictions on the same prepared inputs.

General framework code does not inherit run-tool path or receipt handling. Use the [asset contract](../../../../../../../harness/assets.md) for study outputs. [Method selection](../../../../../../../methods/shared/machine_learning.md) explains when tabular learning is appropriate. [Upstream tracking](UPSTREAM.md) records the external reference version; it is not an automatic sync service.
