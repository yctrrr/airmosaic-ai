# Configure an air-pollution task

**English** | [中文](air-pollution_ZH.md)

Choose the scientific design using the [human-readable examples](../../../../../methods/shared/air_pollution_regression.md), then map it to the settings below. Environment setup, configuration-writing code and calls are maintained once in [operations](operations.md).

## Concentration prediction

Start from the complete [PM2.5 task template](../../../../../config/examples/ml-regression/air-pollution-prediction.template.json). It expects a prepared station-day table with the following illustrative columns:

| Role | Template field | Adaptation |
|---|---|---|
| Outcome | `pm25` | Actual pollutant statistic, unit and averaging period |
| Key | `sample_id` | Unique station-period key |
| Split | `dataset` | Existing `train`, `val`, `test` labels from the study design |
| Numeric predictors | `temperature`, `relative_humidity`, `wind_speed`, `boundary_layer_height` | Time/space-aligned columns available for the intended use |
| Categorical predictor | `season` | Actual category column, declared in `categorical_features` |

Adapt field names and types, missing markers, coverage rules and split design to the selected data. Perform joins, unit conversions, aggregation and derived-variable construction upstream. The template describes retrospective analysis; forecasting needs an appropriate information-availability definition.

Define the unmonitored spatial/time prediction domain separately from this labelled station table. Complete the [input-evidence checks](operations.md#review-the-input-evidence), including ground-observation use in reanalysis/fused/synthetic predictors and overlap with evaluation stations/periods. Record unknown lineage and the chosen independent-reference or sensitivity strategy. Regional inference and field export are not implemented by this template.

The two initial candidates are a depth-5 tree and a 100-tree forest with `mtry=2`, node size 5. Treat these as a small starting comparison. Set `selection_metric` to RMSE or MAE and compare additional supported candidates within the four-candidate limit. Check that `mtry` fits the retained predictor count.

Choose split sizes from the study's usable data and independent site/time coverage. The template uses the adapter's supported maximum row caps to avoid inheriting small demonstration sizes; these are ceilings, not requested sample counts or ratios. Review them against the actual cohort and budget before execution. Larger studies need the scaling/sampling decision described in operations.

Review the training median/mode policy and explanation budget, adapt the caps to the intended cohort, and inspect actual selected counts. For screening, choose `manual` or `train_filter` and fix the candidate order. For interpretation choose `permutation`, `pdp`, `ice` and optionally `shap`; use the method's scientific interpretation rules.

The template has no associated dataset. For a runnable code check use the [synthetic parameters](../../../../../config/examples/run-tool/synthetic-regression.json); their outcome, predictors and units are synthetic.

## A continuous driver's effect

Use the complete [synthetic PLR task](../../../../../config/examples/ml-regression/synthetic-causal.json) to inspect the interface. A study needs its own justified graph and adjustment set before replacing these fields:

| Decision | Configuration |
|---|---|
| Analysis and outcome | `analysis=causal_plr`, actual `target` and `target_unit` |
| Treatment contrast | `causal.treatment`, `treatment_unit`, `treatment_scale` |
| Adjustment | `features=causal.adjustment_set`, `feature_selection.mode=manual`; exclude treatment from predictors |
| Missingness and learner | `missing.policy=drop`; exactly one nuisance candidate |
| Fold design | `causal.folds`, `resampling.mode`, and `group_column` for group mode |
| Identification | `causal.dag` and the six justified `causal.assumptions` |

The branch cross-fits retained training+validation samples. The coefficient uses outcome units per `treatment_scale` original treatment units. Check graph validity, out-of-fold separation, residual treatment variation and uncertainty in the causal artifacts. Group folds preserve declared groups; independence between groups still belongs to the study design.

Before declaring the assumptions, document the physical quantity or proxy represented by each variable, evidence for causal directions, confounders/mediators, product-generation dependencies and plausible alternative explanations. Plan sensitivity checks for unresolved assumptions. Passing DAG checks or obtaining a precise coefficient does not establish causal reliability.

The existing [synthetic causal runner parameters](../../../../../config/examples/run-tool/synthetic-causal.json) can exercise this branch with the same CLI sequence as prediction. A predictive-importance output is not a substitute for this configuration.

## Downstream impacts and adaptations

Map a supported numeric impact-prediction task using the same target/feature/split fields. Exposure assignment, lags, outcome denominators and causal identification are established before fitting. For weather normalization, nonlinear exposure-response, dedicated count/binary/survival models, distributed lags or burden calculations, identify the missing operation and implement it in the appropriate skill before composing the workflow.

## Prompt

```text
Use the AirMosaic regression skill.
Question: <prediction or a justified continuous-treatment effect>.
Input: <prepared fixed dataset and dictionary>.
Design: <unobserved prediction domain, labelled reference, target/unit/period, study-specific split>.
Evidence: <physical variable meanings, product lineage, reused observations and issue/release times>.
Causal question, if any: <contrast, justified DAG/adjustment, uncertainty and sensitivity checks>.
Budget: <models, sample caps, seeds and explanation sample sizes>.
Output: <fresh project result destination>.

Read the relevant method, then create personal task/runner JSON using the operations example.
Map each requested operation to a supported setting; identify required adaptations.
Check dependencies and dry-run, execute within the authorized scope, then read artifacts.json.
Check actual cohorts, held-out performance or causal diagnostics and summarize the interpretation.
Reuse skill code for calculations; workflow code supplies settings and orchestration.
```
