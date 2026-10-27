# Research-stage handoff and traceability

<!-- README-I18N:START -->

**English** | [中文](workflow-handoff_ZH.md)

<!-- README-I18N:END -->

This guide defines manual handoff checks. There is no workflow executor or enforced runtime contract. A fixed sample count, correlation or single test is not a universal scientific acceptance threshold. Originals and private logs remain in authorized local locations.

| Handoff | Required explanation | Acceptance condition |
|---|---|---|
| 01 → 02 | Definitions, units, classifications, coverage and source categories for activity, resources and technology | Accounting scope and method semantics are clear; Stage 02 remains methods-only, without concrete data or code |
| 01 → 03/04 | Product, variable, time, grid, unit and version for background and component inputs | Distinguish observation, reanalysis and forecast; separately validate conversion/matching; passing through Stage 02 is not required |
| 02 → 03 | Allocation and mapping methods, conservation and gaps | Define task-specific input compatibility; a directory does not establish generated inputs |
| 03 → 04 | Concentration unit, grid, surface definition, averaging, valid scope and validation summary | Check recipient-specific inputs and response metrics; observation validation criteria are task-specific |
| Shared → any stage | Applicability, version, boundaries and comparison design | Reference one skill; do not introduce concrete emission implementation or treat method references as executable tools |

## Records and comparison

Separate method selection, engineering execution and scientific acceptance. Identify baseline/intervention scenarios, permitted changes and common valid scope. Traceable sources alone do not establish causal identification. List missing items and unperformed checks explicitly.

Supported tools record sanitized metadata in `${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/records/<tool_id>/record.json`. This is not a complete cross-stage provenance chain or scientific-validation service. Unsupported workflows do not inherit runner protections. See [pathway explanations](../../methods/pathways/README.md), [workflow implementation status](../../workflows/README.md), [four-stage procedures](../four-step-workflow.md) and [single-tool execution](run-tool.md).
