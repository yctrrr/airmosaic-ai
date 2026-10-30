# Module layout and migration

**English** | [中文](layout_ZH.md)

Public source moved from `skills/model/shared/ml_regression/` to `skills/model/shared/machine_learning_model/`. The former empty skill shell and stale cache have been removed. This source consolidation does not move result artifacts.

Model navigation now groups `models/linear_regression/`, `models/tree_based/{decision_tree,random_forest}/` and `models/time_series/timexer/`. The mean baseline belongs to `evaluation/`. The former shared `mlr3/` guidance is retained under `frameworks/r/mlr3/`; its reference tool and the TimeXer reference keep their identifiers and remain non-executable. Their source tracking, examples and metadata are preserved. Human-facing model families mirror these under `methods/shared/machine_learning_model/models/`.

Executable code retains `scripts/r/` and `scripts/python/` with shared planning under `scripts/common/`. Model-family folders provide navigation and contracts rather than duplicate training pipelines. R still adds the mean baseline automatically; Python still requires its explicit candidate. Selection and calculation logic are unchanged.

| Former relative path | Current relative path |
|---|---|
| `scripts/run_regression.R` | `scripts/r/run_regression.R` |
| `scripts/lib/io.R` | `scripts/r/common/io.R` |
| `scripts/lib/target.R` | `scripts/r/common/target.R` |
| `scripts/lib/prepare.R` | `scripts/r/common/prepare.R` |
| `scripts/lib/select.R` | `scripts/r/common/select.R` |
| `scripts/lib/evaluate.R` | `scripts/r/common/evaluate.R` |
| `scripts/lib/fit.R` | `scripts/r/models/fit.R` |
| `scripts/lib/reproduction.R` | `scripts/r/models/reproduction.R` |
| `scripts/lib/explain.R` | `scripts/r/contribution/explain.R` |
| `scripts/lib/causal.R` | `scripts/r/causal/causal.R` |
| `scripts/review_plan.py` | `scripts/common/review_plan.py` |

The R module algorithm bodies are preserved. Only the entrypoint source vector changes to resolve the new module locations, in the same order: I/O, target, selection, preparation, fitting, evaluation, contribution and causal. The separate reproduction library remains an explicit caller dependency. The runner sets `AIRMOSAIC_R_ENTRYPOINT`; source locations resolve from that entrypoint directory. R direct invocation is not a substitute for the runner's task validation and output protections.

The registered R ID remains `ml_regression_workflow`, adapter `mlr3_regression`; its task schema, default learners and PLR restrictions remain unchanged. Python lives in `scripts/python/` with its own contract/dependencies and tool `ml_python_regression_workflow`; see [its actual supported behavior](python-path.md). No R library is automatically required by a validated Python-only path. The common planning helper is not a numeric training runtime.

The former `methods/shared/ml_regression.md` scientific body is retained in [common design](../../../../../methods/shared/machine_learning_model/common.md) (sections 1–4 and 8 plus planning), [models](../../../../../methods/shared/machine_learning_model/models/README.md) (section 5), [contribution](../../../../../methods/shared/machine_learning_model/contribution.md) (section 6) and [causal](../../../../../methods/shared/machine_learning_model/causal.md) (section 7), with an [index](../../../../../methods/shared/machine_learning_model/README.md). General planning and reproduction methods retain their existing homes.
