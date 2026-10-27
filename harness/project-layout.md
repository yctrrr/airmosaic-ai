# Project layout and migration

<!-- README-I18N:START -->

**English** | [中文](project-layout_ZH.md)

<!-- README-I18N:END -->

The five main areas are methods, skills, catalog, core and harness. Configuration templates and synthetic examples support them. No separate application, integration or packaging directory is introduced in this migration.

| Area | Responsibility | Authoritative content |
|---|---|---|
| `methods/` | Human-readable scientific reasoning, suitability, assumptions, provenance, uncertainty and quality rules | Method explanations and complete pathway narratives |
| `skills/` | Computer operations, software setup, parameters, reviewed scripts, failures and operational acceptance | Canonical English `SKILL.md`, Chinese translation and needed resources |
| `catalog/` | Shared capability declarations | Tool manifests; current dataset declarations and fallback behavior remain as documented |
| `core/` | Shared discovery, execution and development | Python package, installation metadata, tests and workflow-definition area |
| `harness/` | Installation, use, collaboration and behavior boundaries | General procedures and contribution rules |

Methods primarily address researchers and can also inform research-design agents. Skills link to scientific explanations instead of duplicating them. A skill may describe a manual operation; only a reviewed, enabled tool adapter executes through run-tool.

## Paths and ownership

| Previous location | Current location | Meaning |
|---|---|---|
| Top-level Python package source | `core/airmosaic_core/` | Same import package and public commands, without a `src/` intermediary |
| Top-level installation metadata and tests | `core/pyproject.toml`, `core/tests/` | One Python subproject |
| Previous workflow entry | [methods/pathways](../methods/pathways/README.md) | Human guidance, not a discovered skill or executable workflow |
| Previous stage declarations | `methods/pathways/references/stage-designs/` | Historical non-executable design references |
| Previous handoff reference | [handoff guide](usage/workflow-handoff.md) | Operational/manual acceptance and traceability |

The stage proposals are preserved for reference, including their historical alternatives. They are not automatic selection rules, executable definitions or validated scientific defaults. A new executable path would belong under `core/workflows/<pathway_id>/`, with a matching method narrative under `methods/pathways/`. [Core workflow status](../core/workflows/README.md) states what remains unimplemented.

## Installation

From the repository root:

```sh
python -m pip install -e './core[dev]'
python -m airmosaic_core.cli list-tools
python -m pytest core/tests -q -p no:cacheprovider
```

From `core/`, use `python -m pip install -e '.[dev]'` and `python -m pytest tests -q -p no:cacheprovider`. Existing environments need an editable reinstall after migration. Do not inject the previous source directory into Python's path. The source checkout is still required for catalog and specialist script resources; standalone distribution remains unimplemented.

## One definition, several interfaces

`catalog/tools/*.yaml` remains the only tool-registration source, with reviewed adapter policies enforced by the runner. CLI and future MCP interfaces must use the same registry/execution services. MCP is a transport and invocation layer, not a second catalog. A method link, skill installation or workflow file grants no execution permission.

Dataset acquisition declarations are still loaded from the existing skill `datasets.yaml` files, with `catalog/datasets/` used as the current detail fallback. This migration does not consolidate them or change dataset IDs. A future consolidation needs a separate behavior change and compatibility checks.

## Scope and boundaries

This migration changes locations, installation and references, preserving tool IDs, adapter support and scientific calculation code. MCP, orchestration, artifact registration and general scientific validation remain unimplemented. No stub executable is created for those capabilities.

The four research stages continue to organize content; cross-stage capabilities remain shared. Stage 02 contains conceptual methods only. Personal data/results, non-secret settings and authentication remain in the three separate roots outside Git. No original data or credentials are needed for migration checks. Historical private drafts and unrelated work are not included.

English uses the canonical filename; Chinese uses `_ZH.md`. Update both together. Long historical references retain their existing language. Follow the [authoring checklist](skill-authoring.md) and [storage contract](storage-and-credentials.md).

## Migration verification — 2026-10-27

The 144 existing tests and three added installed-CLI checks passed on Windows with Python 3.12. The added checks run discovery from the repository, `core/` and an external temporary directory. Two existing source-parser warnings remain. Installation uses the relocated editable project.

All 25 tool declarations retain their IDs and behavior; only nine core entrypoint paths change. Sixteen professional calculation sources and all 15 shared runtime files are byte-identical to the pre-migration baseline. Structured-file parsing, bilingual command/selector checks, path and mapping consistency, and a shared-file privacy scan passed. These checks used public code and synthetic inputs, without original data, credentials or real acquisition/model jobs.
