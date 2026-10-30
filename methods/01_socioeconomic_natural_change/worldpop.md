# WorldPop: population surfaces and conservation of counts

**English** | [中文](worldpop_ZH.md)

Population grids are spatial estimates, not cell-by-cell enumeration. Choose the product and aggregation design to match the exposure question. Acquisition is described by the [WorldPop skill](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md).

## Provenance and product selection

WorldPop teams at the University of Southampton and partners combine censuses, official estimates/projections, boundaries and geographical covariates. Underlying population and boundary inputs differ by country, year and release. See the [official FAQ](https://www.worldpop.org/faq/).

| Product | Selection implications |
|---|---|
| [Global1 2000–2020](https://hub.worldpop.org/Global1_2000-2020) | Distinguish constrained/unconstrained distribution and UN-adjusted/other total benchmarks |
| [Global2 2015–2030](https://hub.worldpop.org/project/categories?id=3) | The reviewed R2025A v1 family includes country 100 m/1 km and global 1 km products; assumptions and release differ from Global1 |
| [Global2 country 1 km R2025A v1](https://hub.worldpop.org/geodata/listing?id=136) | People per pixel, constrained; the historical small-file example was LIE, 2020, UN-adjusted, not China or the full world |
| Catalog REST API | Metadata discovery at `https://hub.worldpop.org/rest/data`; separate from scientific aggregation |
| [Regional statistics API v2](https://api.worldpop.org/v2/) | Geometry-based statistics, a different service from raster discovery/download |

Product snapshots above were reviewed on 2026-10-26. Confirm a chosen release record before new acquisition. Retain its license, recommended citation and DOI; the reviewed Global2 population product DOI is `10.5258/SOTON/WP00840`, with CC BY 4.0 stated by its provider. Fix alias, ISO3, **population year `popyear`**, resolution, constraint, adjustment and release; publication dates do not replace population reference years.

## Uncertainty

Census omissions, dates, boundaries, interpolation and projection affect totals and spatial allocation. Building/built-area errors affect constrained distributions; zero allocation is not a field-confirmed absence of people. Matching a national benchmark does not prove cell accuracy. Annual population does not describe hourly mobility or individual activity.

Global1 and Global2 may differ in inputs, methods and grids; raw subtraction/splicing can confound product changes with demographic change. The [R2025A v1 release statement](https://data.worldpop.org/repo/prj/Global_2015_2030/R2025A/doc/Global2_Release_Statement_R2025A_v1.pdf) describes an alpha release subject to updates. It aligns country totals with WPP 2024 January 1 estimates; do not silently equate these to midyear population. Retain acquisition date and checksum.

## Normalization and aggregation

1. Select total population or age/sex groups and verify country, `popyear`, product, release and file identity.
2. Decode the raster; check bands, CRS, affine/grid, pixel size, dtype, NoData, extent and valid values. Preserve metadata and checksums.
3. Distinguish counts from density. People per pixel can be summed over compatible complete cells; people per hectare/km² require actual areas. Angular degrees are not km².
4. Preserve NoData separately from zero. Require finite nonnegative valid values, investigate anomalies and avoid cellwise rounding that changes totals.
5. Reproject/aggregate counts with an explicit mass-conserving allocation. Bilinear interpolation alone does not conserve population. Report target grid, area assumptions and before/after totals; densities and age shares need different treatment.
6. For zonal sums, reconcile boundary vintage, CRS, grid overlap and coastal NoData. State partial-cell allocation rules and report incomplete regional coverage.
7. Require mutually exclusive, well-defined age/sex groups; compare subgroup sums to totals in the same product/year. Align dates and denominators with GBD, concentrations and risk functions; total-population rasters alone do not supply all health inputs.

See [shared data quality](../shared/data_quality.md) and [population/health alignment](../shared/population_health.md).
