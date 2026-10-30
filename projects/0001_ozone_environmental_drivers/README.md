# 0001 — Environmental features and long-term ozone

**English** | [中文](README_ZH.md)

**Scientific question:** how well do environmental and human-activity proxy features predict station-level long-term mean ozone, and how stable are the resulting predictive associations across feature groups, model choices and validation designs?

The stable project ID is `ozone_environmental_drivers`. The directory number `0001` is for navigation; new results use the stable ID. Here, “drivers” names candidate explanatory features, not identified causal effects.

## Scope and references

| Item | Definition |
|---|---|
| Public input | AQ-Bench v1 station metrics and variable dictionary; fixed version referenced in [project.json](project.json) |
| Response | `o3_average_values`, in ppb; station-level aggregated ozone for 2010–2014 |
| Research stage | `03_atmospheric_transport` |
| General workflow | [ml_regression](../../workflows/ml_regression/README.md), version 1.0.0 |
| Registered tool | `ml_regression_workflow` |
| Operational skill | [Regression skill](../../skills/model/shared/machine_learning_model/SKILL.md) |
| Scientific/source reference | [Ozone reference case and public input](references/air_quality_o3_reference.md) |

The [study plan](study-plan.md) defines hypotheses, experiments and interpretation. [review.md](review.md) is a pending review template. The existing [small configuration](../../config/examples/ml-regression/aq-bench-prediction.json) demonstrates the computation path; it is not a pre-approved full study design.

## Experiments

| Experiment | Scientific purpose | Execution status |
|---|---|---|
| E01 — Baseline comparison | Compare allowed predictive models against the fixed mean baseline on a common cohort | First paper prediction run and independent metric checks complete; reference comparison complete; human scientific review pending |
| E02 — Feature-group comparison | Assess how environmental and human-activity proxy groups change predictive performance and interpretation | First nine- versus three-predictor comparison complete; reference comparison complete; human scientific review pending |
| E03 — Robustness and interpretation | Assess dependence on development seeds, validation design and correlated features | Planned; alternative spatial splits and additional explanation methods need adaptation |
| E04 — Original implementation comparison | Audit provenance, common cohorts, predictions and metrics | compare_existing complete; historical training provenance incomplete and human review pending |

## Current status and use

The first [paper prediction and evaluation experiment](prediction.md) is complete, using external assets and a frozen [prompt](prediction_prompt.md) and [protocol](prediction.json). It retains 4077 development and 1009 test stations. Both models underwent ten-fold selection, refitting on all development stations and final test assessment. Computation and independent checks are complete; original models/results have been compared read-only through the [model_reproduction workflow](experiments/reference_comparison/README.md). Historical training provenance retains gaps; robustness experiments and human scientific review remain pending.

Study-specific project scripts implement ten-fold orchestration using core launch mechanisms, the regression metric helper and mlr3 guidance. This mode is not implemented by generic `ml_regression_workflow`. See the study guide for its entry point and actual status; earlier generic smoke evidence retains its original scope.

For generic adapter tasks, read the study plan, prepare experiment-specific task settings in the private configuration root, then call the existing tool using `--project-id ozone_environmental_drivers --stage 03_atmospheric_transport`. Follow the separate launcher instructions for the paper experiment. Use a fresh run for each experiment configuration. The project manifest references the workflow; it does not execute it automatically. See [project operating rules](../README.md) and [workflow execution](../../workflows/ml_regression/README.md).

Study outputs stay within external `assets/results/ozone_environmental_drivers/`; choose experiment directories and relative artifact names while retaining the experiment/run mapping. General DAG and estimand design lives in methods and workflows. This project remains predictive; adding a causal skill branch does not automatically run observational causal experiments.

`references/` holds this question’s legacy source audit, public-input description and reproduction adaptations. These are project references, not completed experiment results or universal defaults; reusable scientific design remains in methods.

Inputs have matching [repository](../../assets/data/03_atmospheric_transport/AQ-Bench/v1/README.md) and external copies. `project.json` records both paths for explicit selection; project loading remains manual, and result locations are unchanged.
