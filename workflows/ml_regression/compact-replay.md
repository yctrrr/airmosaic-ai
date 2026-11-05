# Compact spatial-regression replay

**English** | [中文](compact-replay_ZH.md)

This combination connects [hourly station preparation](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/hourly-preparation.md), [daily grids and bilinear sampling](../../skills/model/shared/spatial_analysis/references/python-path.md), and [grouped tuning](../../skills/model/shared/machine_learning_model/references/automatic-tuning.md). Numerical operations stay in those skills. The two [example programs](examples/compact_spatial_regression.py) generate synthetic inputs and check their handoffs; they are direct programs, with no new tool ID, runner adapter or MCP permission.

## Keep the example small

Choose a few stations with reviewed historical locations and a compact area before requesting gridded products. Retain the full study calendar when seasonality matters. The synthetic example uses eight stations and all 366 days of 2024 to exercise leap-day and year-boundary alignment; these counts are not model defaults or evidence of national representativeness.

| Retain once | Purpose |
|---|---|
| Selected station hourly labels and cells | Recompute observed-hour counts and daily targets |
| Required native grid nodes, timestamps, axes, units and missing masks | Recompute complete-sampling daily means and bilinear features |
| Station/source metadata, weights, daily table, group/fold assignments | Verify identity and each handoff |
| Reviewed plan, actual program, skill hashes, environment, search settings and seed | Refit without recreating a design from memory |
| Search summaries, frozen test/grid predictions and metrics | Check selection and evaluation independently |

All learners share one prepared table. Avoid saving identical inputs per learner or fitted models per fold. Keep the source precision: the fixture explicitly generates float32 fields; this does not authorize reducing real-product precision. A checksum records identity and cannot restore omitted data. Required nodes retain a lossless subset of the fixture, not a replacement for an upstream archive. Quotsoft's daily source is nationwide; selecting columns reduces local retention and replay size, not necessarily the initial transfer.

Count verification refits in the approved budget as well as search and final fitting. If no refit budget remains, rebuild inputs and metrics and check predictions with the already frozen estimator; do not repeat the search implicitly.

## Run without downloads

Use a task environment containing NumPy, pandas, SciPy and scikit-learn 1.4+; do not install packages into a shared environment implicitly. The example records exact versions, and the checker requires those versions and unchanged skill hashes. Run from the repository root with a fresh external result location:

```powershell
$compactRoot = Join-Path $env:TEMP "airmosaic-compact-check"
$compactStamp = Get-Date -Format "yyyyMMddHHmm"
$compactRun = Join-Path $compactRoot ($compactStamp + "_spatial_regression")
$compactReplay = Join-Path $compactRoot ($compactStamp + "_frozen_replay")
python workflows/ml_regression/examples/compact_spatial_regression.py --repo . --out "$compactRun"
python workflows/ml_regression/examples/check_compact_spatial_replay.py --repo . --source "$compactRun" --out "$compactReplay"
```

Existing outputs or outputs below any Git ancestor are rejected. `gen_script/` retains the actual program and design basis; `events.jsonl` records observed execution; paired retrospective files summarize the outcome. Inputs are explicitly synthetic. The fixed model list and small search ranges exercise software; a real study needs its own reviewed plan. The program reports every predeclared family's test metrics and does not select a family using those test scores.

The checker does not regenerate the fixture. It verifies file/skill hashes and versions, rebuilds daily features from saved stencils, repeats hourly completeness checks, checks saved groups/folds, refits the models and compares parameters and test/grid predictions. It independently recomputes RMSE, MAE and R². A second layer of unit checks covers invalid CRS, extrapolation, missing support, duplicate hours and fold leakage; a successful small fit alone does not cover these cases.

## Scaling without enlarging the example

Keep the retained hourly small example for preparation replay. A reviewed daily study may use [ERA5 local-day delivery](../../skills/data_acquisition/01_socioeconomic_natural_change/era5/references/daily-statistics.md) after a frozen hourly comparison, while retaining explicit three-hourly local-day EAC4 aggregation. Use shared monthly caches and one prepared table for all learners. Do not describe provider daily packages as independently checked hourly archives.

For purged spatial folds and real numeric-table neural comparisons, the [fixed-fold APIs](../../skills/model/shared/machine_learning_model/references/fixed-fold-tabular.md) keep numerical operations in skills. Projects own the exact frozen station roles, acquisition route, candidates, budgets and results. Retain common test keys and individual seed predictions; reload final models for a zero-fit evaluation replay. This does not enlarge or replace the synthetic example.

## Transfer to a real study

Ask the agent to propose target, source versions, historical station/CRS evidence, time semantics, features and lineage, preprocessing, spatial validation, search ranges, budget and destinations before generating a real experiment. Human review remains the default unless the user delegates the decision. Product assimilation/fusion must be assessed separately from programmatic split checks.

Unmonitored-location evaluation needs spatial separation appropriate to the inference domain. Holding out station IDs is insufficient when nearby stations share a coarse grid cell or spatial structure; choose blocks/buffers from reviewed geography and report the effective number of independent groups. A tiny example validates mechanics and cannot establish China-wide accuracy. Do not relabel unknown coordinates/time mappings as verified. Engineering use of provisional interpretations requires explicit review and retained source status, rather than scientific acceptance.

Project results remain with their project. A human scientific decision determines whether selected products enter `assets/`; this recipe does not define its internal organization or promote data automatically.
