---
name: literature-workflow-methods
description: Guide cross-stage literature discovery, attachment review and import planning without executing collectors or modifying a library.
---

# Cross-stage literature workflow

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Define the topic → deduplicate DOI/title → check full-text and attachment sources → separate archiving, summaries and import plans → review evidence.

See the [method and handoff guidance](../../../../methods/shared/literature.md).

## Boundaries

An external collector's dry-run may access the network and write files. An import plan is not an actual library import. No run-tool adapter is provided.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.
