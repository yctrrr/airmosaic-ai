# Run and inspect Transformer software cases

**English** | [中文](transformer-software_ZH.md)

Scientific choices belong to [methods](../../../../../methods/shared/machine_learning_model/models/transformer/README.md) and its [data guide](../../../../../methods/shared/machine_learning_model/models/transformer/data.md). This reference provides concrete software operations and their actual verification scope.

## 1. Select software and environment

The direct example uses Python 3.11+, PyTorch 2.6+ and this repository checkout. Select a trusted environment whose `python` resolves to those dependencies. PyTorch CPU execution was checked on Python 3.14.4 and PyTorch 2.13.0+cpu on 2026-10-30. That is an environment receipt, not a requirement to upgrade other environments. Other versions/platforms need their own checks.

If dependencies are missing, prepare a separate environment using the [official PyTorch selector](https://pytorch.org/get-started/locally/) under the task's installation authorization. The helper never installs packages, requests credentials, downloads data/weights or selects a GPU. It needs no Lightning or Hugging Face dependency for these examples.

| Software reference | Useful operation | Adaptation boundary |
|---|---|---|
| [PyTorch Lightning skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/pytorch-lightning/SKILL.md) | Separate data, training, validation, checkpoint and prediction stages | Its classification template is not a numeric regression model; change the data contract, head, loss and metrics before use |
| [Transformers skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/transformers/SKILL.md) | Inspect model versions, local weights and supported inference/fine-tuning APIs | Text tokenization and language-model Trainer examples do not define an atmospheric numeric input contract |
| [TimeXer operations](../models/time_series/timexer/references/usage.md) | Use the actual upstream environment, CLI and input conventions | Custom splits, training-time test access, scaler persistence and history-only inference require adaptation |

The local helper was independently written using the first reference's separation of responsibilities, not copied from its classification scripts. These source links are references reviewed on 2026-10-30, not an automatic installation or update service.

## 2. Choose the bounded case and configuration

Use [the complete configuration](../../../../../config/examples/machine-learning-model/python/transformer.synthetic.json) and one declared case:

| Case | Generated input, including batch axis `B` | Encoder units |
|---|---|---|
| `tabular` | `static: [B, 4]` | Four numeric features |
| `sequence` | `history: [B, 8, 3]` | Eight historical steps |
| `grid` | `grid: [B, 1, 4, 4]` | Four non-overlapping spatial patches |
| `fusion` | All three inputs above | Separate projections and identity/position embeddings, concatenated for common self-attention |

No dataset or checkpoint input argument exists. A known synthetic scalar target combines all three internally generated sources; single-input cases receive only their declared source. The examples check software mechanics, not a scientific ranking of model families.

The JSON explicitly controls `samples`, `seed`, `d_model`, `heads`, `layers`, `epochs`, `batch_size`, `learning_rate`, `weight_decay` and `dropout`. It requires `purpose=synthetic_software_demo`. Counts govern independent generated cohorts, not a split prescription for real data. The helper rejects unknown fields, incompatible head dimensions, nonfinite settings and budgets beyond its small limits. This JSON is not a task accepted by either existing regression tool.

## 3. Prepare the separated roots and preview

Commands run from the repository root after selecting the intended Python environment. Create three separate existing roots outside Git, then set `AIRMOSAIC_ASSETS_DIR`, `AIRMOSAIC_CONFIG_DIR`, `AIRMOSAIC_AUTH_DIR` following [storage setup](../../../../../config/examples/README.md). This helper reads only the explicitly selected non-secret JSON under `config/examples/` or the personal configuration root; it does not load a profile or inspect authentication files.

Choose an unused external results directory. This PowerShell example uses the project's minute naming convention:

```powershell
$amCase = 'fusion'
$amTaskLabel = (Get-Date -Format yyyyMMddHHmm) + '_' + $amCase
$amOutput = Join-Path $env:AIRMOSAIC_ASSETS_DIR ('results/transformer_software_demo/' + $amTaskLabel)
python skills/model/shared/machine_learning_model/scripts/python/run_transformer_demo.py --case $amCase --config-file config/examples/machine-learning-model/python/transformer.synthetic.json --out-dir $amOutput --dry-run
```

Expected: `can_execute=true`, `blockers=[]`, `external_input_supported=false`, `output_created=false`. Preview validates paths, JSON and installed package metadata without importing Torch or generating tensors. It does not prove that a Torch installation can initialize. Missing Torch gives a dependency blocker instead of an installation attempt.

## 4. Execute and inspect the results

After preview, execute the same selected case and output path:

```powershell
python skills/model/shared/machine_learning_model/scripts/python/run_transformer_demo.py --case $amCase --config-file config/examples/machine-learning-model/python/transformer.synthetic.json --out-dir $amOutput
```

To try another case, choose its name and a fresh output path before repeating preview/execution. Changing the case alone while reusing an existing output directory fails; there is no overwrite switch. Outputs must be beneath external asset results, with at least a task folder and a fresh run folder. Linked locations, Git ancestors and reserved authentication/record names are rejected. Direct execution provides these checks, not OS isolation or the runner's minimal child environment.

| Artifact | What to inspect |
|---|---|
| `configuration.json`, `input-contract.json` | Actual case, counts, shapes, seed and train-only preprocessing |
| `events.jsonl` | Ordered, time-stamped epochs, validation criterion, checkpoint selection and later test evaluation |
| `metrics.json`, `predictions.csv` | Finite keyed predictions, independent RMSE/MAE/R² and training-mean reference |
| `checkpoint.pt` | Model parameters and training-fitted preprocessing; only this newly generated file is reloaded |
| `checks.json`, `status.json` | Finite nonzero gradients, metric agreement, reload equality, CPU/package versions and `scientific_acceptance=false` |
| `artifacts.json` | Relative file paths and checksums; absent on an incomplete run |

The implementation fits preprocessing on training inputs, trains on training labels, chooses a checkpoint by validation MSE, and generates/evaluates the test cohort only after that choice. It reloads its own checkpoint with `weights_only=True`. It does not open arbitrary saved models. Existing metric helpers are reused; network scores may be worse than the mean reference and must still be reported.

Events carry actual UTC times with an offset and record software actions/checks only. They do not capture a host agent conversation, a study's generation rationale or a retrospective scientific review; those follow the [workflow handoff contract](../../../../../harness/usage/workflow-handoff.md) when applicable.

Keep partial outputs and use a fresh destination after investigating a failure. Typical codes are `missing_separated_roots`, `demo_configuration_root`, `demo_budget_exceeded`, `demo_output_exists` and `demo_unsafe_output`; `missing_torch` is a preview blocker. Do not move data into an authentication root or relabel a real task to make it fit this example.

## 5. Hand off a real study separately

Real tables, observations, raster files, text, missing-modality inputs, irregular windows, GPU/distributed training and arbitrary pretrained weights are unsupported by this helper. It has no run-tool/MCP registration and no scientific plan-approval gate, because its sole accepted task is this internal synthetic demonstration. New scientific use still follows [planning and review](planning.md), with an actual loader, explicit sample keys, availability/split rules and a reviewed execution adapter.

Keep generic code in skills and scientific design in methods; workflows may refer to these cases without copying the training logic. Project results retain external `assets/results/<project_id>/` organization, with task-specific internals. No example output is automatically promoted into shared data or committed.
