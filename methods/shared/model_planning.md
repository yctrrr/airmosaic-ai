# Prepare a model plan before generating experiment code

**English** | [中文](model_planning_ZH.md)

A model plan lets a person judge the scientific choices before an agent turns them into an experiment. It records explicit reasons and evidence, rather than hidden reasoning. Begin with the question and authorized data, not a previous task configuration.

## What the plan must explain

| Decision | Required basis | Human judgment |
|---|---|---|
| Target | Physical quantity, units, spatial/time support, unobserved prediction domain, observed/proxy labels and intended use | Does the reference represent the question? Is prediction, fitted-model explanation or causal estimation intended? |
| Variables | A role and physical/proxy meaning for each included variable; inclusion/exclusion reasons, units, measurement support, availability and product lineage | Are important processes missing? Could assimilated/fused observations, target-derived columns or future information reveal the answer? |
| Parameters | Candidate models, bounded ranges, actual evaluated points, fixed settings, defaults/version assumptions and computational budget | Which choices follow mechanisms, literature or training diagnostics, and which are engineering starting points? |
| Splits | Independent unit, time/space/group boundaries, source and usable counts, final-test protection and any sampling rationale | Does the holdout represent the intended application? There is no universal count or ratio. |
| Preprocessing | Units, missing markers, exclusions, imputation, encoding, transformations, unknown categories and training/fold fitting boundaries | Do replacements preserve physical meaning? Are extreme values investigated rather than silently altered? |
| Evaluation | Baseline, selection loss, frozen final comparison, subgroup/residual checks and acceptance criteria | Does the loss express the application need? Is the final test kept outside design and tuning? |
| Interpretation | Exact fitted model, reference population, explanation budget, uncertainty and causal identification if requested | Does the evidence support the proposed interpretation? Predictive importance alone does not identify an effect. |

For parameter ranges, distinguish evidence for a parameter's meaning from evidence that a value works well here. An official manual does not make a chosen tree count optimal. Record alternatives and uncertainty. A previous successful experiment is a reference; reuse its settings only when the current question justifies them.

Use the [regression selection guidance](machine_learning_model/README.md) for literature and data-dependent parameter comparisons, and the [air-pollution examples](air_pollution_regression.md) for spatial-proxy selection. For every proposed value or variable, distinguish a published finding, this study's inference and evidence still to collect. Attach a specific source and a data-specific reason; one shared citation or repeated generic sentence does not justify every variable. State which comparisons are actually supported and which require adaptation.

Read-only planning may inspect the authorized dictionary, keys, split sizes and development predictors. Do not use final-test outcomes to design features or candidate settings. State whether diagnostics describe all development rows or the actual retained training cohort.

## Review nodes

1. **Before experiment-code generation:** present the plan, alternatives and unresolved items. Default to waiting for human review. Save the exact approved plan identity and the actions it permits.
2. **Before execution:** check the generated/reused caller, task binding, data identity, syntax, scope, synthetic tests, dependencies and dry-run. This technical review need not ask again when the existing approval already covers execution. Changes require a new check.
3. **After results:** assess scientific validity, limitations and reuse separately from successful computation. Final-test-driven changes are a new experiment, not another tuning step on the same test.

Blocking unknowns prevent the affected operation. An acknowledged limitation may permit a bounded technical experiment when its claims are restricted; record that judgment rather than marking an unsupported assumption as true.

## Human review and delegated judgment

Human review is the default. If the user explicitly delegates judgment, the agent may review and proceed within that stated scope. Retain the user's non-secret authorization reference, plan identity, permitted actions, review time, agent judgment and limitations. A plan field, command-line auto flag or agent's own statement cannot supply user authorization.

The person reads the plan and responds with approval, requested changes, rejection or delegation. The host agent records that actual response; the person need not edit JSON. Record which actions the response covers. Approval to generate alone does not permit execution.

Authorization to compute does not grant scientific acceptance, publication, credential access or data promotion. A changed question, variable set, parameter range, split, preprocessing policy or input version changes the plan identity and invalidates its old review. Changed generated code needs a fresh technical check.

## Handoff

Human explanation belongs here. The [regression method](machine_learning_model/README.md) supplies scientific detail; the [skill planning reference](../../skills/model/shared/machine_learning_model/references/planning.md) defines machine records and guards. The [workflow](../../workflows/ml_regression/planning.md) shows the ordered handoff. Plans remain in task configuration/planning storage; generated code and outcomes use the selected result scope.
