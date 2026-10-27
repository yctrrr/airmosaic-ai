# AirMosaic AI — Agent Operating Guide

<!-- README-I18N:START -->

**English** | [中文](AGENTS_ZH.md)

<!-- README-I18N:END -->

Directory responsibilities and migration instructions are in the [layout guide](harness/project-layout.md). Methods address scientific reasoning; skills address computer operations; core owns shared execution. Path narratives and non-executable stage proposals live in `methods/pathways/`; future executable definitions belong in `core/workflows/`. No MCP or workflow engine is implemented.




Work from the repository root and read the relevant skill before changing or using its workflow. This file defines general operating rules. Concrete product names, dependencies and invocation details belong in skills and classified guides.

## Required boundaries

- Documentation and routine engineering checks use relevant descriptions, interfaces and synthetic inputs, not original data. Real-data acquisition, inspection or computation requires a bounded task. Stage 02 remains conceptual methods only, without concrete data, parameter values, implementation code, project script names or source fingerprints.
- Respect requested objects, years, regions and operations. Continue necessary authorized reversible work without repeated permission requests; ask only for essential missing information or authorization.
- Inspect branch and working-tree changes first. Preserve originals, results and other contributors' work. A workflow description does not authorize bulk downloads, extra runs, installation, publication or messages.
- Never put private identities, passwords, keys, cookies, profiles, private hosts, signed URLs or machine-specific paths in shared artifacts. Report suspected secrets by location/category without repeating values.
- Keep data/results in `AIRMOSAIC_LOCAL_WORKSPACE`, non-secret settings in `AIRMOSAIC_CONFIG_DIR` and browser state in `AIRMOSAIC_AUTH_DIR`. Roots must exist separately outside Git. Credentials belong in a secret manager or an explicitly authorized official client's protected existing mechanism; do not inspect or export them.
- Keep external releases outside Git. New artifacts use `output/<run_id>/<tool>/`. Do not migrate old outputs or copy sessions without specific authorization.
- Distinguish source review, synthetic/smoke checks, real-data integration and scientific validation. Do not report planned or skipped work as completed.
- Follow [agent boundaries](harness/agent-boundaries.md) and the [storage contract](harness/storage-and-credentials.md). These instructions do not establish OS isolation.

## Documentation map

Use the [four-step guide](harness/four-step-workflow.md), [skill navigation](skills/README.md) and [method mappings](methods/README.md). General rules stay capability-neutral; concrete entries live in category navigation and catalogs.

| Task | Guide |
|---|---|
| Team workflow and handoff | [Harness](harness/README.md) |
| Discover capabilities and readiness | [Catalog](harness/tool-catalog.md), [queries](harness/usage/tool-registry.md) |
| Execute a reviewed adapter | [run-tool](harness/usage/run-tool.md) |
| Prepare local roots | [Storage](harness/storage-and-credentials.md), [examples](config/examples/README.md) |
| Core services | [Core guide](harness/usage/core.md) |
| Acquisition or preparation | [Data acquisition](harness/usage/data-acquisition.md) |
| Existing-output analysis and templates | [Model analysis](harness/usage/model-analysis.md) |
| Reusable specialist workflows | [Category navigation](skills/model/README.md) |
| Author or register a capability | [Authoring](harness/skill-authoring.md), [registration](harness/tool-registration.md) |

General rules, skill entries and category navigation have English and Chinese versions. Historical specialist references may retain their existing language. Read only references relevant to the task.

## Environment and discovery

Use Python 3.10+ in a project environment, installed with `python -m pip install -e './core[dev]'`. Session roots are explicit; `.env` is not automatically loaded. Cache checks require a workspace variable or explicit SDK argument. CONFIG_DIR and AUTH_DIR are caller conventions, not automatic loaders.

```sh
python -m airmosaic_core.cli --help
python -m airmosaic_core.cli list-tools --format json
python -m airmosaic_core.cli describe-tool airmosaic_list_datasets
python -m airmosaic_core.cli check-tool airmosaic_list_datasets
python -m airmosaic_core.cli list-datasets
```

`list-datasets` reads acquisition declarations, not downloaded files. `check-availability` checks file presence, not contents or scientific validity; local paths in its output must be sanitized. Planning commands produce templates, not completed analysis. SDK services include `DataCatalogService`, `DataAccessService`, `CausalDesignService`, `ToolRegistryService` and `ToolRunnerService`.

Only canonical `SKILL.md` is the skill entry; its Chinese sibling is a translation. Host discovery needs an actual supported location/installation. `agents/openai.yaml` supplies display metadata, not executable registration. Preserve historical skill/dataset ID differences and inspect actual metadata instead of guessing from folder names.

`catalog/tools/*.yaml` is the tool-registration source. Read-only list/detail/check queries validate metadata and static prerequisites without running scripts, loading personal configuration or inspecting credentials. Unverified authentication or dependency states must remain explicit.

## Execution sequence

1. Define scope and select an implemented entry.
2. Check inputs, versions, dependencies, authentication requirements and destinations.
3. Verify units, years, spatial/time alignment, missingness and scientific assumptions before handoff.
4. Dry-run reviewed adapters, inspecting `can_execute` and `blockers`, then execute within authorization.
5. Check process state and expected artifact contents; record outcomes and unresolved limitations.
6. Review privacy before delivering a sanitized summary or performing authorized sharing.

Enabled adapters provide parameter/path preflight, fresh outputs, a minimal child environment and sanitized receipts. Network and existing-browser access require the declared authorization flags. Some dependency checks occur only during actual execution. Direct scripts do not inherit these protections; templates/references and unsupported chaining remain non-executable. The runner is a layer for trusted code, not an OS sandbox, credential broker or workflow orchestrator. See classified guides for exact behavior.

## Contribution checks

- Follow the [authoring checklist](harness/skill-authoring.md) and keep skill discovery, host display, datasets, method mappings and executable tools distinct.
- Keep general rules free of specific model/framework/category examples. Put concrete names, dependencies, identifiers and usage in the corresponding skills and classified navigation.
- Write English in the canonical filename and Chinese in an `_ZH.md` sibling, with one reciprocal selector. Update both together; preserve technical identifiers and executable commands. Do not claim untouched references were translated.
- Keep interface examples, metadata and actual implementations consistent. Documentation additions do not create executable tools.
- Maintain reusable provenance, uncertainty, normalization and quality rules in stage-specific `methods/` or `methods/shared/`; skills link the authoritative body. Operational references retain interface and verified-use details. Do not transfer source-specific quality thresholds to unrelated products.
- Use synthetic inputs for routine tests. Run relevant implementation checks when behavior changes; documentation-only edits do not require original-data or model execution. Live receipts stay local.
- Inspect diff, new files, logs and attachments for private information. Never bundle configuration/authentication directories with data.
- Commit and push only when the current task authorizes them, after relevant checks. Separate unrelated work and approved prerequisites; do not force-push or rewrite history. Roles and roadmaps do not grant authority.
