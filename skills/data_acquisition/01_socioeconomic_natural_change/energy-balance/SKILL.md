---
name: energy-balance-methods
description: Guide source-version tracking, unit conversion and sector-boundary review for energy-balance processing. No executable adapter.
---

# Energy balance and unit-conversion methods

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Specify source version and statistical denominator → distinguish physical quantities from conversion factors → check sector/energy mappings → design share, closure and missingness audits.

See the [method and handoff guidance](../../../../methods/01_socioeconomic_natural_change/energy_balance.md).

## Boundaries

Do not execute the original local entry point from this repository or copy fixed output directories and historical conversion rules.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
