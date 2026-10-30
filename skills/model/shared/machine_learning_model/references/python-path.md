# Python regression path

**English** | [中文](python-path_ZH.md)

This page describes the registered sklearn regression adapter. For direct CPU synthetic Transformer software cases, use the separate [software guide](transformer-software.md); its configuration is not accepted by `ml_python_regression_workflow`.

Use `scripts/python/run_regression.py` through registered tool `ml_python_regression_workflow` for a bounded regression engineering run. The configuration schema is `catalog/schemas/python-ml-regression-task.schema.json`; the complete synthetic example is `config/examples/machine-learning-model/python/synthetic-regression.json`. This path implements prediction regression; Python causal PLR remains planned. See [the shared skill](../SKILL.md) for scientific preparation and review.

The input is one prepared CSV with unique, nonempty supplied IDs, an explicit target, explicit feature list, and explicit distinct train/validation/test labels. Every label must be declared; duplicate IDs across any labels are rejected. No random split is inferred. Raw input is read without modification. `prepared.csv` preserves original columns/cell strings for retained rows, while predictions retain IDs and original source-row numbers. This checks the supplied table, not upstream source lineage or scientific suitability.

Choose missing policy `error`, `drop`, or `impute`, plus numeric sentinels. Missing targets are excluded under `impute`; feature imputation uses training medians or training most-frequent categories. Counts by split and column, and keyed excluded rows, are recorded in `preprocessing.json`. Numeric scaling, imputation and one-hot encoding are fitted inside each pipeline on train rows only. Unknown validation/test categories map to all-zero one-hot indicators. All-missing training features and excessive category counts fail. IDs, split and target cannot be features. Manual feature selection is the only implemented selection mode.

Include an explicit `baseline_mean` candidate and choose among `linear_regression`, `decision_tree`, and `random_forest`. No arbitrary estimator, expression, callback or supplied serialized model is accepted. Tree depth and forest size must be explicit. At most eight candidates, 512 trees per forest, 1024 trees across candidates, 100000 rows per split, and five million dense preprocessing cells are allowed; tighter caller row limits fail rather than sample. Forest threads are fixed to one. Candidate parameters are explicit fixed trials, not a CV tuning engine. Every candidate fits train only; minimum validation RMSE selects the first candidate on a tie. The chosen pipeline stays frozen, with no validation refit, before final test predictions. Test metrics never choose candidates. Saved model reload and independently computed RMSE/MAE checks are required for completion. R/Python forest numerical equivalence is not guaranteed.

`explanation.methods` separately selects descriptive `permutation`, `pdp`, `ice`, or `shap`. Contributions use bounded validation rows, with dependence grids and SHAP backgrounds from training rows. Permutation reports validation MSE increase; PDP/ICE support numeric features. SHAP requires the optional `shap` package and explicit `shap_algorithm=permutation`, `shap_background=training_first_rows`, `shap_output=raw_prediction`, and evaluation budget. SHAP currently supports finite numeric raw features only; its base value plus feature contributions must match prediction within tolerance. Missing requested dependencies/capabilities fail explicitly; no successful explanation is fabricated. None of these contributions identifies a causal effect.

The artifact manifest uses the shared roles: target contract, prepared data, preprocessing, feature selection, candidates, saved model, keyed predictions, metrics, provenance, reproducibility, status, and selected contribution tables. Safe relative names can be changed with `output_files`; `artifacts.json` is fixed and the Python model suffix remains `.joblib`. Existing artifact paths are rejected. The sole runtime deserialization is the trusted model freshly saved in that execution. The runner owns destination/path/environment and reviewed-plan protections; direct scripts do not inherit its storage boundaries.

For a new study set `execution.purpose=new_study` and supply the reviewed plan bundle through `--review-bundle`. The shared gate binds the exact input, normalized task, plan review, reviewed generated caller and current fixed implementation. Engineering examples use `engineering_replay`; the runner restricts them to hash-verified manifest-listed repository synthetic data. A direct-script engineering label alone cannot certify synthetic origin or scientific acceptance.

Example (after selecting a trusted Python environment containing `numpy`, `scikit-learn`, `joblib`, `jsonschema`; SHAP only when requested):

```sh
python skills/model/shared/machine_learning_model/scripts/python/run_regression.py --input-csv assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv --task-config config/examples/machine-learning-model/python/synthetic-regression.json --out-dir <fresh-authorized-result-directory>
```

This example is an engineering replay only. Model fitting and reload are operational checks, not real-data validation or scientific acceptance. Version receipts are recorded per run; no dependencies are automatically installed by the workflow.

API references: [sklearn OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html), [SHAP PermutationExplainer](https://shap.readthedocs.io/en/stable/generated/shap.PermutationExplainer.html).

## CLI and MCP entry

Use an environment containing the core project plus the selected dependencies. Tested Python packages are scikit-learn 1.9.1, NumPy 2.5.4, SciPy 1.18.1 and joblib 1.6.0; the optional SHAP path was exercised with SHAP 0.54.1 in an isolated Python 3.14 environment. This is a checked snapshot, not an instruction to upgrade every environment.

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/synthetic-python-regression.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/synthetic-python-regression.json --timeout 180
```

The three separate roots are required. The main project environment was not changed by these checks. For new studies use the [shared plan/bundle procedure](planning.md); there is no self-approval flag. MCP uses the same tool and parameters, preview defaults and startup execution grant `--execute-tool ml_python_regression_workflow`.
