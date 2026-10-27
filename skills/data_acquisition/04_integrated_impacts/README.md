# 04: Integrated Impacts

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Health, economic, distributional, ecological, agricultural and climate impacts of pollution/environmental change. GBD has a controlled adapter; one website query/download passed content checks, while real runner acquisition remains unverified. Health calculations/plots are templates; complete cost/distribution workflows need adaptation.

## Entry points

- [GBD](ihme-gbd-results/SKILL.md)

Begin with the [login/minimal-query guide](ihme-gbd-results/references/first-download-guide.md). Data provenance, uncertainty, counts/rates and age standardization live in the [method](../../../methods/04_integrated_impacts/ihme_gbd.md). Check website access and task CDP prerequisites separately.

Reference [stage 03 stations](../03_atmospheric_transport/pm25-stations/SKILL.md) for concentration observations; they do not directly replace exposure or health calculations.

Reference [ERA5](../01_socioeconomic_natural_change/era5/SKILL.md) and [CAMS](../01_socioeconomic_natural_change/cams/SKILL.md) in stage 01 for covariates/gridded composition. These acquisition references require time/space and representativeness checks; do not duplicate workflows or automatically chain a health model.

## Workflow and handoff

Follow the [four-step workflow](../../../harness/four-step-workflow.md): confirm scope, choose methods, check prerequisites and hand off validated artifacts. See the [stage methods](../../../methods/04_integrated_impacts/README.md) and [shared methods](../../../methods/shared/README.md).

Documentation maintenance reads descriptions and interfaces only, not original data. Actual execution depends on tool manifests; directories and SKILL.md do not register tools.

Ecology, agriculture and climate impacts currently provide scope navigation only. Select receptors, indicators, methods and evidence manually; no dedicated executor exists. Natural conditions are upstream drivers in 01 and evaluated responses here.

Follow the [asset contract](../../../harness/assets.md): share data by stage, actual name and version; group results by project and run, referencing the same data across stages. Registration uses compute/check, human review and a fresh data version.
