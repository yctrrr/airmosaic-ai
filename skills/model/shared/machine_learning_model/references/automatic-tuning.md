# Automatic tuning: direct R and Python helpers

**English** | [中文](automatic-tuning_ZH.md)

Use this route after an approved plan selects development-only automatic parameter optimization. The [method](../../../../../methods/shared/machine_learning_model/tuning.md) owns the reasoning. The direct [R module](../scripts/r/models/auto_tuning.R) implements a bounded `mlr3tuning::auto_tuner()` random search over caller-provided grouped folds. It is separate from the registered `ml_regression_workflow` and `ml_python_regression_workflow`; do not add tuning fields to their existing JSON contracts.

The [Python helper](../scripts/python/models/grouped_tuning.py) below provides a separate in-memory sklearn path. Neither direct helper introduces a new `run-tool` adapter or MCP tool ID. Existing task JSON contracts and IDs remain unchanged.

## R scope and environment

The helper accepts complete finite numeric development data, a target, named features, explicit fold/group vectors, learner parameters and a budget. It supports `regr.rpart` and `regr.ranger`, without file readers, test-data arguments, missing-value fitting, spatial-fold generation, grid inference or exports. Source the module only to define functions. A direct R function does not inherit runner path/credential checks or enforce scientific approval.

Dependencies are `mlr3`, `mlr3tuning`, `paradox`, `future` and `rpart`; forests also require `mlr3learners` and `ranger`. A selected existing package library can be supplied through `R_LIBS_USER` before starting `Rscript --vanilla`. The helper neither installs packages nor loads personal startup files. Check package versions without printing personal library paths. Use a sequential future plan and one learner thread.

As checked on 2026-10-30, the default local R environment lacked the tuning packages. The base-R contract/refusal checks passed; the end-to-end tuning/holdout example was skipped for missing dependencies. This is not a successful model-training receipt or a verified real-data route. Run the full example in the selected dependency environment before a study.

## R explicit configuration

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

## Call the reviewed R function

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

## Inspect R results and preserve boundaries

The returned object contains the fitted AutoTuner, its selected parameter values, tuning archive, exact row/fold/group mapping, declared/observed budget and package versions. Inspect finite development RMSE, failed trials and observed counts; do not report archive scores as final test accuracy. AutoTuner refits on the complete supplied development frame. `term_evals` bounds tuning evaluations, while a time terminator does not constrain every final fitting stage. An external process limit is separate.

Keep final-test targets outside the helper. Freeze all model families before scoring their common final test; use RMSE, MAE and `1-SSE/SST` R². New unlabeled-grid prediction needs identical features/units, missingness and domain checks, with bounded batches and reviewed output code; this helper alone is not a national grid-production pipeline.

The caller stores models, archives and row-level outputs only in the approved external asset project result root; personal mappings remain in CONFIG_DIR and credentials in their protected mechanism. Model objects and archives can retain data and must not enter Git. Preserve generated invocation/configuration, explicit rationale, actual events, versions and artifact checks. Existing plan-review requirements still apply to real studies; this API does not manufacture approvals or bypass them.

## Python grouped tuning

Use Python 3.11+ with separately prepared `numpy`, `pandas`, `scipy` and `scikit-learn>=1.4,<2`; the helper installs nothing. `fit_grouped_regression()` takes two in-memory DataFrames and explicit arguments; it does not read configuration, acquire data, write results, generate folds or enforce study approval. This differs from the R AutoTuner: Python accepts missing numeric features and a separate test frame, searches finite candidate lists, and returns a sklearn Pipeline; R requires complete numeric development inputs, searches numeric bounds and leaves final-test evaluation to its caller. R dependency skips above do not describe Python's execution status.

Set model families, features, group definition, holdouts and search ranges in the reviewed plan before fitting. Development and test group IDs must be valid and disjoint. `fold_id` is positional in development-row order, numbered consecutively 1..k for 2–5 nonempty folds; each group stays entirely within one fold. Numeric features may contain NaN, but each feature must have observations in every fold's training portion; targets must be finite and are never imputed. Median imputation is fitted inside each training fold; linear regression also fits its scaler there. The final refit learns preprocessing anew from all development rows.

| Argument | Python contract |
|---|---|
| `development`, `test` | Nonempty numeric-feature DataFrames, with target and group columns; no shared groups |
| `features`, `target`, `group_column`, `fold_id` | Explicit feature list, distinct target/group column names and development-row fold vector |
| `learner` | `linear_regression`, `decision_tree` or `random_forest`; no estimator injection |
| `search_space`, `fixed_parameters` | Separate dictionaries of unprefixed sklearn parameter names; no overlapping names |
| `n_iter`, `seed`, `max_fits` | Explicit candidate cap 1–16, integer seed 0..2³²−1 and fit budget 1–81 |

