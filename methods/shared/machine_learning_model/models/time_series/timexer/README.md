# TimeXer forecasting

**English** | [中文](README_ZH.md)

The tracked model uses a target history with historical exogenous series for forecasting. Distinguish information available at the forecast origin from future observations. Specify sampling interval, history and horizon, target/covariate roles and whether the goal is retrospective evaluation or deployment. Use chronological development and a separately protected final test; compare relevant persistence or seasonal references.

Scientific background: [time-series design](../../../../time_series_forecasting.md).

AirMosaic currently provides an external Python/PyTorch reference, not a controlled training/inference adapter. Future-known covariates, multiple entities and history-only inference require explicit adaptation. Configuration, code calls and current checks belong to the [matching skill](../../../../../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL.md).

Use the [shared evaluation design](../../../evaluation.md) and submit a [model plan](../../../../model_planning.md) before generating experiment code.
