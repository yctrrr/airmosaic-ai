# Random-forest regression

**English** | [中文](README_ZH.md)

Select an explicit forest budget and tree-complexity controls. Compare the fitted candidate with the baseline using the reviewed holdout design.

Scientific selection belongs to the [random-forest method](../../../../../../../methods/shared/machine_learning_model/models/tree_based/random_forest/README.md).

R uses `regr.ranger` with `num.trees`, `mtry`, `min.node.size`, `max.depth`, `sample.fraction` and `replace`. Python uses `random_forest` with `n_estimators`, `max_depth`, `min_samples_leaf` and `max_features`. Both paths restrict runtime threads; parameter mappings and random seeds do not guarantee cross-language equivalence.

## Configure and invoke

Prepare the [R environment](../../../references/operations.md) or [Python environment/task contract](../../../references/python-path.md), and follow the [shared review process](../../../references/planning.md). Commands below run from the repository root.

R: [complete task](../../../../../../../config/examples/machine-learning-model/r/random_forest.synthetic.json), [runner parameters](../../../../../../../config/examples/run-tool/ml-model-r-random-forest.json).

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/ml-model-r-random-forest.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/ml-model-r-random-forest.json --timeout 180
```

Python: [complete task](../../../../../../../config/examples/machine-learning-model/python/random_forest.synthetic.json), [runner parameters](../../../../../../../config/examples/run-tool/ml-model-python-random-forest.json).

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-random-forest.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-random-forest.json --timeout 180
```

Examples are for an authorized fixed synthetic replay. Python examples request no contribution computation; R tree/forest examples retain the permutation method required by the current R contract. Except for baseline-only tasks, candidates still compete with the mean baseline; selection may legitimately favor the baseline. Preview does not parse rows or prove dependencies. Actual execution uses the three roots and declared result scope for fresh artifacts. Do not reuse technical replay settings as a real-data plan.

## Implementation and checks

- R: [shared fitting](../../../scripts/r/models/fit.R), [held-out evaluation](../../../scripts/r/common/evaluate.R).
- Python: [constructors and shared preprocessing](../../../scripts/python/models/regression.py), [execution and verification](../../../scripts/python/run_regression.py).

Resolve candidates, metrics, predictions, preprocessing and reload checks through `artifacts.json`. Check actual cohorts, learner identities/settings and independently recomputed holdout metrics; exit status or model-file presence alone is insufficient. This directory duplicates no training code and adds no tool ID. Return to [family navigation](../../README.md).
