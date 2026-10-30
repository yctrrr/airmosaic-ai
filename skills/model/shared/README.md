# Shared modeling skills

**English** | [中文](README_ZH.md)

These operations apply across research stages and correspond to explanations in [methods/shared](../../../methods/shared/README.md). A particular study references the capability instead of copying it under each stage.

| Capability | Skill | Method | Execution status |
|---|---|---|---|
| Spatial analysis and mapping | [spatial_analysis](spatial_analysis/SKILL.md) | [Spatial relationships, CRS and support](../../../methods/shared/spatial_analysis.md) | R and Python direct helpers with synthetic checks; geocoding/raster guidance; no run-tool or MCP adapter |
| Machine-learning models, contribution and causal analysis | [machine_learning_model](machine_learning_model/SKILL.md) | [Regression targets, DAGs and interpretation](../../../methods/shared/machine_learning_model/README.md) | R: `ml_regression_workflow`; Python: `ml_python_regression_workflow`; causal PLR remains R-only |
| Reproduction and comparison | [model_reproduction](model_reproduction/SKILL.md) | [Comparison and reliability](../../../methods/shared/model_reproduction.md) | Reviewed direct comparison/recovery helpers; no new run-tool or MCP execution adapter |

`machine_learning_model/` is the shared machine-learning home. Its `models/` groups linear, tree-based and sequence references; `evaluation/` supplies the common baseline comparison; `frameworks/r/mlr3/` contains R framework guidance. Shared calculation code retains `scripts/r/` and `scripts/python/`. Framework and dedicated sequence entries keep their own contracts and reference status. The general [regression workflow](../../../workflows/ml_regression/README.md) documents data/skill combinations, while [projects](../../../projects/README.md) define particular scientific experiments.

For air-pollution tasks, read [process and impact methods](../../../methods/shared/air_pollution_regression.md), then the regression skill's [operating contract](machine_learning_model/references/operations.md) and [domain cases](machine_learning_model/references/air-pollution.md). Scientific examples do not add an executable model or causal estimand.

Stage-specific operations remain under their primary stage. Stage 02 receives conceptual method references only. Tool IDs and discovery depend on the catalog and explicit mappings, not folder names. See [classified usage](../../../harness/usage/machine-learning.md) and [the asset contract](../../../harness/assets.md). New generic regression results use `machine_learning_model/results/`, ignored by Git; prior local results remain in place without automatic migration.

Control costs, distributional scenarios and GCAM output analysis are maintained in [stage 04](../04_integrated_impacts/README.md). Other stages may reference those same skills without a duplicate in shared.
