# Common evaluation and the mean baseline

**English** | [中文](README_ZH.md)

The training-mean baseline is a common evaluation reference for all supported numeric regression candidates, not a separate research-model family. It predicts the training target mean for every holdout row. It never estimates that mean from validation/test outcomes.

## Existing R/Python behavior

- R automatically adds `regr.featureless` with `robust = FALSE` inside [shared fitting](../scripts/r/models/fit.R). Do not declare it in `models` or pass an empty candidate list. Metrics use [common evaluation](../scripts/r/common/evaluate.R).
- Python requires the existing `baseline_mean` candidate explicitly in task JSON; all supplied model examples already include it. The [shared constructor](../scripts/python/models/regression.py) uses `DummyRegressor(strategy='mean')`, and the [runtime](../scripts/python/run_regression.py) performs common scoring and independent checks. No automatic candidate insertion has been added.

Both retain the current candidate selection rule: validation loss can select the baseline if it performs best. The shared comparison is not restricted to forests. Candidate identities, parameter keys and selection calculations are unchanged.

## Configure, run and inspect

Use any [implemented model example](../models/README.md) to obtain the baseline and candidate scores together. Prepare the [R environment](../references/operations.md) or [Python task/environment](../references/python-path.md), then follow [plan review](../references/planning.md).

An optional baseline-only Python engineering check remains available as an evaluation fixture: [task](../../../../../config/examples/machine-learning-model/python/evaluation/baseline.synthetic.json), [runner parameters](../../../../../config/examples/run-tool/ml-evaluation-python-baseline.json). It is not the main model-selection entry.

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-evaluation-python-baseline.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-evaluation-python-baseline.json --timeout 180
```

Check `can_execute` and `blockers`, then actual process/artifact status. Resolve candidates, keyed predictions and metrics through `artifacts.json`; independently recalculate metrics on the same retained cohort and verify model reload. Preview does not train or read data rows. Keep fresh outputs within the selected runner's existing scope. Scientific comparisons need the [evaluation method](../../../../../methods/shared/machine_learning_model/evaluation.md), not engineering fixture settings.
