# 01: Socioeconomic and Natural Change

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Activity, energy, technology, population and natural conditions. WorldPop and company-basic-information ZIP processing support run-tool. ERA5, CAMS EAC4 and forecasts offer website/API guidance and verified small examples, without runner adapters. Yearbooks, energy and enterprise disclosure need adaptation.

## Entry points

- [CSMAR](csmar/SKILL.md): [first-download guide](csmar/references/first-download-guide.md), [verified browser example](csmar/references/first-download-example.md); scoped download validated, compatible ZIP processing implemented
- [Industrial yearbooks](ind_yearbook/SKILL.md)
- [WorldPop](worldpop/SKILL.md)
- [Enterprise disclosure](enterprise-disclosure/SKILL.md)
- [Energy preparation](energy-balance/SKILL.md)
- [ERA5 meteorology and natural conditions](era5/SKILL.md)
- [CAMS EAC4 reanalysis and global forecasts](cams/SKILL.md)

Choose observations, reanalysis or forecasts by the question, verify variables/time/grid/units, then follow the relevant skill. ERA5/EAC4/forecasts have one primary home here, referenced by 03/04. Station observations remain in [stage 03](../03_atmospheric_transport/pm25-stations/SKILL.md).

## Workflow and handoff

Follow the [four-step workflow](../../../harness/four-step-workflow.md): confirm scope, choose methods, check prerequisites and hand off validated artifacts. See the [stage methods](../../../methods/01_socioeconomic_natural_change/README.md) and [shared methods](../../../methods/shared/README.md).

Documentation maintenance reads descriptions and interfaces only, not original data. Actual execution depends on tool manifests; directories and SKILL.md do not register tools.

Follow the [asset contract](../../../harness/assets.md): share data by stage, actual name and version; group results by project and run, referencing the same data across stages. Registration uses compute/check, human review and a fresh data version.
