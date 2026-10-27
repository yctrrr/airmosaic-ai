---
name: socioeconomic-driver-methods
description: Plan socioeconomic activity, energy and technology driver workflows and route to existing shared modeling references. No driver simulation adapter.
---

# Socioeconomic and natural change methods

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

Natural-condition acquisition references [ERA5](../../../data_acquisition/01_socioeconomic_natural_change/era5/SKILL.md) and [CAMS EAC4/forecasts](../../../data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md). Select methods for land use and other natural processes separately; this skill does not simulate them.

## Workflow

Define variables and scope → link acquisition methods → agree deduplication, mappings and units → select shared forecasting models and validation designs if needed → hand off activity, energy and technology interfaces.

See the [workflow and handoff guidance](../../../../harness/four-step-workflow.md).

## Boundaries

mlr3 and TimeXer are shared references; GCAM analyzes existing outputs only. This skill does not automatically train models or run scenarios.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.
