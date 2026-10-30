# How to assess model reproduction

**English** | [中文](model_reproduction_ZH.md)

A reproduction comparison asks whether a stated calculation can be recovered and whether the observed differences matter. Start by defining the claim: exact reconstruction, agreement within a tolerance, replication on different data, or an intentionally corrected model.

## Establish a fair comparison

Preserve the reference and candidate results. Describe the outcome, unit, sample population and prediction origin of each side. A saved model can recover new predictions, but that evidence differs from an original prediction export.

Match samples using unique identifiers. Compare the two complete cohorts as well as their shared samples, and retain unmatched cases. Sorting two tables into the same order does not prove they represent the same observations.

## Review the process that produced the numbers

| Stage | Questions to compare |
|---|---|
| Preparation | Were units, missing values, exclusions and transformations handled consistently? |
| Sample design | Are sample keys, development/test boundaries and grouping identical? |
| Model fitting | Are features, algorithm, settings and learned preprocessing comparable? |
| Selection | Which folds, search budget, criterion and random states selected the model? |
| Evaluation | Are the same truths, metric formulas and prediction scales being scored? |
| Interpretation | Did explanations use the final model and the stated background? |

Use code, configuration and saved artifacts to trace these decisions. Record missing evidence instead of inferring a historical choice from a similar current result.

## Recompute before explaining a difference

Recalculate metrics on each own cohort and on aligned common samples. Inspect prediction differences as well as aggregate scores. Define absolute/relative tolerances and behavior near zero in advance. For stochastic procedures, use seed/environment evidence or a justified repeated-run criterion.

A nearly equal mean score can hide differing predictions or sample exclusions. Conversely, a small numerical difference may be compatible with the intended scientific use. Explain both the magnitude and the scope of agreement.

## Diagnose one cause at a time

When existing evidence cannot explain a difference, plan a bounded probe with a declared change and fixed factors. Keep the original baseline and probe outputs. Separate preparation, split, tuning and scoring changes where possible; repeatedly optimizing against the final test compromises its independence.

## State the conclusion at four levels

Report whether the technical procedure worked, which numerical results agree, which scientific claims are supported, and what human review remains. A reproduced result may still have a scientific limitation; a diagnosed defect can explain a mismatch without validating the original claim.

The [comparison skill](../../skills/model/shared/model_reproduction/SKILL.md) supplies manifests, keyed metric calculation and reports. The [workflow](../../workflows/model_reproduction/README.md) organizes the evidence and study handoffs.
