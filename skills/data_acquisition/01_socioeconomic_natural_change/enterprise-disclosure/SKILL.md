---
name: enterprise-disclosure-methods
description: Guide enterprise financial, annual-report and provincial environmental disclosure source selection and evidence validation. No collection adapter is registered here.
---

# Enterprise sources and disclosure methods

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Specify enterprises, periods and report types → distinguish listings, full text and attachments → design resumable queues and version IDs → check source evidence and coverage.

See the [method and handoff guidance](../../../../methods/01_socioeconomic_natural_change/enterprise_sources.md).

## Boundaries

Do not store enterprise-level records, authentication links or personal sessions in the shared library. The existing `csmar_process_company_info` handles only basic-information ZIP processing, not disclosure collection.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
