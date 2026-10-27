---
name: inventory-input-methods
description: List conceptual source and input-contract methods for emission inventories. Do not expose concrete data, implementation code or local script references.
---

# Emission-inventory input methods

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Define source categories and accounting scope → choose methods for reviewing activity, technology and factor sources → agree unit, species and mapping semantics → list gaps and handoff contracts.

See the [method and handoff guidance](../../../../methods/02_emission_inventory/README.md).

## Boundaries

List conceptual methods only. Do not add concrete data, parameter values, project fields, script names, source fingerprints, commands or implementation code.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.
