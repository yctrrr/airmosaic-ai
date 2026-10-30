# Predictive contribution

**English** | [中文](contribution_ZH.md)

Use [the interpretation method](../../../../../methods/shared/machine_learning_model/contribution.md) to decide the population, comparison and uncertainty the explanation represents. Contributions describe a fitted prediction model; they do not identify causal effects.

The implemented R module [`contribution/explain.R`](../scripts/r/contribution/explain.R) runs validation permutation importance, training-background PDP/ICE and optional empirical-background Shapley estimates. It shares the fitted bundle and common preprocessing; it is not a separate CLI or another fitting pipeline. Configure `explanation` in the existing R task. [R settings](operations.md#8-supported-settings) retain exact sample, feature, grid and computation bounds.

Run through the [R operations](operations.md), then inspect requested explanation roles via `artifacts.json`, background/sample choices, units, categorical levels, dependence and uncertainty. Optional output absence must match the requested settings. Python prediction availability does not imply Python explanation support; check the [Python path](python-path.md).
