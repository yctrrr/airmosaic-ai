# Modeling

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Start from the [four-step workflow](../../harness/four-step-workflow.md):

- [01: Socioeconomic and Natural Change](01_socioeconomic_natural_change/README.md)
- [02: Emission Inventory](02_emission_inventory/README.md)
- [03: Atmospheric Transport and Chemistry](03_atmospheric_transport/README.md)
- [04: Integrated Impacts](04_integrated_impacts/README.md)

General capabilities without a designated primary stage are in [shared](shared/README.md); capabilities owned by a stage may also serve other stages through references. See the [methods library](../../methods/README.md) for each stage's methods.

Follow the [asset contract](../../harness/assets.md): share data by stage, actual name and version; group results by project and run, referencing the same data across stages. Registration uses compute/check, human review and a fresh data version.

Use `skills/model/<stage>/<capability>/`, with the same stage values as `methods/<stage>/`; capabilities without a designated primary stage use `shared`, while other stages reference stage-owned capabilities. `methods/index.yaml` explicitly maps explanations to operations. One method may reference several skills, but each skill has one maintained home.
