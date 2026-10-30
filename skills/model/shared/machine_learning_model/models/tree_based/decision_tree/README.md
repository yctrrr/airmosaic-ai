# Decision-tree regression

**English** | [中文](README_ZH.md)

Select a bounded tree candidate and declare its complexity controls. The shared pipeline owns preparation, validation selection and final evaluation.

Scientific selection belongs to the [decision-tree method](../../../../../../../methods/shared/machine_learning_model/models/tree_based/decision_tree/README.md).

R uses `regr.rpart` with `cp`, `maxdepth`, `minsplit` and `minbucket`. Python uses `decision_tree` with `max_depth` and `min_samples_leaf`. Similar names do not make the R/Python fitted trees numerically identical.

## Configure and invoke

Prepare the [R environment](../../../references/operations.md) or [Python environment/task contract](../../../references/python-path.md), and follow the [shared review process](../../../references/planning.md). Commands below run from the repository root.

R: [complete task](../../../../../../../config/examples/machine-learning-model/r/decision_tree.synthetic.json), [runner parameters](../../../../../../../config/examples/run-tool/ml-model-r-decision-tree.json).

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/ml-model-r-decision-tree.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/ml-model-r-decision-tree.json --timeout 180
```

Python: [complete task](../../../../../../../config/examples/machine-learning-model/python/decision_tree.synthetic.json), [runner parameters](../../../../../../../config/examples/run-tool/ml-model-python-decision-tree.json).

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-decision-tree.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-decision-tree.json --timeout 180
```

Examples are for an authorized fixed synthetic replay. Python examples request no contribution computation; R tree/forest examples retain the permutation method required by the current R contract. Except for baseline-only tasks, candidates still compete with the mean baseline; selection may legitimately favor the baseline. Preview does not parse rows or prove dependencies. Actual execution uses the three roots and declared result scope for fresh artifacts. Do not reuse technical replay settings as a real-data plan.

## Implementation and checks

- R: [shared fitting](../../../scripts/r/models/fit.R), [held-out evaluation](../../../scripts/r/common/evaluate.R).
- Python: [constructors and shared preprocessing](../../../scripts/python/models/regression.py), [execution and verification](../../../scripts/python/run_regression.py).

Resolve candidates, metrics, predictions, preprocessing and reload checks through `artifacts.json`. Check actual cohorts, learner identities/settings and independently recomputed holdout metrics; exit status or model-file presence alone is insufficient. This directory duplicates no training code and adds no tool ID. Return to [family navigation](../../README.md).
