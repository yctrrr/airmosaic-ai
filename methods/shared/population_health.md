# Aligning population and baseline health data

**English** | [中文](population_health_ZH.md)

Health-impact estimates require population, baseline outcomes, exposure and a risk function referring to compatible populations. Acquiring each file does not establish compatibility. Use [WorldPop](../01_socioeconomic_natural_change/worldpop.md) for spatial population estimates and [GBD](../04_integrated_impacts/ihme_gbd.md) for baseline health estimates.

Obtain exposure-response coefficients or curves separately from their published source using the [health-impact method and skill](../04_integrated_impacts/health_impacts.md). A baseline mortality export is not a risk curve. Match pollutant, exposure statistic/window, units, endpoint and eligible population before linking an upstream prediction; a PM2.5 response cannot be applied to an ozone prediction by renaming its column.

## Define a common study population

Specify geography/boundary vintage, year/reference date, age boundaries, sex and cause definitions. WorldPop and GBD may use different total benchmarks and age structures; justify a chosen reference rather than assuming interchangeable denominators. Prefer compatible products from one release across the period and treat revisions separately from observed change.

| Quantity | Alignment needed |
|---|---|
| Population counts | Count/density units, reference date, grid/boundaries, age/sex coverage |
| Baseline deaths | Cause hierarchy, count versus rate, age/sex and location definitions |
| Baseline rate | Correct denominator and unit scale; age-standardized rates cannot reconstruct actual counts |
| Concentration | Exposure period, spatial support and population distribution |
| Risk function | Applicable causes/ages, concentration units, exposure window and counterfactual |

For an age-specific baseline rate `r` per 100,000 and compatible population `P`, expected baseline deaths are `P × r / 100000`. This conversion requires a crude or matching age-specific rate; it is not valid for an age-standardized rate applied to actual population. Aggregate deaths and population first when constructing a combined rate, rather than averaging subgroup rates.

## Check coverage and uncertainty

Use nonoverlapping ages, sexes and regions; never add totals to their components. Preserve missing combinations and distinguish absent information from zero. Check subgroup totals, population conservation across spatial processing and consistency of concentration/population grids.

Retain baseline uncertainty and exposure/risk uncertainty separately. Derived totals and differences require a justified dependence structure or compatible joint draws; adding uncertainty bounds does not create a valid combined interval. Document population downscaling, age disaggregation and gap-filling as additional assumptions.

Acquisition steps are in the [WorldPop skill](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md) and [GBD skill](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md). Apply the [health-impact method](../04_integrated_impacts/health_impacts.md) after alignment.
