# R path: configure and run regression

**English** | [中文](operations_ZH.md)

This reference gives setup, working code and the interfaces used by [the skill](../SKILL.md). Commands run from the repository root.

## 1. Prepare the environment

Use Python 3.10+ with the project installed. In a selected project environment, initial installation is `python -m pip install -e .`. Rscript must be available to the runner.

Replace the two placeholders below with your existing locations. The environment helper sets three sibling roots: `assets`, `config`, and `auth`; create these directories outside Git before running. Select an R dependency library separately:

```powershell
$amLocalRoot = "<existing-local-root-outside-git>"
. ./config/examples/environment.ps1 -LocalRoot $amLocalRoot
$env:AIRMOSAIC_R_LIBRARY = "<existing-r-package-library-outside-git>"
```

R needs `mlr3`, `mlr3learners`, `ranger`, `rpart`, `jsonlite`. This Python check uses the same explicit library selection as execution:

```python
import os
import subprocess

env = os.environ.copy()
for name in ("R_LIBS", "R_LIBS_USER", "R_LIBS_SITE"):
    env[name] = os.environ["AIRMOSAIC_R_LIBRARY"]
packages = "c('mlr3','mlr3learners','ranger','rpart','jsonlite')"
code = f"stopifnot(all(vapply({packages}, requireNamespace, logical(1), quietly=TRUE)))"
subprocess.run(["Rscript", "--vanilla", "-e", code], env=env, check=True)
```

For an authorized first installation, replace the `code` assignment in the check with the following line, run it, then rerun the dependency check:

```python
code = f"install.packages({packages}, lib=Sys.getenv('AIRMOSAIC_R_LIBRARY'), repos='https://cloud.r-project.org')"
```

Package installation uses the network. The runner uses the selected library without installing packages or loading personal R startup files.

For a new study, complete the [plan and review checks](planning.md) before generating experiment task/caller files. The fixed example below is a technical replay for explicit replay requests, not a default study plan.

## 2. Run the included example

The [synthetic parameters](../../../../../config/examples/run-tool/synthetic-regression.json) select a registered synthetic CSV and a complete [prediction task](../../../../../config/examples/ml-regression/workflow-synthetic.json). No workflow program is needed:

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --timeout 180
```

A successful preflight has `can_execute=true` and an empty `blockers` list. R dependencies remain `unverified` until execution; data rows are not parsed by preflight. Actual success is `status=succeeded`, with `artifacts.json` in the result folder.

## 3. Configure your own data

Use one prepared CSV: unique nonblank sample IDs, numeric target, declared predictors and existing train/validation/test labels. Declare categories in `categorical_features`. Repeated station observations need a station-period sample ID and separately designed group/time validation.

The following code reads a personal plan and actual review evidence, then creates new task/runner JSON only after the generation check. Prepare plan/review records using the [plan contract](planning.md); agent review additionally needs actual delegation. Adapt the input location to the planned data. Templates illustrate structure; executable settings come from the approved plan:

```python
import importlib.util
import json
import os
from pathlib import Path

