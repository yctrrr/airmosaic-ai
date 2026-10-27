---
name: timexer-forecasting
description: Explain and adapt the official TimeXer model for time-series forecasting with exogenous variables. Use for TimeXer method review, historical covariate input, training and evaluation setup, checkpoint inference planning, and tracking thuml/TimeXer within AirMosaic.
---

# TimeXer method and usage

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


TimeXer forecasts target time series using exogenous variables. This directory tracks the official [thuml/TimeXer](https://github.com/thuml/TimeXer) implementation, using its official spelling. It complements mlr3 tabular workflows and uses Python/PyTorch.

**Status:** `timexer_workflow_reference` is `reference / catalogued`, `execution.enabled: false`. AirMosaic supplies method/adaptation guidance, not training, inference or download adapters. It cannot run through run-tool. Upstream `run.py` is an external research entry point, not an AirMosaic tool ID.

## Workflow

1. **Define forecast origin:** target, sampling interval, history, horizon and use. Record whether each covariate is available at forecast time; observed future weather and retrospective revisions are not contemporaneously available inputs.
2. **Select the task:** verify `features=MS` for one target with covariates or `M` for multiple targets. The current model implements forecasting only; generic CLI classification/imputation options do not establish TimeXer support.
3. **Understand inputs:** read the [method and boundaries](references/method.md), distinguishing the paper from actual tensor inputs. The tracked code accepts historical covariates; known-future, mixed-frequency and multi-station panel data require adaptation.
4. **Prepare environment/data:** follow [usage](references/usage.md) for an independent environment, pinned commit, CSV order, time continuity and training-only scaling. Begin with synthetic checks; do not install the full old dependency set into the core environment.
5. **Train/evaluate:** set resources and time splits. Upstream benchmark training evaluates test error each epoch; adapt formal work to training/validation development and frozen held-out evaluation. Do not repeat permission requests for already authorized tasks.
6. **Predict new data:** retain configuration, weights, training scaler, column order, units and time encoding; implement history-only inference. `--is_training 0` still performs labeled testing, not production inference.
7. **Validate/record:** check forecast shape, times, units, baselines, horizon-specific errors, extremes and failed samples. Share sanitized summaries. Attention associations or predictive gains are not causal-effect evidence.

## Paths and credentials

- Inputs remain in `${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/` or authorized existing `output/`; new results use `output/<run_id>/timexer_workflow/`. The label is not a tool ID.
- Upstream source stays outside this repository, represented by local `TIMEXER_SOURCE_DIR`. It is not automatically loaded and grants no access to adjacent directories.
- Keep mappings/non-secret parameters in `AIRMOSAIC_CONFIG_DIR`. Local modeling requires no login or `AIRMOSAIC_AUTH_DIR` access. Data-portal acquisition follows its own workflow; tokens remain in a credential manager.
- Raw scripts do not inherit runner path preflight, timeout cleanup, environment isolation or sanitized receipts. Keep artifacts, logs, weights and row-level predictions in local task directories. Do not train from the shared repository root.

See the [storage contract](../../../../harness/storage-and-credentials.md), [agent boundaries](../../../../harness/agent-boundaries.md) and [machine-learning queries](../../../../harness/usage/machine-learning.md).

## Sources and validation

[Upstream tracking](UPSTREAM.md) records the paper, pinned commit, license review and update procedure. Current evidence covers source/parameter review and documentation/syntax checks, without PyTorch installation, data download or training. Do not report this as a successful model run.
