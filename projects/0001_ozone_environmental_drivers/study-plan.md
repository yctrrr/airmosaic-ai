# Study plan — ozone predictive associations

**English** | [中文](study-plan_ZH.md)

## Questions and hypotheses

1. Can the chosen feature set improve held-out predictive performance relative to a mean-response baseline?
2. How do explicitly defined environmental and human-activity proxy feature groups alter that performance on the same stations?
3. Which predictive associations remain stable under reasonable development choices, and which depend on correlated predictors or validation design?

These are predictive questions. Land cover, column pollutants and activity proxies can share information; group differences do not partition causal contributions.

## Fixed input and development design

Use the input version in [project.json](project.json), with the published target unit, station key and train/validation/test labels. Consult the source dictionary before selecting predictors. Exclude the response, other ozone outcome columns, identifiers and split labels from predictors. Preserve source bytes and retain sample keys through every preparation step.

Define the study cohort and exclusions before comparing models. Keep station membership, input version and evaluation conventions aligned across arms; verify their exported keys explicitly. Fit missing-value replacements and category levels on training data only. Record any explicit unseen-category policy and its replacement counts. Missing responses are not imputed.

Use training data for fitting and validation data for model selection. Fix configurations before final test evaluation. If exploratory test results drive revisions, label that use and establish an appropriate new validation design rather than reporting the same test as untouched.

### Protocol for the published-paper experiment

The [paper prediction experiment](prediction.md) freezes its own [prompt](prediction_prompt.md) and [protocol](prediction.json). It uses the article's country/region restriction, three climate classes and nine- versus three-predictor forests. This study merges the released train and val labels for development, preserves test, selects within shared development ten-fold CV, then refits on all development stations. This differs from the generic adapter's validation-set selection; the project script is not a registered tool or general orchestration engine.

Published methods are separated from the additional search ranges, seeds and forest settings. Both model choices are frozen before test assessment. Development OOF scores participate in tuning; final performance uses the held-out test. Original case code and saved results are not used in this attempt; comparison awaits the user's complete implementation and final results. Prior source audits exist, so no blinded-experiment claim is made.

## Experiments

**E01 — Baseline comparison.** Use the existing regression workflow and allowed candidates. Record the candidate set, parameter budget, seed, cohort, selection metric and baseline before execution. Report RMSE, MAE and the defined out-of-sample R², including failures and sample counts.

**E02 — Feature groups.** Define groups from scientific roles and source documentation rather than assigning causal meaning from a column name. Compare groups using the same stations and split, preserving one complete record of included features per run. The current workflow accepts feature lists; group design and cross-run comparison remain manual.

**E03 — Robustness and interpretation.** Predefine development repetitions and explanation comparisons; retain the final test boundary. Start with available permutation importance and training-background partial dependence. Correlated features and unsupported feature combinations limit interpretation. ICE and optional empirical-background permutation Shapley are available through the skill. Alternative spatial splits, predictive resampling and automated experiment aggregation require separately reviewed adaptation; they are not enabled by this plan.

## Acceptance and handoff

Check unique keys and split separation, input/configuration versions, baseline comparability, prediction completeness, metric definitions, model reload and explanation provenance. Agree on scientifically justified effect sizes, uncertainty summaries and applicability before final interpretation; no universal numeric acceptance threshold is imposed here.

Write numerical outputs, plots, model objects and experiment/run mappings only into fresh private result directories. Human review determines which claims and selected files may be reused. This project does not rerun the historical private script or infer future, hourly or causal conclusions from a station-level historical benchmark.