repo = Path.cwd()
personal = Path(os.environ["AIRMOSAIC_CONFIG_DIR"]) / "ml-regression"
personal.mkdir(parents=True, exist_ok=True)
helper = repo / "skills/model/shared/machine_learning_model/scripts/common/review_plan.py"
spec = importlib.util.spec_from_file_location("plan_gate", helper)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
plan = gate.read_json(personal / "plan.json")
review_path = personal / "review.json"
delegation_path = personal / "delegation.json"
review = gate.read_json(review_path) if review_path.exists() else None
delegation = gate.read_json(delegation_path) if delegation_path.exists() else None
input_csv = Path(os.environ["AIRMOSAIC_ASSETS_DIR"]) / "data/03_atmospheric_transport/ExampleDataset/v1/prepared.csv"
gate.require(plan, repo, review=review, delegation=delegation, input_csv=input_csv)
task = plan["task"]
task_path = personal / "task.json"
params_path = personal / "parameters.json"
parameters = {"input_csv": str(input_csv), "task_config": str(task_path)}
for path, value in ((task_path, task), (params_path, parameters)):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
```

In `task.json`, adapt these fields together:

| Decision | Fields |
|---|---|
| Response and timing | `target`, `target_unit`, `target_definition` |
| Schema and variable roles | `features`, `excluded_features`, `categorical_features`, `id_column` |
| Existing split labels | `split.column`, `split.train`, `split.val`, `split.test` |
| Cleaning and screening | `missing.policy`, `missing.sentinels`, `feature_selection` |
| Model comparison | `models`, `selection_metric` |
| Sample and explanation budgets | `row_limits`, `seed`/`seeds`, `explanation` |

### Choose split sizes and sample caps

First design train/validation/test membership using usable sample size, independent entities and the intended time/space evaluation. No fixed counts or proportions apply to every study. Create and check these labels upstream.

Then set `row_limits.train`, `row_limits.val` and `row_limits.test` as computation caps. After cleaning, the current implementation selects `min(usable_split_rows, configured_cap)` rows per split. A cap does not redistribute rows between sets. To retain all usable rows, choose caps at least as large as the planned counts within the [supported bounds](#8-supported-settings). If the study exceeds those bounds, use a reviewed scaling adaptation or an explicitly justified sampling plan. Copying the small example can otherwise downsample a larger study.

Record source, usable and selected counts and any sampling rationale. The registered entry consumes holdout labels; automatic split generation and general cross-validation remain separate adaptations.

### Review the input evidence

Use the [method's product-lineage and causal design rules](../../../../../methods/shared/machine_learning_model/README.md). Before writing the final task, retain:

| Evidence | Check |
|---|---|
| Target and labels | Intended unobserved spatial/time domain, physical target, observed or proxy training labels and evaluation reference |
| Predictor definitions | Physical quantity or proxy, units, layer, spatial support and averaging/lag window |
| Product lineage | Variable/product/version, upstream assimilation/fusion/calibration or synthetic generation, outcome use, overlap with evaluation stations/periods, evidence source or unresolved status |
| Availability | Valid time, issue/release time and availability at the intended prediction origin |
| Causal design, when requested | Physical meaning of treatment/adjustment, mechanism evidence, alternative DAGs, identification assumptions and planned sensitivity checks |

Keep these decisions in the data dictionary and task's generation/design basis; use the existing `requirements` text for a concise reference. Do not invent task-schema fields. Schema validation does not verify the evidence. Unknown dependence must remain explicit; do not describe the resulting scores as independent validation without supporting evidence. Do not set `causal.assumptions` to true merely to pass validation.

The prediction entry needs labelled rows for fitting/evaluation. A separate unlabelled regional prediction table and field export require a reviewed inference/export adaptation.

Numeric strings must parse to finite numbers. Empty cells and configured sentinels become missing; the target is never imputed. `drop` keeps complete cases; `train_median_mode` fits predictor fills on training data. Unknown categories fail unless `unseen_categories=train_mode` is explicit.

Keep private paths in the personal files. Input paths may use `${AIRMOSAIC_ASSETS_DIR}`; configuration paths in the example are resolved to absolute paths. Arbitrary environment placeholders are not supported.

Run a study using the personal parameter file:

```powershell
$amParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "ml-regression/parameters.json"
python -m runtime.cli run-tool ml_regression_workflow --params-file $amParams --project-id air_quality_study --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file $amParams --project-id air_quality_study --timeout 180
```

The project slug selects external `assets/results/air_quality_study/<run_id>/`. Add `out_dir` to the parameter JSON only when choosing another fresh directory within that project root.

## 4. Call from Python or MCP

This executable Python example previews the same synthetic task as the CLI:

```python
import json
from pathlib import Path
from runtime.services import ToolRunnerService

parameters = json.loads(Path("config/examples/run-tool/synthetic-regression.json").read_text(encoding="utf-8"))
record = ToolRunnerService().run(
    "ml_regression_workflow",
    parameters,
    dry_run=True,
    timeout=180,
)
print(json.dumps(record, ensure_ascii=False))
```

After a successful preflight and dependency check, set `dry_run=False` to compute. For personal task files, replace the `parameters` argument with `params_file=str(params_path)` and add `project_id="air_quality_study"`; do not supply both parameter sources.

MCP sends the same runner parameters. Its server must allow `--execute-tool ml_regression_workflow`; client setup is in the [MCP guide](../../../../../harness/usage/mcp.md).

## 5. Read and verify results

For the generic prediction call above, read results after actual success:

```python
if record["status"] == "succeeded":
    output = Path("skills/model/shared/machine_learning_model/results") / record["run_id"]
    files = json.loads((output / "artifacts.json").read_text(encoding="utf-8"))["files"]
    metrics = json.loads((output / files["metrics"]).read_text(encoding="utf-8"))
    print(json.dumps(metrics["test"], ensure_ascii=False))
