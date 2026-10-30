---
name: timexer-forecasting
description: Prepare and adapt the tracked TimeXer forecasting implementation for a target series with historical exogenous variables.
compatibility: "Python; PyTorch; TimeXer"
metadata:
  version: "1.0.0"
  reviewed: "2026-10-29"
---

# Use TimeXer

**English** | [中文](SKILL_ZH.md)

`timexer_workflow_reference` is a non-executable catalog reference. Run reviewed upstream code in its own environment; AirMosaic has no TimeXer training/inference adapter.

This sequence reference is part of the parent [machine-learning capability](../../../SKILL.md). Read the [matching human-facing method](../../../../../../../methods/shared/machine_learning_model/models/time_series/timexer/README.md) before adapting the code.

## Configure the task

Use [upstream tracking](UPSTREAM.md) for the reviewed source commit and dependencies. Keep its source outside this checkout, referenced by `TIMEXER_SOURCE_DIR`. Use an independent Python/PyTorch environment.

| Setting | Required decision |
|---|---|
| Target and time | Target column, sampling frequency, forecast origin and horizon |
| Input | Ordered regular-time CSV with a date column and numeric variables; one entity per sequence |
| Roles | `MS` for multivariate history with one target, `M` for multivariate outputs |
| Windows | `seq_len`, `pred_len`, `patch_len`; preserve sufficient history and target-patch divisibility |
| Model/budget | Dimensions, heads, layers, batch size, epochs, workers and device |
| Storage | Fixed input version and fresh external project result directory |

## Use the code

[Usage and command example](references/usage.md) contains the complete upstream `run.py` call and dependency/input checks. Begin with enough synthetic history. Run from a new project result folder so relative checkpoint, prediction and log files remain there.

1. Validate timestamps, gaps, numeric types, target order and training-only scaling.
2. Set the history and horizon in sampling points, then choose compatible model dimensions.
3. Review the supplied chronological split and validation criterion before training.
4. Preserve configuration, weights, scaler, feature order and time encoding.

The tracked model consumes historical inputs. Known-future covariates, mixed frequencies and multiple entities need a data/model adaptation. The tracked benchmark prints test errors during training; an independent final-test protocol needs explicit handling.

## Check results

Check forecast origins, horizons, shapes, finite values, target units and inverse scaling. Compare persistence/seasonal baselines and inspect errors by horizon/entity. Preserve checkpoint identity and the exact training environment.

`--is_training 0` is labeled testing, not history-only deployment inference. Implement and verify scaler reuse and a history-only input contract before using new unlabeled batches. Source-specific seed/device/checkpoint details are in the usage reference.

The [forecasting method](../../../../../../../methods/shared/time_series_forecasting.md) explains the research design. Tensor details remain in [the technical reference](references/method.md); [asset storage](../../../../../../../harness/assets.md) governs study outputs.
