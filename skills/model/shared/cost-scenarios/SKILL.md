---
name: cost-scenario-methods
description: Guide cross-stage control-cost and distributional scenario boundaries and handoff review. No executable pipeline.
---

# Cross-stage cost and distribution methods

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Define resource costs and transfer payments → specify price basis and units → distinguish historical and incremental components → review same-generation handoffs, eligibility and budgets → design paired-scenario acceptance.

See the [method and handoff guidance](../../../../methods/shared/cost_scenarios.md).

## Boundaries

Methods only. Do not launch external pipelines or jobs or provide inventory implementations. Identity information does not establish cost incidence or physical eligibility.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
