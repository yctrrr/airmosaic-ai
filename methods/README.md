# Scientific methods and pathway explanations

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

Methods primarily explain scientific reasoning to researchers: purpose, suitability, sources, assumptions, uncertainty, normalization and quality criteria. Research-design agents may consult them too. Computer operations and interfaces belong in skills; shared execution belongs in core. No original data are stored here.

## Research-stage navigation

| Stage | Methods | Acquisition skills | Software and computation skills |
|---|---|---|---|
| 01 Socioeconomic and Natural Change | [Methods](01_socioeconomic_natural_change/README.md) | [Operations](../skills/data_acquisition/01_socioeconomic_natural_change/README.md) | [Operations](../skills/model/01_socioeconomic_natural_change/README.md) |
| 02 Emission Inventory | [Conceptual methods](02_emission_inventory/README.md) | [Method references](../skills/data_acquisition/02_emission_inventory/README.md) | [Method references](../skills/model/02_emission_inventory/README.md) |
| 03 Atmospheric Transport and Chemistry | [Methods](03_atmospheric_transport/README.md) | [Input preparation](../skills/data_acquisition/03_atmospheric_transport/README.md) | [Operations](../skills/model/03_atmospheric_transport/README.md) |
| 04 Integrated Impacts | [Methods](04_integrated_impacts/README.md) | [Operations](../skills/data_acquisition/04_integrated_impacts/README.md) | [Operations](../skills/model/04_integrated_impacts/README.md) |
| Cross-stage | [Shared methods](shared/README.md) | [Shared operations](../skills/data_acquisition/shared/README.md) | [Shared operations](../skills/model/shared/README.md) |

Complete paths are explained in [pathways](pathways/README.md). Their executable definitions would belong in [core/workflows](../core/workflows/README.md), where no engine or executable path is implemented. The [four-stage guide](../harness/four-step-workflow.md) gives current operational status. Stages classify responsibilities, not mandatory execution order. Stage 02 remains conceptual methods only, with no concrete data, parameter values or implementation.

## Data explanations

Keep original producer versus provider, product identity, coverage, units, time semantics, uncertainty and normalization here as one authoritative body. Skills link these explanations and retain API/command details and operational examples in references. Cross-stage principles are in [data quality](shared/data_quality.md).

| Source | Main explanation | Supporting material |
|---|---|---|
| ERA5 | [Source, errors and normalization](01_socioeconomic_natural_change/era5.md) | Linked API and small-example guidance |
| CAMS EAC4 / global forecasts | [Products, errors and normalization](01_socioeconomic_natural_change/cams.md) | Separate linked examples per product |
| WorldPop | [Products, errors and normalization](01_socioeconomic_natural_change/worldpop.md) | [Population/health navigation](shared/population_health.md) and linked operational example |
| IHME GBD | [Sources, metrics and uncertainty](04_integrated_impacts/ihme_gbd.md) | [Availability and download planning](04_integrated_impacts/ihme_gbd_availability.md) |
| PM2.5 stations | [Source chain, errors and averaging](03_atmospheric_transport/pm25_stations.md) | [Sources](03_atmospheric_transport/pm25_stations_sources.md), [preparation](03_atmospheric_transport/pm25_stations_preparation.md), [homogenized daily product](03_atmospheric_transport/pm25_homogenized.md) |

The index contains 16 method topics. `document` identifies the main explanation and `supporting_documents` identifies additional files relative to this directory. Pathway explanations and supporting pages do not create new tool registrations. Historical specialist references retain their existing language.

## Method-to-skill mapping

