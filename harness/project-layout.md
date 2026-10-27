# Project layout and migration

<!-- README-I18N:START -->

**English** | [中文](project-layout_ZH.md)

<!-- README-I18N:END -->

The repository has one installable Python project at its root. The package is `airmosaic/`; public commands and registered tool IDs retain their names.

```text
airmosaic-ai-core/
├── pyproject.toml
├── airmosaic/
│   ├── cli.py
│   ├── mcp_server.py
│   └── services/
├── methods/
├── skills/
├── catalog/
├── workflows/
├── assets/
│   ├── data/<stage>/<dataset-name>/<version>/
│   └── results/<toy-project>/<reference-run>/<stage>/
├── config/examples/
└── harness/
    ├── checks/
    └── usage/
```

| Location | Responsibility |
|---|---|
| `methods/` | Human scientific reasoning, assumptions, quality criteria and pathway narratives |
| `skills/` | Computer operations, software preparation, parameters and operational checks |
| `catalog/` | Shared declarations; `tools/*.yaml` remains the only tool-registration source |
| `airmosaic/` | CLI, MCP transport and common execution/data services |
| `workflows/` | Executable pathway definition area; no workflow engine or runnable path is implemented |
| `assets/` | Public synthetic inputs and reference outputs only |
| `config/examples/` | Reusable non-secret parameter/project/path templates |
| `harness/` | Setup, collaboration, agent boundaries and automated checks |

```sh
python -m pip install -e '.[dev]'
python -m airmosaic.cli list-tools
python -m airmosaic.cli list-datasets
python -m pytest -q -p no:cacheprovider
```

## Migration map

The former wrapper directory is removed. Package code moved to `airmosaic/`, installation metadata to `pyproject.toml`, workflow definitions to `workflows/`, and checks to `harness/checks/`. Parameter examples moved to `config/examples/run-tool/`; the MCP connection check is `harness/checks/mcp_smoke.py`. There is no separate top-level tests or examples tree. Reinstall the editable project after migration; old module imports must be updated.

## Asset boundaries

Public [assets](../assets/README.md) are read-only manifest-listed toy fixtures. Actual data and generated results use a configured private `AIRMOSAIC_ASSETS_DIR` outside Git. Personal CONFIG_DIR and AUTH_DIR remain separate. The same data/result layout is used at the private root; there is no separate workspace mode or implicit old-cache fallback. [Asset rules](assets.md) define references and human review.

CLI and MCP share the same catalog and runner. No second registration list is added. The current data declarations remain in skill `datasets.yaml`, with catalog detail fallback; moving directories does not merge those definitions or create an asset-ID resolver. Scientific scripts and tool IDs are preserved. Source checkouts/editable installs remain required; standalone resource packaging is not implemented.

Keep four-stage navigation and shared capabilities, with stage 02 methods-only. New docs use canonical English and an `_ZH.md` sibling. See [authoring](skill-authoring.md), [runtime](usage/runtime.md) and [storage](storage-and-credentials.md).
