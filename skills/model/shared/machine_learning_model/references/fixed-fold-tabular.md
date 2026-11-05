# Explicit fixed-fold numeric-table models

**English** | [中文](fixed-fold-tabular_ZH.md)

These direct Python modules require a reviewed plan, numeric predictors, finite targets, frozen development folds and an untouched outer test set. They are not new run-tool/MCP operations. Existing registered tools and synthetic Transformer demos retain their contracts.

## Classical path

Load [fixed_fold_regression.py](../scripts/python/models/fixed_fold_regression.py). Requirements: NumPy, scikit-learn and threadpoolctl. `candidates(search_space, n_iter=..., seed=...)` freezes parameter draws. `fit_once(X_train, y_train, family=..., parameters=..., seed=..., max_threads=...)` fits exactly once and returns a pipeline.

Supported families are `linear_regression`, `decision_tree`, `random_forest`, and `histogram_gradient_boosting`. Supply explicit parameters; histogram boosting requires `early_stopping=False` so an implicit random validation split cannot replace the reviewed folds. Imputation and optional linear scaling are fitted on training rows only. The caller supplies purged training indices independently from validation indices; this API does not construct geographic folds.

## Neural path

Load [tabular_torch.py](../scripts/python/models/tabular_torch.py). Requirements: NumPy and CPU PyTorch. Inputs are numeric `[rows, features]`, without target, identifiers, coordinates or dates unless individually approved as predictors. The feature count is configurable.

- `mlp`: specify `hidden`, `dropout`, `learning_rate`, `weight_decay`.
- `numerical_tabular_transformer`: specify `d_model` (divisible by four), `layers`, `dropout`, `learning_rate`, `weight_decay`. Per-feature linear tokens, a CLS readout and pre-normalized attention form an FT-inspired adaptation, not an exact published-architecture reproduction.

```python
fit = neural.fit_tabular(
    X_train, y_train, family=family, config=reviewed_config, seed=seed,
    max_epochs=reviewed_epoch_cap, batch_size=reviewed_batch_size,
    x_validation=X_validation, y_validation=y_validation,
    patience=reviewed_patience, min_delta=reviewed_min_delta,
    max_seconds=reviewed_fit_seconds, max_threads=reviewed_threads,
)
predicted = neural.predict(fit["model"], fit["artifact"]["preprocessing"], X_validation)
neural.save_model(fit["artifact"], fresh_checkpoint)
model, artifact = neural.load_model(fresh_checkpoint, max_threads=reviewed_threads)
```

`neural` is the loaded module. Training-only medians and feature/target means and standard deviations are retained in the checkpoint. Predictions return original target units. Missing targets and wholly missing training predictors are refused. For final fits, omit validation and supply an epoch count already selected from development folds. Retain each seed's predictions when averaging seeds.

## Controller and checks

The caller must bind plan/input/code hashes, reserve each fit before spawning a worker, count failed attempts, limit native/Torch threads, apply hard process deadlines and preserve incomplete jobs without hidden retries. The helper's cooperative deadline alone is insufficient. Select parameters/epochs/seeds only within development. Reload own hash-verified final checkpoints, predict every common held-out row, independently recompute physical-unit RMSE/MAE/R² and verify prediction equality without additional fitting. Keep grid inputs and seed predictions in the manifest. A synthetic implementation check does not certify a new real-data study.