| Method | Primary stage | Skill references | Overall state |
|---|---|---|---|
| [Literature discovery and archiving](shared/literature.md) | shared | [literature-workflow](../skills/data_acquisition/shared/literature-workflow/SKILL.md) | local_source |
| [Statistical yearbooks and tables](01_socioeconomic_natural_change/statistical_yearbooks.md) | 01_socioeconomic_natural_change | [ind_yearbook](../skills/data_acquisition/01_socioeconomic_natural_change/ind_yearbook/SKILL.md) | mixed |
| [Enterprise financial and environmental disclosures](01_socioeconomic_natural_change/enterprise_sources.md) | 01_socioeconomic_natural_change | [csmar](../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md), [enterprise-disclosure](../skills/data_acquisition/01_socioeconomic_natural_change/enterprise-disclosure/SKILL.md) | mixed |
| [Population and health inputs](shared/population_health.md) | shared | [worldpop](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md), [ihme-gbd-results](../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md) | registered_tools |
| [CEADs energy and standard-coal conversion](01_socioeconomic_natural_change/energy_balance.md) | 01_socioeconomic_natural_change | [energy-balance](../skills/data_acquisition/01_socioeconomic_natural_change/energy-balance/SKILL.md) | local_source |
| [Enterprise panels and statistical constraints](01_socioeconomic_natural_change/enterprise_panels.md) | 01_socioeconomic_natural_change | [socioeconomic-drivers](../skills/model/01_socioeconomic_natural_change/socioeconomic-drivers/SKILL.md), [csmar](../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md) | local_source |
| [Spatial inventory alignment](02_emission_inventory/spatial_inventory.md) | 02_emission_inventory | [inventory-input-methods](../skills/data_acquisition/02_emission_inventory/inventory-input-methods/SKILL.md), [emission-inventory-methods](../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md) | methods_only |
| [Emission accounting and control efficiency](02_emission_inventory/emission_accounting.md) | 02_emission_inventory | [emission-inventory-methods](../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md) | methods_only |
| [Control costs and allocation scenarios](shared/cost_scenarios.md) | shared | [cost-scenarios](../skills/model/shared/cost-scenarios/SKILL.md) | local_source |
| [Health impacts and paired scenarios](04_integrated_impacts/health_impacts.md) | 04_integrated_impacts | [health_impact_analysis](../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md) | mixed |
| [GCAM output analysis](shared/gcam.md) | shared | [gcam](../skills/model/IAM/gcam/SKILL.md) | registered_tools |
| [mlr3 and TimeXer](shared/machine_learning.md) | shared | [mlr3](../skills/model/machine_learning/mlr3/SKILL.md), [timexer](../skills/model/machine_learning/timexer/SKILL.md) | reference |
| [GEOS-Chem preparation, builds and handoff](03_atmospheric_transport/geos_chem.md) | 03_atmospheric_transport | [atmospheric-inputs](../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md), [geos-chem](../skills/model/03_atmospheric_transport/geos-chem/SKILL.md) | reference |
| [ERA5 acquisition](01_socioeconomic_natural_change/era5.md) | 01_socioeconomic_natural_change | [era5](../skills/data_acquisition/01_socioeconomic_natural_change/era5/SKILL.md) | reference |
| [CAMS reanalysis and forecast acquisition](01_socioeconomic_natural_change/cams.md) | 01_socioeconomic_natural_change | [cams](../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md) | reference |
| [PM2.5 station acquisition and preparation](03_atmospheric_transport/pm25_stations.md) | 03_atmospheric_transport | [pm25-stations](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) | reference |

`local_source` means external guidance without an adapter; `mixed` means only some related tools exist; `registered_tools` means the listed adapters exist while individual references remain non-executable; `reference` is guidance; `methods_only` is conceptual. Actual execution support comes from tool manifests, not an overall method label.

## Use and maintenance

Choose a method and define scope and handoff requirements, then read the mapped skill and query actual tool IDs. For supported tools, prepare non-secret parameters and inspect dry-run `can_execute` and `blockers`. Real acquisition, data reading or computation needs a bounded task; routine documentation checks use interfaces and synthetic inputs.

[index.yaml](index.yaml) maps documents, stages and skills; it is not a registry or executor. Data/results, non-secret settings and authentication remain in separate external roots. [Local-source examples](examples/local-sources.example.yaml) have empty roots and are not automatically loaded. See [sources](SOURCES.md) for dated evidence. Public source fingerprints are not data snapshots; emission methods contain no concrete implementation anchors.
