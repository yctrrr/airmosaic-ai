# 03: Atmospheric Transport and Chemistry

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Station PM2.5 acquisition/preparation and model input contracts from emissions to concentration. ERA5/EAC4/CAMS forecasts belong to 01 and are referenced here. This stage has no download, preparation, compilation, simulation or scheduler adapter.

## Entry points

- [Input preparation](atmospheric-inputs/SKILL.md)
- [PM2.5 stations](pm25-stations/SKILL.md): distinguish hourly archives and homogenized daily values; no runner adapter.
- [ERA5 in stage 01](../01_socioeconomic_natural_change/era5/SKILL.md)
- [CAMS in stage 01](../01_socioeconomic_natural_change/cams/SKILL.md)

Choose the ERA5/CAMS product first, then follow the [Copernicus guide](../../../harness/usage/copernicus-downloads.md) for account, non-secret request, paths and checks. Stations follow their own source workflow. Acquisition and preparation are separately scoped, not automatically triggered.

## Workflow and handoff

Follow the [four-step workflow](../../../harness/four-step-workflow.md): confirm scope, choose methods, check prerequisites and hand off validated artifacts. See the [stage methods](../../../methods/03_atmospheric_transport/README.md) and [shared methods](../../../methods/shared/README.md).

Documentation maintenance reads descriptions and interfaces only, not original data. Actual execution depends on tool manifests; directories and SKILL.md do not register tools.
