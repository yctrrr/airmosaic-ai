# CAMS: using reanalysis and forecasts in research

**English** | [中文](cams_ZH.md)

CAMS supplies atmospheric-composition context and comparison fields. Interpret EAC4 and operational forecasts as different products with different time structures. Acquisition belongs in the [CAMS skill](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md).

## Source and product identity

| Product | Production | Research meaning |
|---|---|---|
| [Global reanalysis EAC4](https://www.ecmwf.int/en/forecasts/datasets/cams-global-reanalysis-eac4) | CAMS/ECMWF atmospheric chemistry model with observational assimilation; distributed through ADS | Model-constrained historical composition; examine changing observations, species, levels and validation |
| [Global composition forecasts](https://www.ecmwf.int/en/forecasts/datasets/cams-global-atmospheric-composition-forecasts) | Assimilated initialization followed by forward integration | Retain initialization, lead and system release; operational upgrades affect long-term consistency |

Satellite assimilation does not imply a ground measurement for every PM2.5 cell. Surface mass concentration, gas mixing ratio, column total and AOD are different physical quantities. See the [official forecast documentation](https://confluence.ecmwf.int/pages/viewpage.action?pageId=673323626). European regional products require their own specification.

## Uncertainty and suitability

Chemical/aerosol processes, transport, initialization, boundaries and emissions introduce uncertainty; disagreement with a station cannot identify a single cause. Assimilated species, vertical sensitivities and coverage differ from surface-monitoring coverage and change over time. Grid cells differ from local stations in terrain, local pollution and boundary-layer support.

Forecast error varies with species, region, initialization and lead. Evaluate leads separately and examine system upgrades; overlapping forecasts are not independent observations. Use product-specific [EAC4 validation](https://atmosphere.copernicus.eu/node/1418) and [global-service reports](https://atmosphere.copernicus.eu/eqa-reports-global-services), rather than applying one error percentage to every field. File checks do not establish independent observational accuracy.

## Comparable fields and time series

1. Fix product, parameter, surface/model/pressure coordinate, grid and units together.
2. Convert PM2.5 from kg/m³ to µg/m³ by `10^9` only when the metadata declare that mass-concentration unit. Gas mass mixing ratios need different formulas and supporting density/temperature/pressure information.
3. Retain EAC4 UTC sampling. Key forecasts by product/system, initialization, lead, variable, level and grid; compute `valid_time = forecast_reference_time + leadtime` explicitly.
4. Predetermine fixed-initialization or lead-selection rules for overlapping valid times. Evaluation may use only forecasts actually available at the decision time; do not default to averaging initializations.
5. Define day boundaries and sampling support. Three-hour instantaneous samples at 00,03,…,21 provide eight samples per UTC day, not 24 observed hours. Set coverage and weighting by field definition; station 20-hour thresholds do not apply.
6. Separate missing files/times, nonfinite values and unit/level errors. Do not substitute another initialization without marking it or fill missing values with zero.
7. Match station observations only after reconciling UTC/local time, averaging, concentration state, surface definition and spatial support. Fit bias correction on training data and retain independent evaluation. Species/grid/vertical conversion for a transport-model boundary is a separate method.

Do not splice EAC4 and operational forecasts into a homogeneous trend series without studying product and system differences.
