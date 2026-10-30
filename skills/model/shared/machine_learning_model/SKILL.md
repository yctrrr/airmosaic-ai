---
name: machine-learning-model
description: Plan and review numeric machine learning studies, route R/Python prediction, or run CPU-only synthetic Transformer software cases; keep predictive contribution and causal estimation distinct.
compatibility: "Core Python 3.10+; R path requires Rscript and declared packages; Python training requires Python 3.11+ and separate dependencies; CPU Transformer cases require PyTorch 2.6+"
metadata:
  version: "3.2.0"
  reviewed: "2026-10-30"
---

# Machine learning model

**English** | [中文](SKILL_ZH.md)

Use this skill for numeric prediction, predictive contribution and separately justified causal estimation. [Human-facing methods](../../../../methods/shared/machine_learning_model/README.md) explain scientific choices; this entry routes actual operations. Framework guidance and dedicated sequence references now live inside this capability, with their own contracts and execution status.

## Plan, review and prepare

Before generating experiment code, use [model planning](../../../../methods/shared/model_planning.md) and the [plan/review contract](references/planning.md). Save reasons, evidence, alternatives and uncertainty. Human review is the default; agent judgment requires explicit user delegation bound to the exact plan. Do not copy historical studies, sample splits or parameter choices as defaults. Check unchanged task/data, exact generated code, synthetic evidence and preflight before execution. The common helper is `scripts/common/review_plan.py`; review records attest trusted caller decisions, not identity or permissions.

Define the target, each variable's role/units/timing, source/product lineage and observation overlap. Design spatial/time or group holdouts before preprocessing; train-only transforms and screening must not see holdout information. Keep row limits separate from scientific sample design. Retain source, usable and selected counts and exclusion reasons. Stage 02 discussions remain conceptual. See [common design](../../../../methods/shared/machine_learning_model/common.md).

## Select only the needed branch

For a model-first route, open the [model-family directory](models/README.md): [linear regression](models/linear_regression/README.md), [tree-based models](models/tree_based/README.md), or the [time-series reference](models/time_series/README.md). Decision trees and random forests share the tree family. The mean baseline belongs to [common evaluation](evaluation/README.md), not to a separate research-model family. Each implemented model links its R/Python configurations and shared calculation code.

Read [mlr3 framework guidance](frameworks/r/mlr3/SKILL.md) for direct R API examples and extensions. The nested [TimeXer skill](models/time_series/timexer/SKILL.md) retains external Python/PyTorch instructions and remains reference-only; consolidation does not enable a new runner.

| Operation | Runtime and reference |
|---|---|
| R data preparation, fitting and held-out evaluation | [R operations](references/operations.md): registered `ml_regression_workflow`, adapter `mlr3_regression`, prepared CSV plus existing task JSON |
| Python numeric prediction | [Python path](references/python-path.md): separate dependencies, task contract and `ml_python_regression_workflow`; implemented with its separate documented checks and supported limits |
| Transformer software operation cases | [Software guide](references/transformer-software.md): direct CPU synthetic table, sequence, grid and fusion helper; Python 3.11+ and Torch 2.6+, no registered adapter or external-data option |
| Model families, settings and fixed-fold reproduction | [Models](references/models.md); select declared candidates through configuration rather than copied per-model pipelines |
| Development-only automatic tuning | [Direct R path](references/automatic-tuning.md): grouped fixed-fold AutoTuner helper; base contracts checked, full tuning pending the required dependency environment; no runner adapter |
| Predictive contribution | [Contribution](references/contribution.md): permutation/PDP/ICE/Shapley explain fitted predictions |
| Causal effect | [Causal](references/causal.md): R continuous-treatment PLR, declared DAG/manual adjustment and justified assumptions |

R and Python are distinct runtime paths; a Python caller invoking the R tool still requires R. Their task contracts are not interchangeable. The common plan contract retains the supported scientific/runtime distinctions and must pass the selected runtime's task validation.

## Run and verify

For an explicitly requested fixed synthetic R replay, from repository root:

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --timeout 180
```

Inspect `can_execute` and `blockers` before execution. Dry-run does not parse rows or prove dependencies. [R operations](references/operations.md) retains complete environment, configuration-writing, CLI/Python/MCP calls, supported bounds and artifact-reading examples. Check actual process success, artifact contents, retained samples/features, independently recomputed held-out metrics and model reload. Explanations need their declared background and uncertainty; PLR needs additional scientific identification review. Return the artifact index, checks and unresolved limitations. A technical replay is not scientific validation or approval of a new study.

Keep raw data, credentials, personal plans and generated study results outside Git under the [storage contract](../../../../harness/assets.md). Use the selected runner's declared result scope and fresh output directory; never move historical outputs during source maintenance. [Air-pollution cases](references/air-pollution.md), [published basis](references/published-basis.md) and the [workflow](../../../../workflows/ml_regression/README.md) are optional task-specific references. The [migration map](references/layout.md) identifies module homes and runtime boundaries.
