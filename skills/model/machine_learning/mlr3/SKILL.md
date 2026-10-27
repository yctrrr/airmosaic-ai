---
name: mlr3-modeling
description: Guide use of mlr3 and mlr3verse for tabular regression or classification, learner comparison, tuning and prediction in AirMosaic. Track the zhjx19/ml-mlr3 reference project and adapt its workflow to local data, validation and privacy boundaries.
---

# mlr3 modeling and reference-project tracking

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


Use this skill for mlr3 modeling and tracking [zhjx19/ml-mlr3](https://github.com/zhjx19/ml-mlr3). See [upstream tracking](UPSTREAM.md) for the reviewed commit, version and review method. AirMosaic maintains usage/adaptation guidance; it does not automatically sync, install or execute upstream code.

**Invocation status:** `mlr3_workflow_reference` is `implementation_status: reference`, `execution.enabled: false`. It supports documentation queries, not run-tool training, tuning or prediction. R APIs such as `lrn()` and `resample()` are not AirMosaic tool IDs.

## Scope and dependencies

- Tabular regression/classification, baseline comparisons, resampling, tuning and prediction on new data.
- Basic examples require R, mlr3 and rpart; preprocessing PipeOps require mlr3pipelines; tuning needs mlr3tuning/paradox. Other learners require their extensions and backends. Installing mlr3verse does not establish that every backend works.
- Survival, clustering, spatial/temporal resampling and large training tasks require separately selected extensions, splits and validation cases. Examples do not cover these tasks, deep learning or remote deployment.
- Verify namespaces, dictionary keys and parameter names in the task environment and record package versions. Upstream checks are not local validation.

## Agent workflow

1. **Define the task:** target, prediction time, sample unit, available features, metrics and intended use. Exclude target-derived features, future information and identities unsuitable for modeling.
2. **Set data boundaries:** read authorized inputs only. Keep data, models and predictions in the workspace and non-secret mappings in CONFIG_DIR. Local modeling requires no account/API key or AUTH_DIR access.
3. **Split before fitting:** define training, validation and final tests from the study design. Repeated firms/stations/regions and time series do not automatically permit random row-wise CV. Retain local row IDs and split rationale.
4. **Build the development workflow:** deep-clone Task/Learner objects where needed. Put fitted imputation, encoding, scaling and feature selection inside resampling PipeOp graphs and reuse the same graph for prediction.
5. **Constrain selection:** begin with simple baselines and specify candidates, metric direction, folds, tuning count/time and resource budgets. Use development data only; use suitable outer validation for post-selection performance estimates.
6. **Evaluate frozen choices:** freeze features, preprocessing, hyperparameters and thresholds before the agreed final test within existing authorization. Do not repeatedly revise against the test and still label it independent. State gaps if authorization or test design is missing.
7. **Fit and predict:** record the final training scope and check new columns, types, factor levels, units and preprocessing contracts. Predict with the fitted learner/GraphLearner; do not refit preprocessing per new batch.
8. **Validate and share:** review failed folds, missing predictions, baselines and applicability. Preserve local reproduction records. Models, detailed predictions, backends and sessionInfo may contain sensitive information; inspect before sharing.

## Read as needed

| Task | Document |
|---|---|
| Splits, PipeOps, tuning, final fitting and inference | [Workflow and validation](references/workflow.md) |
| Basic regression/classification R APIs | [Synthetic example](examples/basic-model-use.md) |
| Reference version and upstream updates | [Upstream tracking](UPSTREAM.md) |
| Catalog entry and paths | [Machine-learning guide](../../../../harness/usage/machine-learning.md) |

Follow the [storage contract](../../../../harness/storage-and-credentials.md) and [agent boundaries](../../../../harness/agent-boundaries.md). New outputs may use `${AIRMOSAIC_LOCAL_WORKSPACE}/output/<run_id>/mlr3_workflow/`; this directory label is not an executable tool ID. Selecting the skill does not authorize data access, installation, external sharing or deployment.
