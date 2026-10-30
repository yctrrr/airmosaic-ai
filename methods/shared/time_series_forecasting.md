# Forecasting with target history and external variables

**English** | [中文](time_series_forecasting_ZH.md)

A forecast uses information available at a stated origin to estimate later values. Define the origin, sampling interval and horizon before constructing examples; a model should be assessed on the same information it will have in use.

## Define what is known

Separate target history, other observed histories and variables genuinely known for future periods. Revised observations and reanalysis can support retrospective studies while differing from operational inputs. Record release timing and uncertainty for each source.

Align series on the intended time axis. Missing periods, changes in sampling frequency and different entities need explicit handling. A window must belong to the same entity and must not silently cross a station boundary.

## Choose windows and baselines

History length decides what past patterns the model can use; horizon length determines how far ahead it must predict. Compare persistence and an appropriate seasonal reference before interpreting a more complex model's improvement. Longer histories and larger models require enough development windows and computational budget.

## Example model idea

[TimeXer](https://arxiv.org/abs/2402.19072v4) represents the target history in temporal patches and external histories as variable-level information, combining them through attention. This provides a way to use auxiliary series while preserving a distinct target role. It is a predictive architecture; attention patterns require separate scientific interpretation.

The tracked implementation's actual tensor/data contract is narrower than a general forecasting problem. Its [skill](../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL.md) explains which historical inputs are accepted and which future-variable, multi-entity or deployment operations need adaptation.

## Evaluate as a forecast

Use chronological development and holdout periods or a reviewed rolling-origin protocol. Account for overlap between windows and label periods. Fit scaling and other learned transformations within training data, then reuse them without fitting to each evaluation batch.

Report errors by horizon and entity where appropriate, with target units and inverse transforms clear. Decide whether repeated predictions for the same timestamp are scored by origin/horizon or combined under an explicit rule. Inspect extremes, missing forecasts and changing conditions.

## Preserve a usable model

A checkpoint alone does not define a forecasting system. Keep the feature order, fitted transforms, time encoding, source version, window design and model settings. Test new-history inference separately from scoring a labeled test set. The [operating reference](../../skills/model/shared/machine_learning_model/models/time_series/timexer/references/usage.md) provides the code-level handoff.
