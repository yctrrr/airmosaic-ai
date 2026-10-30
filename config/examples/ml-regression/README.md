# Regression task settings

**English** | [中文](README_ZH.md)

These are non-secret task settings for [the regression skill](../../../skills/model/shared/machine_learning_model/SKILL.md), not runner parameter envelopes. `config/examples/run-tool/` contains the separate input/task path objects.

| Example | Meaning |
|---|---|
| [aq-bench-prediction.json](aq-bench-prediction.json) | A numeric station target, explicit predictors and published split; bounded predictive example |
| [synthetic-causal.json](synthetic-causal.json) | Known-effect synthetic treatment/outcome, declared DAG and cross-fitted PLR |

Copy a selected task into personal CONFIG_DIR and change only supported fields: target/unit/definition, features and exclusions, ID/split labels, missingness, candidates, seeds, limits and explanation methods. For training-only filtering, set `feature_selection.mode` to `train_filter`. Causal settings require manual covariates, complete cases, a suitable DAG/adjustment set and declared assumptions. Natural-language `requirements` records intent; it does not execute code or automatically choose a model.

`output_files` can rename scientific artifacts within the chosen output folder, for example:

```json
{"output_files":{"metrics":"statistics/evaluation.json","model":"models/selected.rds"}}
```

`artifacts.json` keeps its fixed name for local discovery. Do not use absolute paths, traversal, secret/internal directories, nested checkouts or conflicting filenames. Existing artifacts are preserved. For a particular project, the runner parameter JSON may set:

```json
{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/AQbench_dataset.csv","task_config":"config/examples/ml-regression/aq-bench-prediction.json","out_dir":"${AIRMOSAIC_ASSETS_DIR}/results/example_project/experiment-a"}
```

Use that runner JSON with `--project-id example_project --dry-run` first. Supply no project ID for the default generic skill result scope. A project manifest is not a task setting or automatically loaded configuration. Keep personal paths and generated results out of public examples.
