# AirMosaic core

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

This Python subproject supplies shared discovery and controlled single-tool execution. Professional implementations remain in skill directories. The [repository layout](../harness/project-layout.md) separates human methods, operational skills, declarations and execution.

## Installation and checks

From the repository root, using the selected project interpreter:

```sh
python -m pip install -e './core[dev]'
python -m airmosaic_core.cli list-tools
python -m pytest core/tests -q -p no:cacheprovider
```

From this `core/` directory:

```sh
python -m pip install -e '.[dev]'
python -m airmosaic_core.cli list-tools
python -m pytest tests -q -p no:cacheprovider
```

Installation metadata is in `pyproject.toml`. `airmosaic_core/` is the importable package; there is no intervening `src/` directory. Modules still locate the repository catalog and skill resources relative to this checkout, independent of the caller's working directory. Supported use remains a full source checkout with editable installation; a standalone wheel does not include the repository's specialist resources.

## Implemented boundary

The CLI and SDK share the existing registry and runner. Tool IDs, adapter policies and scientific calculations are unchanged. Install optional dependencies only for the selected task. Follow the [execution guide](../harness/usage/run-tool.md) and [storage contract](../harness/storage-and-credentials.md) before using data or running tools.

MCP transport, workflow orchestration, an artifact-registration service and a general scientific validator are not implemented. [Workflow definitions](workflows/README.md) remain an explicitly reserved area, without executable path declarations. Tests use synthetic fixtures and do not establish scientific acceptance.
