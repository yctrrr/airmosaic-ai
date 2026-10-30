# DAG and continuous-treatment PLR

**English** | [中文](causal_ZH.md)

Use [causal design methods](../../../../../methods/shared/machine_learning_model/causal.md) before implementation: define treatment, outcome, temporal order, physical mechanisms, confounding, alternative DAGs, overlap and sensitivity checks. Graph validity does not prove identification.

The R [`causal/causal.R`](../scripts/r/causal/causal.R) branch is selected by `analysis=causal_plr`. It replaces the prediction fit/evaluate/explain branch while sharing target and preparation modules. It requires a declared DAG, manually justified adjustment set equal to `features`, one numeric treatment, units, treatment scale, exactly one nuisance candidate, `missing.policy=drop` and six justified assumption declarations. Do not check assumptions merely to pass validation.

The retained train+validation pool is cross-fitted; test rows remain excluded. Use 2–10 folds and at least `max(30,10*folds)` rows; group mode requires `max(5,folds)` groups and an independent-group assertion. These implementation guards do not establish adequate effective sample size or causal validity. [R operations](operations.md#6-causal-and-reproduction-options) retains the complete invocation/configuration, coefficient-unit definition and output roles. Read causal effect, residuals, folds, nuisance models and DAG through `artifacts.json`, and report identification limits. Python predictive candidates do not provide this R PLR branch.
