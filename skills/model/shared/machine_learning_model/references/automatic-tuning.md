# R automatic tuning: configuration, call and checks

**English** | [中文](automatic-tuning_ZH.md)

Use this route after an approved plan selects development-only automatic parameter optimization. The [method](../../../../../methods/shared/machine_learning_model/tuning.md) owns the reasoning. The direct [R module](../scripts/r/models/auto_tuning.R) implements a bounded `mlr3tuning::auto_tuner()` random search over caller-provided grouped folds. It is separate from the registered `ml_regression_workflow` and `ml_python_regression_workflow`; do not add tuning fields to their existing JSON contracts.

## Current scope and environment

The helper accepts complete finite numeric development data, a target, named features, explicit fold/group vectors, learner parameters and a budget. It supports `regr.rpart` and `regr.ranger`, without file readers, test-data arguments, missing-value fitting, spatial-fold generation, grid inference or exports. Source the module only to define functions. A direct R function does not inherit runner path/credential checks or enforce scientific approval.

Dependencies are `mlr3`, `mlr3tuning`, `paradox`, `future` and `rpart`; forests also require `mlr3learners` and `ranger`. A selected existing package library can be supplied through `R_LIBS_USER` before starting `Rscript --vanilla`. The helper neither installs packages nor loads personal startup files. Check package versions without printing personal library paths. Use a sequential future plan and one learner thread.

As checked on 2026-10-30, the default local R environment lacked the tuning packages. The base-R contract/refusal checks passed; the end-to-end tuning/holdout example was skipped for missing dependencies. This is not a successful model-training receipt or a verified real-data route. Run the full example in the selected dependency environment before a study.

## Explicit configuration

`ml_autotune_regression()` requires all of the following arguments:

| Argument | Meaning |
|---|---|
| `development`, `features`, `target` | Authorized development-only data frame, feature names and numeric target; maximum 100,000 rows and 64 features |
| `fold_id`, `group_id` | Vectors in the same row order; 2–10 consecutively numbered nonempty folds; a group cannot cross folds |
| `learner_id` | `regr.rpart` or `regr.ranger` |
| `search_bounds` | Named list of finite lower/upper numeric pairs; lower must be smaller than upper |
| `fixed_parameters` | Separate named list of fixed numeric values; cannot overlap search parameters |
| `evaluations`, `max_model_fits`, `seed` | Explicit candidate limit, fitting budget and seed; at most 64 evaluations and 641 fits, counting the final fit |

Tree parameters: `cp`, `maxdepth`, `minbucket`, `minsplit`. Forest parameters: `mtry`, `min.node.size`, `max.depth`, `num.trees`, `sample.fraction`. Unsupported fields fail. Integer ranges remain integer; `mtry` cannot exceed the feature count. Forest tree count must be explicit, fixed or searched, and cannot exceed 512. Random search uses batch size one; no automatic algorithm selection or Bayesian optimizer is implemented. The current range sampling is uniform on its declared numeric scale; logarithmic search requires a reviewed extension.

Parameters such as `ranger::min.node.size` and `rpart::minbucket` are not interchangeable. Preprocessing that estimates anything from data must be inside each resampling learner/graph. This first helper requires complete numeric inputs instead of silently imputing before CV; a pipeline extension needs separate testing.

## Call the reviewed function

From repository root, with an authorized development table and pre-reviewed grouping already in memory:

```r
operations <- new.env(parent = baseenv())
source("skills/model/shared/machine_learning_model/scripts/r/models/auto_tuning.R",
       local = operations)
# args is the approved named list described above, not a runner parameter file.
fit <- do.call(operations$ml_autotune_regression, args)
fit$selected_parameters
fit$budget
# Prediction occurs later, after all choices are frozen; exclude target and IDs.
prediction <- fit$learner$predict_newdata(authorized_prediction_features)$response
```

The [complete synthetic script](../frameworks/r/mlr3/examples/automatic-tuning.R) provides concrete argument lists for both tree and forest searches, with a linear model and a training-mean baseline. Its small values are engineering-example settings, not scientific defaults. It generates all inputs in memory and writes no data/model files:

```sh
Rscript --vanilla skills/model/shared/machine_learning_model/frameworks/r/mlr3/examples/automatic-tuning.R --validate-only
Rscript --vanilla skills/model/shared/machine_learning_model/frameworks/r/mlr3/examples/automatic-tuning.R
```

The first command checks ten meaningful refusals with base R and **does not tune**. The full command exits 77 with `dependencies_unavailable` when packages are missing. With dependencies, it must finish actual tuning, freeze all four models before scoring, check finite holdout predictions, same-seed tree replay and an in-memory serialization round trip. It emits a structured final status; no partial output should be interpreted as success.

## Inspect results and preserve boundaries

The returned object contains the fitted AutoTuner, its selected parameter values, tuning archive, exact row/fold/group mapping, declared/observed budget and package versions. Inspect finite development RMSE, failed trials and observed counts; do not report archive scores as final test accuracy. AutoTuner refits on the complete supplied development frame. `term_evals` bounds tuning evaluations, while a time terminator does not constrain every final fitting stage. An external process limit is separate.

Keep final-test targets outside the helper. Freeze all model families before scoring their common final test; use RMSE, MAE and `1-SSE/SST` R². New unlabeled-grid prediction needs identical features/units, missingness and domain checks, with bounded batches and reviewed output code; this helper alone is not a national grid-production pipeline.

The caller stores models, archives and row-level outputs only in the approved external asset project result root; personal mappings remain in CONFIG_DIR and credentials in their protected mechanism. Model objects and archives can retain data and must not enter Git. Preserve generated invocation/configuration, explicit rationale, actual events, versions and artifact checks. Existing plan-review requirements still apply to real studies; this API does not manufacture approvals or bypass them.

Official interfaces checked: [AutoTuner](https://mlr3tuning.mlr-org.com/reference/auto_tuner.html), [fixed custom resampling](https://mlr3.mlr-org.com/reference/mlr_resamplings_custom.html), [random-search batching](https://mlr3tuning.mlr-org.com/reference/mlr_tuners_random_search.html), [parameter domains](https://paradox.mlr-org.com/reference/Domain.html).
