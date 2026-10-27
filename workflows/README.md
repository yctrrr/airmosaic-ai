# Executable workflow definitions

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

**Status: not implemented.** No workflow engine, executable pathway, workflow schema or workflow command is registered. This directory contains only status and authoring guidance; it is not scanned by the current tool registry or runner.

Human-facing choices and handoffs live in [methods/pathways](../methods/pathways/README.md). Historical stage proposals remain there as non-executable references. Scientific explanations belong in methods, computer operations in skills, and shared execution in `airmosaic/`.

## Conditions for a future definition

A future `<pathway_id>/workflow.yaml` must identify its version, purpose, applicable stages, supported inputs and outputs, actual tool IDs, dependencies, artifact bindings, checks, manual prerequisites and stopping conditions. Path-specific contracts may live alongside it. Such a declaration will require a reviewed engine and meaningful validation before execution; adding YAML alone grants no capability or authorization.

The planned engine will preflight the path, delegate single-tool operations to the existing execution service, register artifacts and check each handoff before continuing. Failed checks preserve partial artifacts and block downstream steps. Resume must account for prior external effects. Process success, contract validation and scientific validation remain separate states.

The catalog service may index definitions from this directory in the future, without keeping a duplicate definition. Local MCP and CLI already share single-tool services; they can use workflow services once those are implemented. There is currently no automatic connection between research stages. Stage 02 remains conceptual methods only, with no concrete data, parameter values or implementation.

## Data and project results

Follow the [asset contract](../harness/assets.md). Shared data outside Git uses `assets/data/<stage>/<dataset-name>/<version>/` with actual dataset names. Projects reference fixed versions in configuration without cross-stage duplication. New results use `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`, with records and temporary files inside that run. New calls provide project and stage together. Compute/check, obtain human review, then register selected data in a fresh version; never overwrite originals or existing versions. Personal settings, authentication and credentials remain separate. Existing files are not migrated; automatic approval and registration services are not implemented.