Tree/forest parameters are `max_depth` (integer 1–64) and `min_samples_leaf` (integer 1–10000); forests additionally accept `n_estimators` (integer 1–512) and `max_features` (numeric >0 and ≤1, using sklearn's supplied integer/fraction semantics). Trees require an explicit depth; forests also require an explicit tree count, fixed or searched. Each search list has 1–16 distinct valid values, with at most 65536 combinations. Trees/forests require a nonempty search. Linear regression accepts empty parameter dictionaries, does not search, fits once and returns an empty CV table with `best_cv_rmse=None`; it does not produce a comparable linear CV score.

Tree/forest `RandomizedSearchCV` maximizes negative RMSE on the declared folds with `n_jobs=1`, fixed seed and errors raised. The fit budget includes `min(n_iter, combinations) × folds + 1` fits, including the development refit. `best_cv_rmse` is the unweighted mean of fold RMSE values, not pooled row RMSE. Freeze selection using development evidence before evaluating the test. This API evaluates one already declared family, then predicts and scores its test once; it has no family-selection stage. If comparing multiple families, arrange development-only CV selection upstream, freeze the chosen family and search plan, then call the final helper. Never choose the final family or revise ranges from their test scores.

### Complete small synthetic call

Run this code from the repository root in the selected Python environment. All inputs are generated in memory; sizes and parameters are engineering-example choices, not study defaults. A shared prepared table can serve multiple model families; the helper retains the final estimator and CV summaries, not all fitted fold models.

```python
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

path = Path("skills/model/shared/machine_learning_model/scripts/python/models/grouped_tuning.py")
spec = importlib.util.spec_from_file_location("grouped_tuning_example", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

rng = np.random.default_rng(29)
x = rng.normal(size=(32, 2))
table = pd.DataFrame({"x1": x[:, 0], "x2": x[:, 1],
                      "target": 2 * x[:, 0] - x[:, 1],
                      "group": np.repeat(np.arange(8), 4)})
development = table.iloc[:24].copy()
test = table.iloc[24:].copy()
development.loc[[0, 5, 12], "x1"] = np.nan
test.loc[24, "x2"] = np.nan
features = ["x1", "x2"]
groups = development["group"].to_numpy()
fold_id = np.repeat([1, 2, 3, 1, 2, 3], 4)
assert not set(groups) & set(test["group"])
assert pd.DataFrame({"g": groups, "f": fold_id}).groupby("g").f.nunique().max() == 1

# The family and ranges are fixed before passing final test data.
result = module.fit_grouped_regression(
    development, test, features=features, target="target", group_column="group",
    fold_id=fold_id, learner="decision_tree",
    search_space={"max_depth": [2, 3], "min_samples_leaf": [1, 2]},
    fixed_parameters={}, n_iter=3, seed=41, max_fits=10)
selection = result["selection"]
cv = result["cv_results"]
metrics = result["test_metrics"]
predictions = result["predictions"]
assert selection["fits_required"] == 10 and selection["n_candidates"] == 3
assert selection["test_used_for_selection"] is False
assert len(cv) == 3 and np.isfinite(cv["mean_test_score"]).all()
assert np.isclose(selection["best_cv_rmse"], -cv["mean_test_score"].max())
residual = predictions["observed"] - predictions["predicted"]
assert np.isclose(metrics["rmse"], np.sqrt(np.mean(residual ** 2)))
assert np.isclose(metrics["mae"], np.mean(np.abs(residual)))
sst = np.sum((predictions["observed"] - predictions["observed"].mean()) ** 2)
assert np.isclose(metrics["r2"], 1 - np.sum(residual ** 2) / sst)
print(selection["parameters"], metrics)
```

`selection` records actual estimator parameters, declared search/fixed parameters, seed, row folds, score and budget. Inspect `cv_results` for candidate parameters and per-fold scores; timing columns need not reproduce exactly. `test_metrics` contains RMSE, MAE, `1-SSE/SST` R² and a development-target-mean reference under `development_mean_reference`. Zero test-target variance returns `r2=None` with `r2_note="undefined_zero_test_target_variance"`. The mean reference belongs to common evaluation, not a separate model family. `predictions` retains the test index with observed/predicted/reference columns. For later unlabeled predictions, pass identically ordered numeric features to `result["estimator"].predict(feature_frame[features].to_numpy(dtype=float, na_value=np.nan))` after domain/units/missingness checks.

The Python synthetic checks cover all three models, group/fold refusal, training-fold imputation, budgets/parameters, deterministic predictions/selection and test-target perturbation. Run `python -m pytest harness/checks/test_grouped_tuning.py -q` in the dependency environment. These are engineering checks, not real-station training, spatial generalization evidence or scientific acceptance. Model objects may retain data; any caller-chosen persistence must follow the same external-project storage boundary described above.

Official R interfaces checked: [AutoTuner](https://mlr3tuning.mlr-org.com/reference/auto_tuner.html), [fixed custom resampling](https://mlr3.mlr-org.com/reference/mlr_resamplings_custom.html), [random-search batching](https://mlr3tuning.mlr-org.com/reference/mlr_tuners_random_search.html), [parameter domains](https://paradox.mlr-org.com/reference/Domain.html).
