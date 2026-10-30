# 02: Emission Inventory

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Methods and operations for converting activity and technology into emissions. The accounting entry now provides an explicit activity/technology/control calculator with synthetic examples and checks. It is a direct local script, not a registered run-tool/MCP adapter. Other conceptual entries, real-source preparation and spatial/time/species allocation retain their separately declared status.

## Entry points

- [Accounting and spatial methods](emission-inventory-methods/SKILL.md)

## Workflow and handoff

Follow the [four-step workflow](../../../harness/four-step-workflow.md): confirm scope, choose methods, check prerequisites and hand off validated artifacts. See the [stage methods](../../../methods/02_emission_inventory/README.md) and [shared methods](../../../methods/shared/README.md).

Documentation maintenance reads descriptions and interfaces only, not original data. Actual execution depends on tool manifests; directories and SKILL.md do not register tools.

Follow the [asset contract](../../../harness/assets.md): share data by stage, actual name and version; group results by project and run, referencing the same data across stages. Registration uses compute/check, human review and a fresh data version.
