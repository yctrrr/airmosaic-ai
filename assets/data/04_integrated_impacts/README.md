# Stage data navigation

**English** | [中文](README_ZH.md)

Keep one primary location per dataset and reference its fixed version across stages. Public inputs must be declared synthetic fixtures or explicitly authorized licensed snapshots. Private data remain at the configured external asset root.

See the [asset entry](../../README.md).

Exposure-response source parameters belong under external `${AIRMOSAIC_ASSETS_DIR}/data/04_integrated_impacts/ExposureResponse/<dataset-version>/`, separately from population, exposure and baseline mortality. Follow the [health method](../../../methods/04_integrated_impacts/health_impacts.md) and [skill](../../../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md) for source/version, applicability and validation. Public provenance instructions do not grant redistribution rights for source attachments or authorize a health calculation.
