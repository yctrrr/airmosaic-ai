# Workflow layer: analysis pipeline templates

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


Four-step atmospheric-environment workflow design. Step 02 lists conceptual methods only; other module and branching declarations are proposals requiring task-specific validation.

**Status: design templates.** No orchestrator or runtime enforcement is implemented. This document has no standard skill frontmatter and is not a registered executable tool. See the [harness](../harness/README.md) and [actual tool catalog](../harness/tool-catalog.md) for operations.

Use the [four-step guide](../harness/four-step-workflow.md) for procedures/status and the [methods library](../methods/README.md) for mappings. Step 02 is methods-only and GEOS-Chem is reference-only; neither has an automatic executor.

## Layer overview

```text
Layer 1: Socioeconomic and Natural Change
  Economic activity → Activity levels → Energy use → Control technology
  ↓
Layer 2: Emission Inventory
  Socioeconomic variables → Pollutant emissions → Carbon-emission changes
  ↓
Layer 3: Atmospheric Transport and Chemistry
  Emissions → Transport → Chemistry → Deposition → Concentrations
  ↓
Layer 4: Integrated Impacts
  Concentrations/environmental change → Health, economy and distribution / Ecology, agriculture and climate
```

## Data-volume branching

This is a proposal requiring domain validation, not automatic model selection or orchestration. Review sample size, label quality, suitability and independent validation together.

- **Adequate data and demonstrated suitability:** consider AI modeling; causal identification also requires a valid design and assumptions.
- **Insufficient data:** consider empirical formulas or documented manual corrections.

## Template files

| Layer | File | Description |
|---|---|---|
| 1 | `layers/01_socioeconomic_natural_change.yaml` | Socioeconomic and natural change |
| 2 | `layers/02_emission_inventory.yaml` | Emission-inventory methods |
| 3 | `layers/03_atmospheric_transport.yaml` | Atmospheric transport and chemistry |
| 4 | `layers/04_integrated_impacts.yaml` | Integrated impacts |

## Current invocation boundary

This is a design, not an executable skill or service. Select real registered IDs from the [catalog](../harness/tool-catalog.md), then follow the [run-tool guide](../harness/usage/run-tool.md) for supported single-tool tasks:

```powershell
python -m airmosaic_core.cli list-tools --category data_acquisition
python -m airmosaic_core.cli list-tools --category model
python -m airmosaic_core.cli run-tool airmosaic_list_datasets --dry-run
```

Adapters do not implement every stage or automatically connect acquisition, simulation, health templates and acceptance. Pass validated task artifacts explicitly; unsupported methods require implementation or manual adaptation and task authorization.

## Traceability

See the [manual handoff checklist](references/io_traceability.md) for interfaces, comparison scope and traceability limits.
