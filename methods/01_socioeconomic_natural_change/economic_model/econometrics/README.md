# Econometrics: questions, identification and estimation

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

Econometrics connects an economic or environmental question to observed variation in data. A coefficient is an estimate under a particular statistical model. Its causal interpretation requires a defensible design and assumptions; fit, significance and a long control list do not supply identification. Begin with the unit and population, outcome, exposure or policy, time horizon and **estimand** (the quantity to learn). Decide whether the aim is description, prediction, a causal effect or structural parameters before selecting software.

## Modeling philosophy and architecture

1. **Question and estimand.** State the target population, intervention or contrast, outcome, time horizon, units and scale. Examples are a conditional association, a forecast, an average treatment effect (ATE), an effect among treated units (ATT), or a local effect near a cutoff (RDD) or for instrument compliers (IV). These answer different questions.
2. **Data-generating setting.** Define observation unit, sampling frame, panel IDs and dates; inspect missingness, measurement, selection, timing and possible spillovers. Draw a causal graph or write an explicit confounding argument when claiming an effect.
3. **Identification.** Explain which variation separates the target from confounding, feedback and common shocks. List the assumptions that link observable data to the estimand. [Lewbel's identification survey](https://www.aeaweb.org/articles?id=10.1257/jel.20181361) distinguishes causal, reduced-form and structural identification.
4. **Specification and estimation.** Write the equation, variables, transformations, fixed effects, weights and sample restrictions before fitting. Estimate only after checking data support and model rank. A structural model additionally specifies behavioral equations and equilibrium or dynamic restrictions, then estimates or calibrates parameters against data; those restrictions must be defended separately from reduced-form effects.
5. **Inference and interpretation.** Choose uncertainty estimation for the assignment and sampling process, e.g. clustering at the unit where shocks or treatment are shared. Report coefficient units, uncertainty, sample definition, identifying assumptions, diagnostics, sensitivity, heterogeneity and external-validity limits. Do not select a causal story by the smallest p-value or highest R².

## Common model families

| Family | Typical use and equation | Main identification or validity question |
|---|---|---|
| OLS / GLM | Baseline conditional association, `Y = α + Xβ + ε`; a link function handles binary or count outcomes. | Are regressors exogenous for the claimed effect, and is the outcome model appropriate? OLS alone is descriptive unless additional design assumptions hold. |
| Panel fixed effects | `Y_it = α_i + λ_t + βD_it + X_itγ + ε_it` removes time-invariant unit and common time components. | Are time-varying confounders, anticipation and treatment timing addressed? Fixed effects alone do not prove causality. |
| Difference-in-differences / event study | Compares outcome changes in treated and comparison groups. | Is the untreated counterfactual trend credible, with suitable comparison groups and no problematic anticipation? Pretrend plots are diagnostics, not proof. Staggered adoption with heterogeneous effects needs an estimator and target estimand chosen for that design, rather than an automatic two-way fixed-effects coefficient. |
| Instrumental variables / 2SLS | Uses a proposed instrument `Z` to isolate variation in endogenous `D`. | Relevance, exclusion and independence need a substantive defense; check weak-identification sensitivity. An IV coefficient may identify a local effect under additional assumptions. |
| Regression discontinuity | Compares observations near an assignment cutoff. | Is potential outcome behavior continuous at the cutoff, with no precise manipulation? Check bandwidth and specification sensitivity; the result is local. |
| Time-series / forecasting | Uses lags, dynamics and validation windows to predict or describe temporal dependence. | Are stationarity, structural breaks, leakage and out-of-sample performance checked? Predictive success alone does not identify policy effects. |
| Structural econometrics | Estimates behavior under stated utility, technology, market or dynamic restrictions. | Which parameters and counterfactuals are identified by data versus imposed functional forms or calibration? How do model fit and sensitivity behave? |

An environmental application might model observed emissions, household expenditure or exposure as an outcome. Align policy dates, industry and region identifiers, pollutant units and geography; state whether the outcome is measured, inventoried or model-simulated. When a derived IO, LCA or atmospheric output becomes a regressor or outcome, propagate its uncertainty and avoid presenting the combined estimate as directly observed. [IO](../io/README.md) and [CGE](../cge/README.md) provide accounting or equilibrium scenarios, whereas econometric identification uses variation in observations; hybrid research can connect them only with an explicit mapping and uncertainty treatment.

## Operational starting point and public skill precedents

The [econometrics skill](../../../../skills/model/01_socioeconomic_natural_change/econometric-analysis/SKILL.md) provides a small cross-sectional OLS calculator and an analysis routing checklist. It does not implement DiD, IV, RDD, fixed effects or a structural model. For those, specify the design and use a reviewed specialist implementation, such as [fixest](https://lrberge.github.io/fixest/reference/feols.html) for selected R panel workflows; choose variance estimators deliberately using the [fixest standard-error guide](https://lrberge.github.io/fixest/articles/standard_errors.html).

The organization draws on two publicly released agent skills: [EconAgentSkills](https://github.com/JonasWeinert/EconAgentSkills) separates data discipline, econometric methods and reproducible reporting, and [econometrics-skill](https://github.com/xiaomihu1992/econometrics-skill/blob/main/SKILL.md) starts from outcome, treatment, confounding and identifying variation. These are workflow references, not imported code or an endorsement of every estimator or default in either repository. Their implementation limitations must be reviewed before use.
