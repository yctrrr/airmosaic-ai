# Complete pathway explanations

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

This area explains complete research paths for people and research-design agents: purpose, applicability, scientific assumptions, inputs, sequence, handoffs and acceptance. Computer operations live in skills; shared execution lives in core. See the [layout](../../harness/project-layout.md).

**Status: design references.** No pathway here is executable. The previous workflow entry and stage proposals have moved here as method documentation. They are not discovered skills, registered tools or runtime policies. The [core workflow area](../../workflows/README.md) has no implemented engine or executable path definitions.

## Research stages and handoffs

| Stage | Meaning | Historical proposal |
|---|---|---|
| 01 Socioeconomic and Natural Change | Describe activity, resources and natural background/drivers | [Stage reference](references/stage-designs/01_socioeconomic_natural_change.yaml) |
| 02 Emission Inventory | Explain how activity and technology can be translated into emissions | [Methods-only reference](references/stage-designs/02_emission_inventory.yaml) |
| 03 Atmospheric Transport and Chemistry | Describe transformations from emissions to concentrations and related fields | [Stage reference](references/stage-designs/03_atmospheric_transport.yaml) |
| 04 Integrated Impacts | Assess responses of human society and natural systems | [Stage reference](references/stage-designs/04_integrated_impacts.yaml) |

Stages classify research responsibilities; they do not force a four-step execution sequence. Background inputs may feed later stages directly. Cross-stage capabilities stay shared. Stage 02 contains conceptual methods only, without concrete data, parameter values, implementation code, project scripts or executable commands.

The historical YAML files preserve earlier candidates and interface ideas, not verified defaults. Their numerical thresholds, output resolutions, formulas and high/low-data alternatives are not automatic method-selection or execution rules. Select methods using data quality, scientific assumptions, resources, baselines and independent validation; sample size alone is insufficient. Proposed causal methods also require an appropriate identification design.

## How to use a path

For user-specified model construction and reference-code validation, see [model building from research requirements](requirements_driven_model_building.md). It separates reusable capabilities, new task specifications and reproduction cases; it is a design reference rather than an implemented training path.

1. Define the research question, scope, required result and permitted operations.
2. Read relevant methods and use the [four-stage navigation](../../harness/four-step-workflow.md) to select existing skills.
3. Query actual tool IDs and readiness; review input compatibility and missing manual preparation.
4. Define upstream/downstream fields, units, time/space semantics and acceptance conditions before handing off artifacts.
5. Use single-tool dry-run and authorized execution where supported, then inspect artifacts and validation evidence. Do not infer automatic chaining from these diagrams.
6. Share the sanitized handoff described in the [handoff guide](../../harness/usage/workflow-handoff.md).

## Future validated paths

A future human narrative may use `<pathway_id>.md` and its Chinese sibling. Its corresponding execution definition would live under `workflows/<pathway_id>/`. Keep scientific reasoning here and machine bindings there, with stable IDs and reciprocal links. A path must disclose its implementation, tested version, validation scope and manual parts. Do not add placeholder executable definitions for unsupported methods.

Planning and reading a path grant no data access, software installation, network submission, model execution or publication authority. Use the [storage contract](../../harness/storage-and-credentials.md); original data and credentials are not needed for documentation maintenance.

## Data and project results

Follow the [asset contract](../../harness/assets.md). Shared data outside Git uses `assets/data/<stage>/<dataset-name>/<version>/` with actual dataset names. Projects reference fixed versions in configuration without cross-stage duplication. New results use `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`, with records and temporary files inside that run. New calls provide project and stage together. Compute/check, obtain human review, then register selected data in a fresh version; never overwrite originals or existing versions. Personal settings, authentication and credentials remain separate. Existing files are not migrated; automatic approval and registration services are not implemented.
