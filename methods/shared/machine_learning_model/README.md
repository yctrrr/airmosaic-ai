# Machine learning model methods

**English** | [中文](README_ZH.md)

Regression relates a numeric outcome to a set of variables. A useful study defines the question, separates model development from evaluation, and explains what its results mean. This guide follows that sequence; the [regression skill](../../../skills/model/shared/machine_learning_model/SKILL.md) supplies configuration and code.

Read [common design](common.md) for the question, variable roles, product lineage, sampling, preprocessing, spatial/time validation and result review. Then choose [models](models/README.md), [predictive contribution](contribution.md), or [causal design](causal.md). Contribution describes fitted predictions; causal effects require a separately justified identification design.

The model directory groups [linear regression](models/linear_regression/README.md), [tree-based models](models/tree_based/README.md) and [time-series models](models/time_series/README.md). Decision trees and random forests share the tree family. The training-mean baseline is a [common evaluation reference](evaluation.md), not a separate research-model category. These method pages explain scientific choices; matching skill pages own configuration, code and actual runtime status.

The cross-task [Transformer architecture method](models/transformer/README.md) explains attention and study design; its [data guide](models/transformer/data.md) distinguishes tables, sequences, grids and mixed sources. This is a method reference, not a newly enabled model. Existing specialist entries keep their current locations.

The [planning method](../model_planning.md), [requirements-driven building](../requirements_driven_model_building.md), and [reproduction method](../model_reproduction.md) remain authoritative for their own decisions. Select the runtime only after the scientific design: the [skill](../../../skills/model/shared/machine_learning_model/SKILL.md) routes R and Python implementations. Stage 02 use remains conceptual only.

The [automatic parameter-selection method](tuning.md) explains development-only search, grouped validation, final refitting and test isolation; its linked skill reference records actual configuration and runtime limits.
