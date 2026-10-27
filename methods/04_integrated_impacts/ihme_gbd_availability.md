# GBD data availability and download plans

<!-- README-I18N:START -->

**English** | [中文](ihme_gbd_availability_ZH.md)

<!-- README-I18N:END -->

Reviewed: 2026-10-26. See the [GBD method](ihme_gbd.md) for data meaning, uncertainty and normalization, and the [first-download guide](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md) for operations. Official product availability is distinct from adapter support and verified local acquisition.

## Official data scope

GBD 2023 disease, injury and risk estimates cover 1990–2023 and 204 countries and territories, with selected subnational estimates. The study reports 375 diseases/injuries and 88 risks; the cause-of-death study covers 292 causes. Valid combinations have constraints, so multiplying these totals does not give an export row count. Sources: [disease and risk paper](https://doi.org/10.1016/S0140-6736(25)01637-X), [cause-of-death paper](https://doi.org/10.1016/S0140-6736(25)01917-8).

The table also uses the [IHME tools guide, GBD 2021 edition](https://www.healthdata.org/sites/default/files/2024-06/IHME_GBD_2021_DATA_TOOLS_GUIDE_06262024.pdf) to identify product types and channels. That older guide does not establish current IDs, years or account export permissions.

| Product | Outputs and interpretation | Official route or evidence | Project boundary |
|---|---|---|---|
| Cause-specific deaths | Counts, rates and applicable proportions | Results → Cause; 2023 cause-of-death paper, 1990–2023 | One global all-cause count website export verified; other combinations and run-tool remain unverified |
| YLLs | Years of life lost, counts/rates | Results → Cause; 2023 burden study | Measure parameter available; current selections need checking, not individually tested |
| YLDs | Years lived with disability, counts/rates | Results → Cause; 2023 burden study | Same boundary; not individually verified |
| DALYs | Disability-adjusted life years, counts/rates | Results → Cause; 2023 burden study | Do not add DALYs to their YLL/YLD components |
| Incidence and prevalence | Counts and applicable rates/proportions | Results → Cause; tools guide and disease methods | Check cause/age validity; export not verified |
| Risk-attributable burden | Attributable deaths, YLLs, YLDs, DALYs and applicable PAFs | Results → Risk; 2023 risk study | No independent risk ID argument; changing context is insufficient; use the website or adapt the interface |
| Risk exposure | SEV; pollutant concentrations require the corresponding exposure product | SEV entry; risk study and tools guide | No verified dedicated interface; SEV is not PM2.5 concentration |
| HALE | Healthy life expectancy in years | Corresponding Results entry; 2023 burden study | Verify dedicated dimensions, not automatically supported by the cause adapter |
| All-cause mortality and life expectancy | Demographic mortality, life expectancy and related estimates | Round-specific GHDx product; [demographic paper](https://pubmed.ncbi.nlm.nih.gov/41092927/) | Verify tables, years and channel separately; life expectancy is not a rate per 100,000 |
| Population, life tables and fertility | Age/sex population and demographic indicators | Tools guide; Results navigation or GHDx record | Check release and period per product; population export unverified; population_group is not a count switch |
| Other topics | Etiology, injury nature and impairment results where provided | Tools guide and current topic product | Dedicated arguments are missing; manual selection/adaptation required |

Results commonly export CSV, while some products use separate records or asynchronous download tasks. Preserve estimates and available uncertainty bounds. Rounded website cells are not full-precision exports. The source catalog indexes inputs; it does not make every input microdataset publicly downloadable.

## Dimensions to constrain

| Dimension | Suggested scope | Checks |
|---|---|---|
| Release round | Prefer GBD 2023 for this task | Use one round over the study period; verify the version ID rather than copying historical defaults |
| Time | Usually 1990–2023 for disease/risk studies; 2000–2023 may suit a research task | Demographic, life-table and topic periods may differ |
| Location | Global, region, country; add provided subnational locations when needed | Avoid overlapping totals; do not promise arbitrary county, city or grid data |
| Sex | Male, female or both | Do not combine both-sex totals with components; some indicators restrict sex |
| Age | Age-specific, all-age or age-standardized, requested separately | The study commonly reports 25 fine age groups, but product selections can include aggregates or restrictions |
| Cause/risk | A small set of target leaf causes or risks | Avoid overlapping hierarchies |
| Measure | Applicable deaths, YLLs, YLDs, DALYs, incidence or prevalence | Defines the estimand, not merely the unit |
| Metric | Applicable number, rate or percent | Check units/denominators; age-standardized rates cannot reconstruct counts using actual population |

## Suggested download scopes

A has passed. B and C are candidate plans, not completed downloads. Define the research task before expanding the scope.

| Stage | Scope | Expected combinations | Purpose |
|---|---|---:|---|
| A: verified connectivity check | GBD 2023; 2023; Global; All causes; All ages; Both; Deaths; Number | 1 | Fresh result, ZIP acquisition and CSV content verified |
| B: small China table | 2019/2023; China; ischemic heart disease; All ages; Both; Deaths; Number and Rate | Up to 4 | Check country, years and count/rate distinctions after verifying options |
| C: candidate health-model baseline | 2000–2023; China; six candidate causes; male/female; 15 groups from 25–29 to 95+; Deaths; age-specific Rate | Up to 4,320 | Age-specific baseline mortality; confirm risk-function, cause and age applicability |

C's candidate causes are ischemic heart disease, stroke, COPD, tracheal/bronchus/lung cancer, lower respiratory infections and type 2 diabetes. This is not a universal PM2.5-model cause set. Adapt the plan if the selected risk function requires children, other ages or different cause definitions.

Count combinations as locations × years × causes × sexes × ages × measures × metrics. Inapplicable combinations may reduce actual rows. The estimate and bounds are fields in a record, not three extra records. Do not begin with every cause, age and location.

## Current verified state

On 2026-10-26, scope A passed the official website route: fresh result checked at 21:00, export submitted at 21:02, 717-byte ZIP acquisition confirmed at 21:05, and one-record/18-column CSV validation completed at 21:05:42. Times are Beijing time (UTC+8). Follow the [verified guide](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md). No task CDP session was confirmed for a real `ihme_gbd_fetch_results` call.

The user handled access verification. No authentication state was copied or internal endpoint used to replace verification. Only the new export was inspected, not existing research data.
