# Linear regression

**English** | [中文](README_ZH.md)

Use the implemented ordinary linear predictor when a linear candidate is appropriate for the approved question. This path provides prediction and model checks, not coefficient inference or causal identification.

R linear regression is not enabled in the current adapter. Do not pass `regr.lm` to the R tool. The Python constructor is `LinearRegression()` with no exposed learner parameters; penalized variants are not implemented here.

## Configure and invoke

Prepare the [Python environment/task contract](../../references/python-path.md), and follow the [shared review process](../../references/planning.md). This predictor does not require R. Scientific choices belong to the [matching method](../../../../../../methods/shared/machine_learning_model/models/linear_regression/README.md). Commands below run from the repository root.

Python: [complete task](../../../../../../config/examples/machine-learning-model/python/linear_regression.synthetic.json), [runner parameters](../../../../../../config/examples/run-tool/ml-model-python-linear-regression.json).

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-linear-regression.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-linear-regression.json --timeout 180
```

Examples are for an authorized fixed synthetic replay. Python examples request no contribution computation; R tree/forest examples retain the permutation method required by the current R contract. Except for baseline-only tasks, candidates still compete with the mean baseline; selection may legitimately favor the baseline. Preview does not parse rows or prove dependencies. Actual execution uses the three roots and declared result scope for fresh artifacts. Do not reuse technical replay settings as a real-data plan.

## Implementation and checks

- Python: [constructors and shared preprocessing](../../scripts/python/models/regression.py), [execution and verification](../../scripts/python/run_regression.py).

Resolve candidates, metrics, predictions, preprocessing and reload checks through `artifacts.json`. Check actual cohorts, learner identities/settings and independently recomputed holdout metrics; exit status or model-file presence alone is insufficient. This directory duplicates no training code and adds no tool ID. Return to [family navigation](../README.md).
