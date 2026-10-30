# Tree-based regression

**English** | [中文](README_ZH.md)

A decision tree partitions predictors and fits a local response in each leaf. A random forest combines multiple randomized trees and averages their predictions. They share a family, while their complexity and stability controls remain distinct.

| Model | R learner | Python learner | Configuration and calls |
|---|---|---|---|
| Single decision tree | `regr.rpart` | `decision_tree` | [Decision tree](decision_tree/README.md) |
| Random forest | `regr.ranger` | `random_forest` | [Random forest](random_forest/README.md) |

Both reuse language-specific preparation, fitting and [common evaluation](../../evaluation/README.md); no training code is copied into these navigation folders. R/Python parameters and seeds do not imply identical fits. Review the [scientific comparison](../../../../../../methods/shared/machine_learning_model/models/tree_based/README.md) and [plan](../../references/planning.md) before choosing settings. Return to [model families](../README.md).
