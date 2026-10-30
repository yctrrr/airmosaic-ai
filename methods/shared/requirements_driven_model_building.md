# Turning a research request into a model design

**English** | [中文](requirements_driven_model_building_ZH.md)

A request such as “build a model from these data” leaves several scientific choices open. Resolve the choices that change the meaning of the result before selecting software.

## Describe the question

Write the outcome or objective, the observational unit, population, period and unit of measurement. Explain whether the result will support prediction, comparison, explanation, causal estimation or reproduction.

| Choice | Questions to answer |
|---|---|
| Data | Which fixed source and version represent the intended population? |
| Variables | Which predictors are available at use time, and which have causal or identification roles? |
| Constraints | What assumptions, baselines and scientific requirements must the model satisfy? |
| Evaluation | Which new entities, regions or periods should be represented by holdout data? |
| Decision | What evidence would make the result useful, limited or inconclusive? |

Use the available dictionary to resolve terminology. A target name alone does not establish its aggregation, physical unit or measurement support.

## Choose build or reproduce

For a new model, choose a supported method appropriate to the question and state why it is suitable. For reproduction, fix a particular reference procedure, data contract and numerical comparison criterion. Existing code provides a reference experiment; its settings are not universal defaults.

For example, a paper's station-based regression and tuning design cannot be replaced by a convenient generic split while retaining the same reproduction claim. The [reproduction method](model_reproduction.md) explains how to compare such designs.

## Plan a defensible evaluation

Select a baseline, development budget and final holdout. Repeated entities, spatial dependence, time order and overlapping lags affect separation. Fit learned transformations within training data and inside every relevant training fold.

Choose metrics that match the outcome and intended use. Preserve comparable sample populations across candidate models and report exclusions. Freeze the final choices before the agreed test.

## Decide how to interpret the result

Model explanation asks how fitted predictions depend on inputs. Causal estimation asks about a defined treatment contrast under identification assumptions. Decide which question is intended before choosing controls or explanation tools; [regression design](machine_learning_model/README.md) gives the details.

## Hand off a concrete task

The handoff includes a fixed input/dictionary reference, target definition, variable roles, split rationale, candidate requirements, computation budget, output destination and review criteria. Identify missing preparation or unsupported methods explicitly.

The selected [skill](../../skills/model/shared/README.md) translates those choices into parameters and code. A [workflow](../../workflows/ml_regression/README.md) combines reviewed operations. A specific study records its experiments and judgments in [projects](../../projects/README.md).
