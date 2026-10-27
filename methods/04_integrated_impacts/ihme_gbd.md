# IHME GBD: provenance, estimation uncertainty and normalization

<!-- README-I18N:START -->

**English** | [中文](ihme_gbd_ZH.md)

<!-- README-I18N:END -->

Reviewed: 2026-10-26. Primary stage: 04. The [shared population and health method](../shared/population_health.md) links this reference; execution is described in the [GBD skill](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md). Documentation adds no tool or acquisition permission.

## Provenance and product identity

IHME and the Global Burden of Disease Collaborative Network combine vital registration, surveys, surveillance and research inputs with quality processing and statistical estimation. Results are organized by location, year, age, sex and cause. **Results Tool outputs are synthesized estimates, not individual case records or exclusively observed death-registration counts.**

- Use [GBD Results](https://vizhub.healthdata.org/gbd-results/) to select and export results.
- Use [GBD 2023 resources](https://ghdx.healthdata.org/gbd-2023) and the [source catalog](https://ghdx.healthdata.org/gbd-2023/sources) to trace inputs and versions. Record exported estimates separately from underlying inputs.
- Consult the [GBD 2023 demographic paper](https://pubmed.ncbi.nlm.nih.gov/41092927/) and [disease, disability and risk paper](https://doi.org/10.1016/S0140-6736(25)01637-X). Check each indicator against its own methods and appendices.

The observed page displayed GBD 2023. Release round and study year are different: a 2020 estimate in GBD 2023 need not equal its counterpart in GBD 2021. Prefer one round for the study period; examine method and input revisions before interpreting cross-round differences as health changes.

Choose products through the [available-data table and download plans](ihme_gbd_availability.md), which separate official offerings, adapter support and verified acquisition.

Use, licensing, citation and export requirements follow [IHME terms](https://www.healthdata.org/data-tools-practices/data-practices/terms-and-conditions) and the product page. A paper's open license does not imply unrestricted rights to all inputs or results. The user handles terms and login; do not share credentials, cookies or task download links.

## Indicators and dimensions

| Item | Meaning and handling |
|---|---|
| Number | Counts such as deaths or DALYs may be non-integer estimates; do not round each row before calculation |
| Rate | Verify denominator and units; per 100,000 is common, but the selected product governs |
| Percent | Verify denominator and whether values use 0–1 or 0–100 encoding before scaling |
| Age-specific, all-age and age-standardized | Different estimands; do not multiply age-standardized rates by actual population to reconstruct counts or substitute crude all-age rates for age-specific rates |
| All causes, parent and child causes | Hierarchies overlap; do not add all causes to components or sum overlapping parent/child categories |
| Sex and location | Do not add both-sex totals to male/female results or combine global, national and nested subnational totals |
| Cause deaths and risk attribution | Cause deaths are baseline outcomes; pollution attribution requires risk dimensions and a comparative-risk framework |
| Population and population_group | `population_group` is not a population-count switch; confirm the population product, channel and dimensions separately |

## Error and uncertainty

- Input coverage, under-registration, diagnosis, coding and registration quality vary. Sparse-data settings rely more heavily on modeling and cross-location/time information.
- Cause classification, unusable-code treatment, covariates, models, population denominators and release revisions affect estimates and comparability.
- Retain `val`, `lower` and `upper`. An uncertainty interval is not simply a survey confidence interval; its width does not identify every input error.
- Aggregations, differences and ratios require joint uncertainty propagation. Adding lower bounds and upper bounds is not a rigorous combined interval, and independence between causes or years cannot be assumed.

Consult the specific round and indicator methods. For example, the [GBD 2023 cause-of-death paper](https://doi.org/10.1016/S0140-6736(25)01917-8) describes percentile-based 95% uncertainty intervals. Do not impose one draw count or error percentage on all products.

## Normalization and validation sequence

1. **Fix the query contract:** record round, context, years, locations, causes/risks, ages, sexes, measure and metric with IDs and labels. Verify a small scope first; historical IDs are syntax examples.
2. **Require fresh results:** wait for completion and check returned dimensions. Old rows during loading, residual rows after errors and previous files are not current success evidence.
3. **Preserve the export:** save the new raw file with non-secret request metadata, acquisition time and checksum. Keep derived tables separate; exclude account details and temporary URLs from shared records.
4. **Define schema and keys:** common fields include dimension IDs/names, year and `val/lower/upper`. Follow the actual export schema. Include round, context and every applicable dimension in the key; do not infer IDs from column order or translated names.
5. **Validate content:** compare requested and returned IDs/labels, counts and missing combinations. Require parsable finite values and `lower ≤ val ≤ upper`. Missing rows are not zeros. Check valid ranges by indicator; structure alone does not establish model accuracy.
6. **Align population and age:** define age boundaries, open-ended groups, infancy groups and denominators explicitly. Use compatible counts and weights when aggregating; averaging age-specific rates does not create an overall rate.
7. **Prepare downstream use:** align age-specific baseline rates with population, concentration and cause definitions required by the risk function. WorldPop and GBD populations are not automatically interchangeable; explain totals, age structures and reference dates.
8. **Handle time and gaps:** prefer a full period from one round. Document and flag interpolation, supplementation or cross-round harmonization rather than applying an old project's year cutoff.

Before health calculations, check risk functions and scenarios using the [health-impact method](health_impacts.md). See the [first-download guide](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md) for operations, manual steps and the verified website example.
