# Random-forest regression

**English** | [中文](README_ZH.md)

A forest averages randomized trees to reduce instability relative to an individual tree. Per-split variable sampling, per-tree row sampling and tree complexity jointly affect diversity and local fit. More trees mainly improve numerical stability; they do not repair leakage, dependent samples or weak extrapolation. Assess prediction and interpretation stability under the intended evaluation design.

Parameter reasoning and cited evidence: [model comparison](../../README.md).

R uses ranger and Python uses scikit-learn; use backend-specific parameter meanings, ranges and seed handling. Configuration, code calls and current checks belong to the [matching skill](../../../../../../skills/model/shared/machine_learning_model/models/tree_based/random_forest/README.md).

Use the [shared evaluation design](../../../evaluation.md) and submit a [model plan](../../../../model_planning.md) before generating experiment code.