```

For project calls, use the selected project result root instead. The index resolves configurable filenames; `artifacts.json` itself is fixed. Prediction roles include `model`, `predictions`, `metrics`, `candidates`, `preprocessing`, and requested explanations. PLR roles include `causal_effect`, `causal_residuals`, `causal_folds`, `causal_models` and `dag`. All roles are listed in the [output contract](../contracts/output-files.json).

Check retained sample counts and selected features, independently recompute metrics from held-out predictions, and confirm model reload. Failure can leave partial files without an index: inspect the runner receipt/status, then use a fresh run rather than overwriting artifacts.

## 6. Causal and reproduction options

For `analysis=causal_plr`, start from the complete [synthetic causal task](../../../../../config/examples/ml-regression/synthetic-causal.json). Set one numeric treatment, its unit and `treatment_scale`, outcome/unit, DAG and manual adjustment set; `features` must equal `adjustment_set`. Use `missing.policy=drop` and exactly one nuisance candidate. Supply the six assumption declarations only after justifying the scientific design.

The retained train+validation pool is cross-fitted; the test split is excluded from effect estimation. Use 2–10 folds and at least `max(30,10*folds)` rows. Group mode needs at least `max(5,folds)` groups and asserts independent groups. A coefficient reports outcome units per `treatment_scale` original treatment units. See [domain mapping](air-pollution.md) for the design decisions.

The separate `scripts/r/models/reproduction.R` library accepts development data and fixed folds for bounded forest search. It is not an automatic-CV option of the registered entry.

## 7. Script interfaces

`scripts/r/run_regression.R` receives `--input-csv`, `--task-config`, `--out-dir` through the runner. Its modules share a `context` environment; they are not separate CLI tools.

| Module | Operation and handoff |
|---|---|
| `scripts/r/common/target.R` | Record target, variable roles and split contract |
| `scripts/r/common/prepare.R` → `scripts/r/common/select.R` → preparation | Read once, screen training-labelled rows, form cohorts and fit training-only preprocessing |
| `scripts/r/models/fit.R` | Fit baseline/candidates; select using validation loss; save model bundle |
| `scripts/r/common/evaluate.R` | Score frozen validation/test predictions; verify model reload |
| `scripts/r/contribution/explain.R` | Permutation on validation; PDP/ICE on training background; optional empirical-background Shapley estimates |
| `scripts/r/causal/causal.R` | Alternative to fit/evaluate/explain: cross-fitted PLR and inference |
| `scripts/r/common/io.R` | Role-resolved output, status and metric definitions |
| `scripts/r/models/reproduction.R` | `reproduction_forest()`, `reproduction_search_forest()`; source `scripts/r/common/io.R` first for `metrics()` |

The R adapter's Python configuration/output validation lives in `runtime/services/mlr3_workflow.py`; dependency/path/receipt handling stays in the common runner. Direct R module calls do not inherit these protections.

## 8. Supported settings

The [task schema](../../../../../catalog/schemas/ml-regression-task.schema.json) is authoritative. The adapter supports:

| Setting | Bounds and behavior |
|---|---|
| Input | At most 100,000 rows and 64 candidate predictors |
| Prediction cohorts | At least 10 usable training and 5 usable validation/test rows; caps: 20,000/5,000/5,000 |
| Candidates | 1–4 declared candidates, plus mean baseline; select by validation RMSE or MAE |
| `regr.rpart` | `cp`: 0–1; `maxdepth`: 1–30; `minsplit`: 2–10,000; `minbucket`: 1–5,000 |
| `regr.ranger` | `num.trees`: 1–1,000; `mtry`: 1–64 and within retained feature count; `min.node.size`: 1–10,000; `max.depth`: 1–30; `sample.fraction`: 0.1–1; `replace`: boolean |
| Explanations | At most 5 requested features; background/validation samples 5–200; repeats 1–10; grid points 2–20; categorical grid at most 32 levels |
| Shapley estimates | 1–20 rows, 2–32 permutations; configured rows × permutations × candidate-feature count × background rows ≤ 2,000,000 |

Ranger uses one thread and 100 trees if omitted; rpart internal CV is disabled. Other omitted learner parameters follow installed versions. The adapter does not automatically tune, create CV splits, or refit the winner on train+validation.

`train_filter` defaults to missing fraction 0.5, distinct count 2 and absolute correlation 0.95. Screening uses all source training-labelled rows before target filtering/subsampling; imputation uses the selected training cohort. Correlated candidates are removed in declared order. VIF is diagnostic. `row_limits` can subsample: inspect source, usable and selected counts.

PDP/ICE use training 5th–95th percentile grids or category levels. `explanation.features` selects permutation/PDP/ICE variables; optional Shapley covers all retained predictors. These are predictive explanations; causal design is a separate branch.
