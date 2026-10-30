# Machine-learning operations

**English** | [中文](machine-learning_ZH.md)

| Layer | Responsibility | Entry |
|---|---|---|
| Method | Target definition, feature roles, DAG identification, regression and interpretation assumptions | [Regression method](../../methods/shared/machine_learning_model/README.md) |
| Task skill | Reviewed target/feature preparation, fitting, evaluation, predictive explanation and supported causal estimation | [Regression skill](../../skills/model/shared/machine_learning_model/SKILL.md) |
| Model families | Linear regression, tree-based models and sequence references | [Model directory](../../skills/model/shared/machine_learning_model/models/README.md) |
| Common evaluation | Training-mean reference and shared candidate checks | [Evaluation](../../skills/model/shared/machine_learning_model/evaluation/README.md) |
| Software demonstration | Direct CPU synthetic Transformer input/training/reload cases; not a registered tool | [Software cases](../../skills/model/shared/machine_learning_model/references/transformer-software.md) |
| Framework skill | mlr3 environment, API and extension guidance | [mlr3](../../skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL.md) |
| Sequence reference | External Python/PyTorch TimeXer instructions; no runner adapter | [TimeXer](../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL.md) |
| Workflow | General data/skill combinations, DAG design step, branches and handoffs | [Regression combination](../../workflows/ml_regression/README.md) |
| Project | A particular question, experiments, comparisons and review | [Project 0001](../../projects/0001_ozone_environmental_drivers/README.md) |

The existing R executable ID remains `ml_regression_workflow`, with an mlr3 backend. The separate Python regression entry is `ml_python_regression_workflow`; its [language path](../../skills/model/shared/machine_learning_model/references/python-path.md) specifies the distinct task, dependencies and review bundle. `mlr3_workflow_reference` and `timexer_workflow_reference` remain non-executable guidance. Package APIs are not tool IDs.

```powershell
python -m runtime.cli list-tools --category model --query mlr3
python -m runtime.cli describe-tool ml_regression_workflow
python -m runtime.cli check-tool ml_regression_workflow
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/aq-bench-ml-regression.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-causal.json --dry-run
```

Use [prediction settings](../../config/examples/ml-regression/aq-bench-prediction.json) to configure target, features, train/validation/test labels, missingness, bounded rpart/ranger candidates, seeds and explanations. The training-only filter records missingness, variation, correlation and VIF diagnostics. Predictive explanations include permutation importance, PDP, ICE and optional empirical-background permutation Shapley estimates. These explain predictions, not causal effects.

Use [synthetic causal settings](../../config/examples/ml-regression/synthetic-causal.json) for one continuous-treatment, cross-fitted partially linear slope. It requires a declared DAG, total-effect adjustment set, manual covariates, complete cases, one nuisance specification and scientific assumptions. It supports independent-unit or independent-group folds; arbitrary causal estimands, IV/DID and automatic causal discovery need adaptation. The known-effect synthetic example is implementation evidence. Observational causal analysis requires a study-specific design.

No project ID selects the regression skill's local, Git-ignored `results/<run_id>/`. A project ID selects external `assets/results/<project_id>/`; `out_dir` and relative `output_files` may choose a useful internal layout. The adapter preserves existing files, creates internal `.airmosaic/<run_id>/` records/temp and writes `artifacts.json` for local discovery. Do not publish generated results. Other adapters retain their documented layouts.

Model computation needs no login or network. Set `AIRMOSAIC_R_LIBRARY` explicitly for a reviewed external package directory containing mlr3, mlr3learners, ranger, rpart and jsonlite; otherwise only standard R libraries are used. Personal startup files and implicit personal/site libraries are disabled. Three private roots remain required. MCP uses the same configuration and checks; execution requires the startup grant `--execute-tool ml_regression_workflow`.

Classification, other learners, automatic tuning, predictive cross-validation, new-data inference and general experiment orchestration require additional adaptation. The [published basis](../../skills/model/shared/machine_learning_model/references/published-basis.md) distinguishes source-informed design from numerical paper reproduction. Scientific review and approved data reuse remain separate from execution.


Synthetic workflow checks may explicitly select `result_scope=workflow`, limited by the [asset contract](../assets.md) to a fixed Git-ignored workflow result tree and manifest-listed synthetic inputs. Scientific projects retain external results; the default scope is unchanged.
