# Model families and fitting

**English** | [中文](models_ZH.md)

Browse the [model-family directory](../models/README.md) for linear models, the tree family and reference-only sequence models. Decision trees and random forests share one family; the [baseline belongs to common evaluation](../evaluation/README.md). Implemented models link full per-language task/runner examples. This reference describes the common fitting interface.

Choose the scientific family with [model comparison methods](../../../../../methods/shared/machine_learning_model/models/README.md). The R path currently supports a mean baseline plus declared `regr.rpart` and `regr.ranger` candidates. Learner choice and bounded parameters belong in the existing task JSON; no per-family pipeline copy is needed. [R operations, supported settings](operations.md#8-supported-settings) records exact bounds, defaults, validation selection and absent tuning/CV/refitting. Python families and dependency checks are declared separately in the [Python path](python-path.md).

Common preparation lives in `scripts/r/common/`. The R fitting module is [`scripts/r/models/fit.R`](../scripts/r/models/fit.R), followed by held-out [`evaluate.R`](../scripts/r/common/evaluate.R). [`reproduction.R`](../scripts/r/models/reproduction.R) is a separate development-only fixed-fold forest library; it is not called by the registered prediction entry. Source [`io.R`](../scripts/r/common/io.R) before calling `reproduction_forest()` or `reproduction_search_forest()`. Preserve externally fixed folds and keep test rows outside search. See the independent [reproduction method](../../../../../methods/shared/model_reproduction.md).

Use the [complete R calls and result checks](operations.md), including candidate metrics, actual cohorts, saved preprocessing, frozen predictions, independent metric recalculation and reload equality. A successful model fit does not establish scientific validity.

For development-only package-driven parameter search, use the separate [automatic-tuning helper](automatic-tuning.md). It takes reviewed grouped folds and bounded ranges; the registered fitting modules above do not invoke it or accept its settings. Its full dependency-based execution remains separately recorded.
