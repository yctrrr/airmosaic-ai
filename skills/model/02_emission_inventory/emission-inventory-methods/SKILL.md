---
name: emission-inventory-methods
description: List conceptual emission accounting, control-efficiency and spatial allocation methods without concrete data, code or execution entrypoints.
---

# Emission-inventory modeling methods

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Select accounting and control-efficiency methods → distinguish sources of change → design conservation and double-counting checks → select spatial-allocation and temporal/species handoff methods.

See the [method and handoff guidance](../../../../methods/02_emission_inventory/README.md).

## Boundaries

Conceptual methods only: no dataset declaration, executable tool ID, implementation formula/code or local source anchor.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.
