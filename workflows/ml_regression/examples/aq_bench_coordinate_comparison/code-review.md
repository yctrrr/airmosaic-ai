# Inspect generated code against its scientific basis

**English** | [中文](code-review_ZH.md)

Read the [study plan](README.md) first. This page specifies what to inspect after approval; no `run.py`, model or execution events exist for this round. Reasons are reviewable decision summaries, not hidden reasoning records.

## What current code actually does

The [existing caller](../planned_regression.py) writes `plan["task"]` to `gen_script/task.json` and copies reviewed orchestration after approval. Execution calls `ml_regression_workflow` through the skill gate and runner. It does not scientifically select features/parameters from literature or generate new numerical algorithms. Preserve the truthful copy mode in `generation.json`.

The [preparation module](../../../../skills/model/shared/machine_learning_model/scripts/r/common/prepare.R) reads configured columns, missingness and existing labels; [variable selection](../../../../skills/model/shared/machine_learning_model/scripts/r/common/select.R) diagnoses/filters under the declared policy; [fitting](../../../../skills/model/shared/machine_learning_model/scripts/r/models/fit.R) trains declared candidates and selects by validation error. They do not read papers to establish scientific validity.

A value appearing in code therefore does not establish its justification. Connect the approved plan, actual configuration and effective execution values to check faithful implementation.

## Item-by-item mapping

| Decision | Configuration or data | Check after generation |
|---|---|---|
| V01–V08 | First eight `features` in A/B | Identical environmental set/order; no silent importance/correlation-driven changes |
| V09–V11 | Only B adds `lat`, `lon_sin`, `lon_cos` | A retains geographic metadata outside predictors; B's circular transformation is correct |
| P01–P04 | Prepared data, `id` and derived columns | Unchanged source hash; independently recomputable five-field sum/angular transform; identical paired keys |
| P05–P07 | `missing`, `feature_selection` and fold fitting | No clipped/imputed outcomes; fit-only medians; no default correlation filter |
| H01–H02 | `models[*].parameters` | Exact four `mtry`/node combinations; no extra search opportunities for B |
| H03–H05 | Tree count, sampling and omitted parameters | Explicit 500 trees, 0.632 without replacement; record unrestricted depth and variance splitting defaults as well as explicit fields |
| H06 | `seeds`, order and fit records | Identical effective seeds for paired settings; fold identity, base and derived seeds retained |
| H07 | Inner comparisons and outer scoring | No outer outcomes/scores in selection; recompute pooled metrics from station errors |
| H08 | `explanation` | Traceable common background sampling/budget; no geographic PDP that varies longitude sine/cosine independently |
| Spatial protocol | Fold manifests, distances and refits | Never split cells; buffer fitting side; refit all eligible training records after selection rather than retaining an inner model |

Retain `decision_id`, `source_id`, `study_reason`, `alternative`, `uncertainty`, `config_field`, `code_location`, `effective_value` and `check_evidence` per item. These are requirements for actual post-generation evidence, not records already captured here.

## Generation order and adaptations

`comparison-plan.json` is a multi-arm scientific draft, not a `model-plan.schema.json` single-task record. Do not pass it to the gate as an executable plan. The two task drafts only illustrate published-split fields and have no prepared input.

After approval, design reusable skill interfaces for deterministic preparation, paired cohorts, spatial grouping/buffers, development-only fitting and frozen outer refit/scoring. The current runner requires training/validation/test labels and automatically evaluates the selected model. Do not supply outer-test labels to inner calls and describe repeated scoring as isolation.

Subsequent workflow callers compose these skill interfaces and save task/decision mappings; numerical work stays in skills. Validate preparation, folds and interfaces with synthetic inputs, then bind real prepared-data hashes, exact tasks and actual reviews into each skill plan. Execute only after exact-code checks.

The resulting data flow must be inspectable:

`comparison-plan.json` → actual approved plan → bound prepared input and fold manifests → `gen_script/task.json` + `run.py` → skill preparation/fitting/evaluation → independent checks

This is a proposed flow, not a new executable command or completed run.

## Questions the result must answer

- Do paired coordinate contrasts vary by region/seed? Are comparisons of independently tuned pipelines labelled separately?
- Does improvement occur only on nearby benchmark splits and disappear or reverse under regional holdout?
- Did features, samples, effective seeds or defaults change without explanation?
- Are pre-generation reasons, observed actions and retrospective summaries distinct? Are unimplemented, skipped and failed operations explicit?

Without a regional feature grid, discuss station prediction and dependence diagnostics only; scores cannot establish absence of block-like map artefacts.
