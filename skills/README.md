# Skills: four stages and shared capabilities

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

Skills describe concrete computer operations: software setup, input preparation, invocation and operational checks. Keep scientific explanations in [methods](../methods/README.md), human pathway narratives in [methods/pathways](../methods/pathways/README.md), and shared runtime code in [core](../harness/usage/runtime.md).




Data acquisition and modeling follow four stages: 01 Socioeconomic and Natural Change, 02 Emission Inventory, 03 Atmospheric Transport and Chemistry, and 04 Integrated Impacts. See the [four-step guide](../harness/four-step-workflow.md) for sequence and status.

- [Data acquisition](data_acquisition/README.md): sources, inputs and processing boundaries.
- [Modeling](model/README.md): methods, configuration and acceptance.
- [Methods](../methods/README.md): mappings to real skill files, not skill/tool registration.
- [Add or maintain a skill](../harness/skill-authoring.md): bilingual files, required content, registration boundaries and review checks.

Shared capabilities retain their shared, IAM and machine_learning homes. A SKILL.md adds guidance only; tool registration and executability depend on catalog/tools and the runner allowlist. English entry points use canonical filenames; Chinese counterparts end in `_ZH.md`. Historical long references retain their current language in this migration.

## Data and project results

Follow the [asset contract](../harness/assets.md). Shared data outside Git uses `assets/data/<stage>/<dataset-name>/<version>/` with actual dataset names. Projects reference fixed versions in configuration without cross-stage duplication. New results use `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`, with records and temporary files inside that run. New calls provide project and stage together. Compute/check, obtain human review, then register selected data in a fresh version; never overwrite originals or existing versions. Personal settings, authentication and credentials remain separate. Existing files are not migrated; automatic approval and registration services are not implemented.
