# Understanding and preparing research data

**English** | [中文](data_quality_ZH.md)

Before using a dataset, establish what its values represent, how they were produced and which comparisons they support. A successful transfer establishes file access; scientific use requires the checks below.

## Understand the source

Record the original producer and actual distributor, product/version, coverage, access conditions and citation. Distinguish observations, quality-controlled releases, reanalysis, forecasts and filled or homogenized estimates. A third-party archive remains a distributor even if it preserves official observations.

Describe spatial support, time zone and timestamp meaning, instantaneous versus accumulated quantities, averaging periods and units. Identify revision histories, station changes and source quality flags.

## Describe uncertainty in context

Consider measurement and sampling error, spatial representativeness, missing acquisition, model/assimilation error, revisions and matching/conversion error. Their importance depends on the instrument, product, region and period. Missing quality flags do not demonstrate an error-free measurement, and one generic percentage rarely represents all sources.

## Prepare comparable observations

Preserve the source release and form a traceable derived version. Define unique keys and field mappings, resolve duplicates/conflicts, distinguish missing values from zeroes and convert units explicitly. Establish the time reference before aligning records.

Separate provider flags, structural checks, research exclusions and imputation. Mark unusual values before deciding to exclude them; high concentration alone is not proof of error. Retain the reason for each affected observation.

## Assess coverage before averaging

Remove duplicate or invalid observations before counting valid unique periods. Select completeness rules appropriate to the product and intended statistic, with their source and version. Where coverage is inadequate, retain a missing statistic and its reason rather than inventing a complete observation.

For cross-source comparisons, align the physical quantity, temporal support and spatial representation. Fit bias corrections and other learned transformations within the appropriate training data.

## Report a usable handoff

Include source/version, mapping and transformation rules, coverage/exclusion summaries, quality status and unresolved limitations. The project selects its internal result layout under the [asset contract](../../harness/assets.md); a reviewed data version can later be referenced by other studies.

Source-specific explanations: [stations](../03_atmospheric_transport/pm25_stations.md), [ERA5](../01_socioeconomic_natural_change/era5.md), [CAMS](../01_socioeconomic_natural_change/cams.md), [WorldPop](../01_socioeconomic_natural_change/worldpop.md), [GBD](../04_integrated_impacts/ihme_gbd.md). Their completeness and interpretation rules are not interchangeable.
