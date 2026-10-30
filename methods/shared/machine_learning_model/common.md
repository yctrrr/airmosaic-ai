# Questions, variables, sampling and evaluation

**English** | [中文](common_ZH.md)

## Before generating experiment code

Prepare a [model plan](../model_planning.md) explaining target, each variable, parameter ranges, splits, preprocessing, evaluation and interpretation. Present its reasons, evidence, alternatives and uncertainty for human judgment. Wait by default; proceed under agent judgment only when the user explicitly delegates it. Save the reviewed plan before experiment-code generation and recheck code/task/data before execution.
## 1. Decide what you want to learn

Start with a sentence such as “estimate daily concentration in unmonitored areas” or “estimate how a specified driver changes concentration.” These lead to different designs:

| Goal | Main result | Decisions to settle first |
|---|---|---|
| Prediction | Predictions and errors on new samples | Who/where/when the model will predict, and which variables will be available |
| Explain a fitted model | Variables and patterns used by that model | Which population and reference conditions the explanation represents |
| Estimate a causal effect | A defined change in outcome under a specified treatment contrast | Treatment, outcome, temporal order, common causes and identification assumptions |

For regional environmental prediction, the target is commonly a spatiotemporal variable at places or times not covered by monitoring, or a field that cannot be observed directly. Define its spatial support, averaging period, units and intended use. Available observations provide training labels and held-out references; they are distinct from the unobserved prediction domain. A regional daily field and tomorrow's hourly concentration need different information and validation.

If the target itself cannot be observed, state whether labels are proxies, simulations or derived estimates. Agreement with those labels evaluates agreement with the reference, not necessarily accuracy against the underlying physical quantity.
## 2. Prepare a table whose rows have clear meaning

Each row needs a unique sample identifier, a measured or derived outcome, candidate variables and enough location/time information to define the evaluation design. Record data sources, unit conversions, aggregation rules and missingness.

Check whether records were joined to the correct site and period. Distinguish missing observations from measured zeroes. Investigate implausible values using source-specific quality rules. Retain a record of exclusions so another researcher can understand which population remains.

Choose a missing-value strategy that fits the question. Filling predictors from the training data can support prediction; the target should not be manufactured to increase sample size. Any transformation estimated from data must be learned without using held-out observations.
## 3. Choose variables before selecting a model

A useful variable has a scientific role, adequate measurement quality and appropriate timing. For prediction, ask whether it would exist when the prediction is made. For causal analysis, ask how it relates to the treatment and outcome.

Define the physical quantity, units, height or layer, spatial support and time window of each variable. Distinguish a measured or modelled quantity from a statistical proxy. Correlation or predictive usefulness alone does not establish a causal role.

| Role | Example of the decision it changes |
|---|---|
| Predictor | Can it improve a prediction using information available at deployment? |
| Common cause | Must it be considered to address confounding of treatment and outcome? |
| Mediator | Is the question about the total effect or a path that excludes this intermediate process? |
| Collider | Could selecting or adjusting on it introduce an association? |
| Identifier or target-derived field | Does it reveal the answer or encode the split rather than provide usable information? |

Missingness, variation, correlations and VIF help diagnose the candidate set. Use these diagnostics within training data. When predictors are redundant, scientific relevance and measurement quality help decide which to keep. Low predictive importance is not a reason to remove a necessary confounder.

Spatially structured predictors also need a transferability check: low pairwise correlation or VIF does not show that a model can predict beyond sampled locations. The [air-pollution examples](../air_pollution_regression.md) explain the evidence and comparisons for coordinates and other geographic proxies.

### Check product lineage before splitting

Regional predictors often come from reanalysis, observation-fusion products or synthetic/simulated fields. Record each product's version, source observations, assimilation/fusion or calibration procedure, and any use of the outcome or evaluation stations and periods. Also check whether a synthetic-data generator or upstream model was fitted using evaluation labels. Reanalysis combines models and observations; the relevant inputs differ by product and variable. See the official [ERA5](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) and [EAC4](https://www.ecmwf.int/en/forecasts/datasets/cams-global-reanalysis-eac4) descriptions.

If an upstream predictor already used held-out outcome observations, splitting the downstream table does not restore independent validation. Where feasible, use observations excluded from the upstream product, construct station/time-excluded or out-of-fold products, or remove the dependent feature and compare sensitivity. If independence cannot be established, report that limitation rather than claiming an independent test.

Record valid time and actual issue/release time separately. Retrospective reconstruction may use later-released products under its stated design; a forecast must respect the information available at its prediction origin. Assimilating earlier observations into an available forecast initialization is not automatically leakage. Decide against the intended use and the actual product lineage.
## 4. Reserve an evaluation set that resembles intended use

Training data fit the model. Validation data choose variables, candidates and settings. The final test evaluates the frozen design.

Choose counts and proportions from the usable data size, number of independent units, time/space structure and precision needed for evaluation. There is no universal split ratio or fixed sample count. With limited independent samples, consider a suitable resampling design and verify its implementation support before using it. Computation caps are a separate decision and must not silently change the evaluation population.

For later periods at known sites, consider a forward temporal holdout. For new sites or regions, hold out the corresponding sites or areas. Account for repeated measurements and overlapping temporal windows. A random row split can leave closely related observations on both sides and answer an easier question than the intended application.

Fix the test population before model selection. If cross-validation is used, repeat learned preprocessing within each training fold. Keep comparisons on the same sample population wherever possible.

[Roberts et al. (2017)](https://doi.org/10.1111/ecog.02881) show why dependence-aware validation matters, but also why overly restrictive blocking can turn interpolation evaluation into extrapolation. Choose distances, groups and time gaps from the prediction task and development-data structure; a published block size is not a universal independence threshold.
## 8. Review the result against the original question

Use the [common evaluation reference](evaluation.md) for the training-mean comparison shared across model families. Keep this reference separate from the test-mean normalization in R².

A useful report lets a reader answer: Which data and samples were used? Which variables and models were compared? How did the frozen model perform on the intended holdout? What interpretation is supported? Which assumptions or uncertainties remain?

Keep this reasoning with the study. Configuration, script execution and artifact reading are in the [skill operations](../../../skills/model/shared/machine_learning_model/references/operations.md). For concentration drivers, weather normalization and downstream effects, continue with the [air-pollution examples](../air_pollution_regression.md). The methodological connection to the published review is documented in the [source mapping](../../../skills/model/shared/machine_learning_model/references/published-basis.md).
