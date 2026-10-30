# Common evaluation references

**English** | [中文](evaluation_ZH.md)

The mean baseline asks whether predictors improve on a constant prediction. Compute the target mean from the usable training cohort and use that same constant on validation/test rows. Learned target transformations, if any, must follow the declared training-only contract and reported outcome scale.

Compare every candidate and reference on identical sample keys, units, exclusions and loss definitions. Validation chooses candidates; the frozen final test assesses the agreed procedure. Retain RMSE and MAE in outcome units and inspect bias and important subgroups. A complex model can lose to the baseline; report that result rather than discarding the reference.

Test R² defined as `1 - SSE/SST` uses the test-set outcome mean in `SST`. That normalization is not the fitted training-mean baseline and does not authorize using test outcomes to fit a predictor. Keep the explicit baseline RMSE/MAE comparison as well.

For forecasting, persistence or seasonal references may be scientifically more informative. Declare them in the plan and verify an implementation rather than assuming the tabular mean baseline covers every task. Current [common skill evaluation](../../../skills/model/shared/machine_learning_model/evaluation/README.md) documents the actual R/Python support. Model selection reasoning remains in [model families](models/README.md); [common design](common.md) owns the split and preprocessing rationale.
