# Model families

**English** | [中文](README_ZH.md)

Choose a family, then its implemented R/Python path. Configuration and shared code remain separate from this model navigation.

| Family | Entry | Current status |
|---|---|---|
| Linear regression | [Linear regression](linear_regression/README.md) | Python predictor; R adapter not enabled |
| Tree-based models | [Decision tree and random forest](tree_based/README.md) | Both R and Python regression paths |
| Transformer software cases | [Table, sequence, grid and fusion](transformer/README.md) | Direct Python CPU synthetic helper; no real-data or run-tool adapter |
| Time-series models | [TimeXer](time_series/README.md) | External Python/PyTorch guidance only; no run-tool adapter |

The [mean baseline](../evaluation/README.md) belongs to common evaluation and is not a model-family choice. Read [contribution](../references/contribution.md) and [causal](../references/causal.md) separately. No classification, clustering, boosting or additional neural training adapter is enabled by this index.

Complete tasks and runner parameters remain in `config/examples/`. Registered regression examples replay manifest-listed synthetic inputs; the Transformer helper generates its own independent inputs. Their counts and caps do not prescribe scientific samples or splits. New studies require [plan review](../references/planning.md). Framework API guidance lives under [R/mlr3](../frameworks/r/mlr3/SKILL.md); shared calculation code keeps `scripts/r/` and `scripts/python/`.
