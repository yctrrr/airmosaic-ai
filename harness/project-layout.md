# Project layout and migration

<!-- README-I18N:START -->

**English** | [中文](project-layout_ZH.md)

<!-- README-I18N:END -->

The repository has one installable Python project at its root. The `runtime/` package contains shared runtime services and the CLI/MCP interfaces. Both interfaces use the same capability catalog and runner; public commands and registered tool IDs retain their names.

```text
airmosaic-ai-core/
├── pyproject.toml
├── runtime/
│   ├── cli.py
│   ├── mcp_server.py
│   └── services/
├── methods/
├── skills/
│   ├── data_acquisition/<stage>/<capability>/
│   ├── model/<stage>/<capability>/
│   └── agent_operations/shared/<capability>/
├── catalog/
├── workflows/
├── projects/
├── assets/
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
| `runtime/` | CLI, MCP transport and common execution/data services |
| `workflows/` | Reusable data/skill combination descriptions and handoff contracts |
| `projects/` | Scientific questions, experiments, generated results, evaluation and review |
| `assets/` | Reuse of human-reviewed outputs; internal organization deferred |
| `config/examples/` | Reusable non-secret parameter/project/path templates |
| `harness/` | Setup, collaboration, agent boundaries and automated checks |

```sh
python -m pip install -e '.[dev]'
python -m runtime.cli list-tools
python -m runtime.cli list-datasets
python -m pytest -q -p no:cacheprovider
```

## Migration map

The former wrapper directory is removed. Package code lives in `runtime/`, installation metadata in `pyproject.toml`, workflow definitions in `workflows/`, and checks in `harness/checks/`. Parameter examples are in `config/examples/run-tool/`; the MCP connection check is `harness/checks/mcp_smoke.py`. There is no separate top-level tests or examples tree.

After the package rename, reinstall with `python -m pip install -e '.[dev]'`. Python imports use `runtime`; module entrypoints are `python -m runtime.cli` and `python -m runtime.mcp_server`. The installed commands remain `airmosaic` and `airmosaic-mcp`, and the distribution name remains `airmosaic-core`. Update existing MCP client configurations to the new module entrypoint; see the [client example](../config/examples/mcp-client.example.json).

## Asset boundaries

Project experiments retain their results and review evidence; selected outputs may enter `assets/` only after human scientific review. Asset internals are outside this revision. Personal settings and authentication remain separate and private. Current output interfaces are unchanged; see the [result and review contract](assets.md).

CLI and MCP share the same catalog and runner. No second registration list is added. The current data declarations remain in skill `datasets.yaml`, with catalog detail fallback; moving directories does not merge those definitions or create an asset-ID resolver. Scientific scripts and tool IDs are preserved. Source checkouts/editable installs remain required; standalone resource packaging is not implemented.

Keep four-stage navigation and shared capabilities, with stage 02 limited to methods and its explicitly declared bounded synthetic inventory route. New docs use canonical English and an `_ZH.md` sibling. See [authoring](skill-authoring.md), [runtime](usage/runtime.md) and [storage](storage-and-credentials.md).

## Numbered research projects

The [project index](../projects/README.md) uses `0001_<topic>`, `0002_<topic>` and so on for specific studies. Display numbers are separate from research stages and run identifiers; a stable `project_id` without the prefix groups results. Public folders hold shareable designs and references, with actual data, settings and results in the existing private roots. Workflows provide reusable combination examples; projects define the scientific question, experiment design and acceptance evidence. Project manifests are not automatically loaded or executed.

Project ownership uses `projects/<number_topic>/results/`, with no fixed internal artifact template. Private results remain outside Git; repository project results are ignored. Direct runner support for that new destination is not implemented: use the selected adapter's existing compatibility location and preserve historical outputs. See the [project guide](../projects/README.md).

Each skill category uses the four research stages and `shared`, corresponding to `methods/<stage>/`. `methods/index.yaml` connects methods to skills explicitly. Cross-stage skills do not add separate software-category roots outside that stage taxonomy; classified navigation maintains concrete entries.

Capabilities with a designated primary stage remain there and serve other stages through references. Shared is for general capabilities without a designated primary stage.

Configuration templates belong in `config/examples/`, shared scientific design in `methods/shared/`, data/skill combinations in `workflows/`, and specific cases and experimental evidence in the corresponding `projects/<number_topic>/`. Methods retain stage folders, shared explanations and necessary indexes, without separate configuration-example or parallel pathway directories.


## Synthetic workflow checks

The [asset contract](assets.md#synthetic-workflow-checks) is authoritative for the explicit synthetic workflow result scope, input restrictions and fixed output tree. The [common handoff contract](usage/workflow-handoff.md) defines generated programs and process records.

## Maintenance and language paths

Project maintenance lives in `skills/agent_operations/shared/`, governed by [authoring](skill-authoring.md) and [improvement](skill-improvement.md). It adds no research stage or scientific method. Machine-learning operations have one home in `skills/model/shared/machine_learning_model/`, with `scripts/r/`, `scripts/python/` and shared planning helpers. Existing regression and reproduction workflows keep their names. Historical local results stay at the previous ignored location; no automatic result migration is performed.
