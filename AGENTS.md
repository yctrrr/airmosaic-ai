# AirMosaic AI — Agent Operating Guide

<!-- README-I18N:START -->

**English** | [中文](AGENTS_ZH.md)

<!-- README-I18N:END -->

See the [layout guide](harness/project-layout.md). Methods explain scientific reasoning, skills describe computer operations, workflows provide reusable data/skill combinations, and `projects/` organizes specific scientific questions and experiments with four-digit numbering. Core services own common execution. Shared scientific design lives in `methods/shared/`, combinations in `workflows/`, and studies in the [project index](projects/README.md). MCP reuses the catalog and runner; general cross-tool orchestration remains planned. See the [MCP guide](harness/usage/mcp.md).




Work from the repository root and read the relevant skill before changing or using its workflow. This file defines general operating rules. Concrete product names, dependencies and invocation details belong in skills and classified guides.

## Required boundaries

- Documentation and routine engineering checks use relevant descriptions, interfaces and synthetic inputs, not original data. Real-data acquisition, inspection or computation requires a bounded task. Stage 02 permits bounded synthetic calculations only in the explicitly declared and reviewed inventory skill; other conceptual entries do not imply computation. Real-data processing still requires a bounded task, and direct examples do not enable a stage-02 runner adapter.
- Respect requested objects, years, regions and operations. Continue necessary authorized reversible work without repeated permission requests; ask only for essential missing information or authorization.
- Inspect branch and working-tree changes first. Preserve originals, results and other contributors' work. A workflow description does not authorize bulk downloads, extra runs, installation, publication or messages.
- Never put private identities, passwords, keys, cookies, profiles, private hosts, signed URLs or machine-specific paths in shared artifacts. Report suspected secrets by location/category without repeating values.
- Separate project experimental results from reviewed assets. `AIRMOSAIC_ASSETS_DIR` remains an existing runtime compatibility setting, not evidence of asset approval. Keep non-secret settings in `AIRMOSAIC_CONFIG_DIR` and browser state in `AIRMOSAIC_AUTH_DIR`, with separate existing private roots outside Git. Credentials stay in a secret manager or an explicitly authorized official client's protected mechanism; do not inspect or export them.
- Keep external releases outside Git. Project results follow the project ownership convention and the selected adapter's currently supported output boundary. Local ignore rules do not grant write support. Generic demonstrations retain their reviewed exceptions. Do not migrate old outputs or copy sessions without specific authorization.
- Distinguish source review, synthetic/smoke checks, real-data integration and scientific validation. Do not report planned or skipped work as completed.
- Follow [agent boundaries](harness/agent-boundaries.md) and the [storage contract](harness/storage-and-credentials.md). These instructions do not establish OS isolation.

## Documentation map

Use the [four-step guide](harness/four-step-workflow.md), [skill navigation](skills/README.md) and [method mappings](methods/README.md). General rules stay capability-neutral; concrete entries live in category navigation and catalogs.

| Task | Guide |
|---|---|
| Organize experiments around a scientific question | [Numbered projects](projects/README.md) |
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

Use Python 3.10+ in a project environment, installed with `python -m pip install -e '.[dev]'`. Session roots are explicit; `.env` is not automatically loaded. Cache checks require a workspace variable or explicit SDK argument. CONFIG_DIR and AUTH_DIR are caller conventions, not automatic loaders.

```sh
python -m runtime.cli --help
python -m runtime.cli list-tools --format json
python -m runtime.cli describe-tool airmosaic_list_datasets
python -m runtime.cli check-tool airmosaic_list_datasets
python -m runtime.cli list-datasets
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
- Organize skills as `skills/<category>/<stage>/<capability>/`, using the same four stages and `shared` as methods. Maintain one home per capability and explicit method mappings.
- Keep general rules free of specific model/framework/category examples. Put concrete names, dependencies, identifiers and usage in the corresponding skills and classified navigation.
- Write English in the canonical filename and Chinese in an `_ZH.md` sibling, with one reciprocal selector. Update both together; preserve technical identifiers and executable commands. Do not claim untouched references were translated.
- Keep interface examples, metadata and actual implementations consistent. Documentation additions do not create executable tools.
- Maintain reusable provenance, uncertainty, normalization and quality rules in stage-specific `methods/` or `methods/shared/`; skills link the authoritative body. Operational references retain interface and verified-use details. Do not transfer source-specific quality thresholds to unrelated products.
- Use synthetic inputs for routine tests. Run relevant implementation checks when behavior changes; documentation-only edits do not require original-data or model execution. Live receipts stay local.
- Inspect diff, new files, logs and attachments for private information. Never bundle configuration/authentication directories with data.
- Commit and push only when the current task authorizes them, after relevant checks. Separate unrelated work and approved prerequisites; do not force-push or rewrite history. Roles and roadmaps do not grant authority.

## Data and project results

Experimental results belong to their [project](projects/README.md), which retains code, settings, evaluation and review records. Only a human scientific decision can admit selected outputs to `assets/`; internal asset organization is deferred. Current runners retain their existing external output contracts until project-directory support is implemented. Generic demonstration exceptions remain adapter-specific. Do not move historical outputs, bypass checks or infer approval from file presence. Configuration, authentication and credentials remain separate. See the [result and review contract](harness/assets.md).

Repository `assets/` permits manifest-listed, hash-verified synthetic inputs and explicitly publication-authorized, licensed public data snapshots. Keep published data in the separate public-data manifest with source and attribution; private data are not authorized by this exception. Current project-output compatibility locations remain outside Git and do not establish asset approval. A reviewed adapter may explicitly support local, Git-ignored skill results for generic demonstrations; never put private data there for publication. Supply project/stage context as required by the selected adapter. Reference private locations in personal configuration, never filesystem links; the old workspace mode is removed.

Project folders use four-digit display numbers; execution retains a stable `project_id` without that prefix. Project manifests provide explicit references, not runner parameters or new permissions. Keep scientific experiment records distinct from generic workflow demonstration checks.


## Synthetic workflow checks

An explicitly reviewed adapter additionally supports explicit `result_scope=workflow` (`--result-scope workflow` in the CLI). Only hash-verified manifest-listed repository synthetic CSVs are accepted. Outputs stay in Git-ignored `workflows/ml_regression/results/<timestamp>_<task>/`, with receipts/temp under `.airmosaic/<run_id>/` in that result root. Project IDs, real/external data, paths outside this fixed tree and nested repositories are rejected. The `auto` default is unchanged; scientific studies retain external project results. Reviewed workflow orchestration examples are reusable source; per-run generated code and design basis stay in the result's `gen_script/`, following the common handoff rules. This check provides neither scientific approval nor OS isolation.


Agent objectives/actions/observations, stop conditions and generation/event/retrospective records follow the [common execution and process-record contract](harness/usage/workflow-handoff.md). Each adapter must declare actual capture coverage; retrospective summaries do not replace observed events.
