# Skills: operations across four research steps

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

Skills explain how to prepare software and inputs, perform an operation and check its outputs. [Methods](../methods/README.md) explain the research reasoning; [workflows](../workflows/README.md) combine data and skills.

## Find the research step

| Step | Operational coverage | Acquisition | Modeling and analysis |
|---|---|---|---|
| 01 Socioeconomic and Natural Change | Prepare upstream activity, population and natural-condition inputs | [Category](data_acquisition/01_socioeconomic_natural_change/README.md) | [Category](model/01_socioeconomic_natural_change/README.md) |
| 02 Emission Inventory | Select accounting and input methods; conceptual guidance only | [Category](data_acquisition/02_emission_inventory/README.md) | [Category](model/02_emission_inventory/README.md) |
| 03 Atmospheric Transport and Chemistry | Prepare atmospheric inputs and support simulation/observation analysis | [Category](data_acquisition/03_atmospheric_transport/README.md) | [Category](model/03_atmospheric_transport/README.md) |
| 04 Integrated Impacts | Prepare outcome inputs and assess human or natural impacts | [Category](data_acquisition/04_integrated_impacts/README.md) | [Category](model/04_integrated_impacts/README.md) |

Cross-stage operations have one home in shared [acquisition](data_acquisition/shared/README.md) or [modeling](model/shared/README.md), referenced where needed.

Project maintenance has a separate [agent-operations category](agent_operations/README.md), kept in shared rather than adding a research stage.

## Check the current capability

Category pages and individual `SKILL.md` files maintain the available operations and their status. Read the selected skill's dependencies, configuration, actual entrypoint and result checks. Use [tool queries](../harness/usage/tool-registry.md) for registered execution support and static prerequisites, and [run-tool](../harness/usage/run-tool.md) for reviewed adapters.

Detailed method relationships live in [methods/index.yaml](../methods/index.yaml). A skill document, a reference/template and an executable registration are distinct; inspect the selected entry rather than inferring support from its folder name.

## Contribute

Keep stage-specific skills in their primary stage and cross-stage capabilities under `shared`. Maintain bilingual instructions and the appropriate category/index when a capability changes; keep this overview focused on research steps and scope.

Follow [skill authoring](../harness/skill-authoring.md), [registration](../harness/tool-registration.md) and [asset storage](../harness/assets.md) for the operational details.
