---
name: model-reproduction
description: Compare frozen keyed regression predictions, recompute metrics and diagnose source/preprocessing/split differences while preserving both result sets.
---

# Compare existing model results

**English** | [中文](SKILL_ZH.md)

Use `scripts/compare_existing.py` for a direct, reviewed comparison. It has no registered run-tool or MCP execution ID. The [method](../../../../methods/shared/model_reproduction.md) explains comparability and reliability judgments.

## Configure

Use the installed project Python environment and three existing separate ASSETS/CONFIG/AUTH roots from the [environment example](../../../../config/examples/environment.ps1). No model framework is needed for CSV/JSON comparison.

Copy the [complete task](../../../../config/examples/model-reproduction/compare-existing.json) to personal configuration, then adapt:

| Fields | Meaning |
|---|---|
| `project_id`, `target` | Shared project, target identity and unit |
| `candidate.root`, `reference.root` | Separate frozen result directories inside that external project |
| `manifest`, `prediction_origin` | File/hash inventory and origin of predictions |
| `models[].id` | Explicitly paired model identifiers |
| `predictions`, `id_column`, `truth_column`, `prediction_column` | CSV and column mappings |
| `reported_metrics` | Optional source JSON and metric pointers |
| `tolerances` | Truth/metric absolute and relative comparison tolerances |
| `output_files` | Optional artifact names within a new comparison directory |

See the [schema](../../../../catalog/schemas/model-reproduction-task.schema.json). A source-audit matrix is optional supplied evidence; the script does not audit arbitrary code automatically.

## Run the synthetic example

From the repository root:

```sh
python skills/model/shared/model_reproduction/scripts/make_synthetic_fixture.py --fixture-id synthetic_v1 --execute
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo --execute
```

The first command creates only synthetic evidence. The second preflights manifests/configuration without parsing predictions; the third compares them. Repeated runs need fresh names and a matching task copy. `--out-dir` can choose a fresh folder within the project result root.

## Check results

Expect `preflight_passed` before execution and `completed` after it. Read `artifacts.json`, comparison reports, own-cohort/common-ID metrics, unmatched IDs and source-preservation evidence. The five-row example expects candidate RMSE/MAE/R² = 0/0/1 and reference = 1/1/0.5.

Check matching truths/units, cohort coverage, metric assertions and numerical tolerances separately. Process completion does not imply metric assertions passed. A constant truth has no defined R²; an empty intersection has no paired score. Preserve both inputs and record any recovery or normalization separately.

For trusted saved forests, `reference_ranger.R` exposes `reference_ranger_model()`, `reference_ranger_predict()` and `reference_ranger_metadata()` to a reviewed R caller. It does not train or execute original source; model loading, preprocessing and path validation are caller responsibilities. Other formats need adaptation.

The [comparison workflow](../../../../workflows/model_reproduction/README.md) orders source review, alignment and diagnosis. [Synthetic fixture details](../../../../config/examples/model-reproduction/README.md) describe the example's artifacts; [asset storage](../../../../harness/assets.md) defines the external result boundary.
