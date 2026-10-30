# PM2.5 mortality risk and paired scenarios

**English** | [中文](health_impacts_ZH.md)

Estimate long-term attributable mortality only after selecting a compatible exposure–response model and baseline mortality definition. This method explains scientific decisions; the [health skill](../../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md) handles configuration, source records, template adaptation and checks.

## Select the estimand and response model

| Family | Meaning and selection requirement |
|---|---|
| GEMM | Burnett et al. (2018), outdoor-air cohort evidence. NCD+LRI and five cause-specific models are alternative endpoint constructions; never add their burdens together. Select the exact age parameters, inclusion/exclusion of the Chinese cohort, reference exposure and uncertainty implementation. |
| IER | Burnett et al. (2014) and subsequent version-specific updates integrate risk evidence from multiple particle sources. Select the exact release, cause/age parameters and counterfactual distribution. An IER table cannot be relabelled GEMM. |
| Log-linear | A published RR for concentration increment ΔC implies β = ln(RR_ΔC)/ΔC. With a task-defined reference C0 and declared below-reference rule, RR(C; C0) = exp[β × max(C−C0, 0)]. The floor is an assessment assumption, not proof of a biological threshold. A constant slope is not a complete nonlinear GEMM/IER model. |

The historical WHO HRAPIE 2013 recommendation for annual mean PM2.5 and natural-cause mortality at ages 30+ is a bounded log-linear entry, not a default for every region or current evidence. WHO published HRAPIE-2 in 2025; new studies should review it and justify their chosen version. Available real parameters, provenance and unresolved restrictions are described in the skill's [ER source record](../../skills/model/04_integrated_impacts/health_impact_analysis/references/exposure_response.md).

## Match exposure, population and outcomes

Use long-term annual mean PM2.5 in µg/m³ on declared spatial support, with a documented averaging period and coverage. An annual field is a proxy for long-term exposure; immediate realization of a long-term risk contrast requires an explicit lag/steady-state assumption. Population, baseline rates and scenarios must have compatible years, locations and age/sex definitions. Missing exposure is not zero. Corrections and resolution changes belong in the [transport handoff](../03_atmospheric_transport/geos_chem.md).

Check **pollutant, statistic, period and unit** before accepting any model output. AQ-Bench's `o3_average_values` is a 2010–2014 average O3 target in ppb. It cannot feed these PM2.5 functions. Ozone needs its own verified response function and matching exposure statistic; a multiyear mean is not a seasonal mean of daily maximum 8-hour concentrations. Merely renaming columns or converting units does not resolve this mismatch.

Baseline rates must match cause, sex, age, geography, metric and period. Natural-cause/all-cause definitions, NCD+LRI and cause-specific baselines are not interchangeable. Sum mutually exclusive causes only; do not add natural-cause burden to its component diseases or short-term mortality to overlapping long-term mortality. Joint age-sex population fractions multiply total population; within-sex fractions multiply sex-specific population. Both-sex totals and separate sex strata are alternatives. Combine fine-age rates with matched population weights, never by adding rates. If RR varies by fine age, calculate attributable counts before aggregating. Keep explicit 80+ weights and age mapping; aggregate 25+ curves and fine-age rows are alternatives.

## Attributable mortality and avoided mortality

For grid g and mutually exclusive age-sex/cause strata (s,c), observed baseline death count B = P × m/100000, where m is deaths per 100,000 matched persons per year. For RR relative to the declared reference:

```text
AF(C) = 1 − 1/RR(C)
D_attributable(C) = sum_g,s,c [B_g,s,c × AF_g,s,c(C)]
```

A rate is not a count; a five-year rate is not automatically an annual rate. Check the source denominator and exposure period before multiplication.

Record whether m is the observed rate at baseline exposure C_baseline, a fixed set of matched stratum-specific rates, or a reference-exposure rate. These meanings cannot be silently interchanged. Do not multiply an age-standardized rate by actual population to reconstruct deaths. With an unnormalized risk function, baseline attributable deaths are B_baseline × [1 − RR(C0)/RR(C_baseline)]; the AF above assumes RR(C0)=1. If using counterfactual deaths B_C0 instead, the corresponding excess is B_C0 × [RR(C)/RR(C0) − 1], not B_C0 × AF(C). These identities assume compatible risk scaling. The following scenario ratio is an algebraic derivation from multiplying baseline deaths by the relative scenario risk, conditional on risk transferability and fixed other causes of mortality; it is not a new epidemiological estimate.

Declare which paired-scenario estimand is used:

- **Difference of fixed-rate attributable burdens:** hold P, matched stratum-specific m, risk functions and valid support fixed, and report D(C_baseline) − D(C_intervention). This is a fixed-rate accounting contrast.
- **Risk-scaled avoided deaths from observed baseline mortality:** under the same causal/steady-state assumptions, hold baseline death count B_baseline fixed and use B_baseline × [1 − RR(C_intervention)/RR(C_baseline)]. For a log-linear model without a reference crossing, this becomes B_baseline × [1 − exp(−β × (C_baseline−C_intervention))]. It generally differs from the fixed-rate AF difference because the latter does not rescale scenario baseline mortality.

Choose one consistently and label it; do not silently substitute one for the other. A reduction to the model reference makes them coincide when B is the observed baseline count. Preserve negative avoided deaths for worsened exposure. Separate demographic or baseline-rate changes from exposure-only effects. A modeled scenario contrast does not establish an empirically identified policy effect.

## Uncertainty and scientific checks

Validate RR=1 gives zero burden; identical scenarios give zero difference; hand arithmetic and `/100000` conversion agree; joins are complete and unique; excluded population is reported; grid totals match disjoint regional sums. Require the exact selected endpoint/age set rather than silently retaining only an intersection. Stop for unsupported concentration ranges, missing curve branches or ambiguous age labels. Never silently cap concentration at 200 or replace unmatched risk with zero.

Report response uncertainty separately from exposure, mortality and population uncertainty. RR confidence limits are not raw population-risk quantiles. For nonlinear models, preserve source draws/covariance and paired draws across scenarios; separate curve pointwise limits do not automatically produce a confidence interval for a regional sum or scenario difference. A slope-only log-linear interval remains conditional on all other inputs.

## Primary sources

- [Burnett et al. 2018, GEMM](https://doi.org/10.1073/pnas.1803222115) and its [author data repository](https://github.com/mszyszkowicz/DataGEMM).
- [Burnett et al. 2014, IER](https://doi.org/10.1289/ehp.1307049).
- [WHO HRAPIE 2013](https://iris.who.int/handle/10665/153692), Table 1; [HRAPIE author summary, Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4480843/).
- [WHO HRAPIE-2 2025](https://www.who.int/publications/i/item/9789289062633).

GBD Results baseline mortality acquisition does not supply ER curves. Select a verified response version explicitly. Catalogued health templates remain disabled in run-tool; neither their presence nor this method claims a validated health computation.
