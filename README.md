# AirMosaic AI / 清空智枢

Atmospheric environment decision intelligence: reusable domain skills, data acquisition workflows, model-analysis templates and local Python services.

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

## Start here

Read the [Harness guide](harness/README.md) for team roles, execution steps, boundaries and validation. General rules and skill navigation have separate English and Chinese versions; historical specialist references retain their existing language.

| Goal | Documentation |
|---|---|
| Follow the four research steps and their current execution status | [Four-step guide](harness/four-step-workflow.md) |
| Install and call existing CLI/SDK services | [Core tools](harness/usage/core.md) |
| Acquire and prepare task-scoped data | [Data acquisition](harness/usage/data-acquisition.md) |
| Follow source-specific acquisition onboarding | [Source onboarding](harness/usage/copernicus-downloads.md) |
| Plan observation acquisition, preparation and quality checks | [Observation reference](skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) |
| Analyze existing results or adapt calculation templates | [Model analysis](harness/usage/model-analysis.md) |
| Use specialized methods and track reference projects | [Specialized workflows](skills/model/README.md) |
| Find reusable methods from recent local practice | [Methods library](methods/README.md) |
| Let an agent modify the project | [AGENTS.md](AGENTS.md), [agent boundaries](harness/agent-boundaries.md) |
| Run reviewed CLI/Python/R tools | [run-tool](harness/usage/run-tool.md) |
| Connect a local MCP client | [MCP installation, resources and execution grants](harness/usage/mcp.md) |
| Find available capabilities | [Registry queries](harness/usage/tool-registry.md), [tool catalog](harness/tool-catalog.md) |
| Separate data, personal configuration and authentication | [Storage and credentials](harness/storage-and-credentials.md) |
| Share data across stages and review project results for reuse | [Asset layout and review](harness/assets.md) |
| Add skills/tools and configure discovery/display | [Registration specification](harness/tool-registration.md) |

## Repository layout

```text
pyproject.toml            Installation and command entry points
airmosaic/                Runtime package: CLI, MCP and services
methods/                  Scientific methods and pathway narratives
skills/                   Operational skills and specialist scripts
catalog/                  Tool/data declarations and schemas
workflows/                Executable definitions; orchestration unimplemented
assets/                   Public toy data and reference results only
config/examples/          Public non-secret configuration and parameters
harness/                  Operating rules, usage and checks
  checks/                 Synthetic/interface/security checks
```

Actual data and generated outputs use the private, Git-external `AIRMOSAIC_ASSETS_DIR`; personal non-secret settings use `AIRMOSAIC_CONFIG_DIR`; browser sessions use `AIRMOSAIC_AUTH_DIR`. Keep all three roots outside Git checkouts and separate from each other. Passwords and tokens belong in a credential manager. Model releases and private notes also remain outside the repository. See the [environment example](config/examples/README.md) for explicit session setup.

## Workflow scope

See the bilingual [layout and migration guide](harness/project-layout.md) for directory responsibilities. [Pathway explanations](methods/pathways/README.md) describe research choices and handoffs; [core workflow status](workflows/README.md) identifies the unimplemented execution layer. Local stdio MCP is available through the [connection guide](harness/usage/mcp.md). Artifact registration and scientific validation services remain planned.

```text
Socioeconomic & natural change → emissions → atmospheric transport/chemistry → integrated impacts
```

These layers organize the research workflow, not a promise that every stage is executable. Select methods using suitable inputs, baselines and domain review; sample counts alone do not establish method suitability or scientific validity.

Operational mapping: [four-step workflow](harness/four-step-workflow.md), [skills](skills/README.md) and [methods](methods/README.md). Methods-only stages contain no concrete data or implementation code. Other stages reference shared capabilities instead of duplicating them. Check each entry's actual execution state and input contract; documentation maintenance uses descriptions, interfaces and synthetic inputs without reading original data.

## Quick start

From the repository root, with Python 3.10+:

```powershell
python -m venv .venv
$amPython = (Resolve-Path ".venv/Scripts/python.exe").Path
& $amPython -m pip install -e ".[dev]"
& $amPython -m airmosaic.cli --help
& $amPython -m airmosaic.cli list-datasets
& $amPython -m airmosaic.cli list-tools
& $amPython -m airmosaic.cli list-tools --category data_acquisition --format json
```

The [core guide](harness/usage/core.md) provides Windows and Linux/macOS configuration. Set `AIRMOSAIC_ASSETS_DIR` before cache checks or data work. `.env` is not loaded automatically. Optional model/browser dependencies must be configured separately. `AIRMOSAIC_CONFIG_DIR` and `AIRMOSAIC_AUTH_DIR` are caller conventions, not automatically loaded stores.

After configuring and creating all three separate roots, preview then run a local adapter:

```powershell
& $amPython -m airmosaic.cli run-tool airmosaic_list_datasets --project-id example_project --stage 01_socioeconomic_natural_change --dry-run
& $amPython -m airmosaic.cli run-tool airmosaic_list_datasets --project-id example_project --stage 01_socioeconomic_natural_change
```

## Current interfaces

The CLI provides dataset/cache/template commands plus `list-tools`, `describe-tool` and `check-tool`. The SDK also exports `ToolRegistryService` and `ToolRunnerService`. Tool queries support categories, skill/keyword/status filters, structured details and local prerequisite checks; see the [query guide](harness/usage/tool-registry.md).

Dataset listing reads acquisition skill declarations. Cache inspection only finds files; it does not validate contents or checksums. The causal-plan command returns a local template without calling an LLM or producing a causal estimate.

The registry validates `catalog/tools/*.yaml` and separates executable entries from templates/references. Queries do not execute tools, authenticate users or read credentials. Enabled adapters provide parameter checks, dry-run, path preflight and sanitized receipts as described in the [execution guide](harness/usage/run-tool.md). Check actual dependencies and authorization per task; a dry-run does not prove live execution. The runner is not an OS sandbox. Local MCP derives its tools from this catalog and preserves runner checks. Cross-tool orchestration and remote service interfaces remain unimplemented. Use real tool IDs and flat task JSON; unsupported workflows require manual preparation or separate adaptation.

## Skills and agents

Open the repository root and ask the agent to read `AGENTS.md`, locate the relevant skill and verify its actual entry point before running it. Skills may contain instructions, scripts, references, templates and examples.

`datasets.yaml` registers acquisition data declarations with the current catalog service. `agents/openai.yaml` is optional host metadata; it does not register an executable tool. Codex skill discovery requires a supported location or installation, as described in the [registration guide](harness/tool-registration.md).

## Contributing and privacy

Use the [skill authoring checklist](harness/skill-authoring.md) for bilingual entry points, content requirements and registration boundaries.

Contribute a bounded capability with documented inputs/outputs and validation cases. Follow the [contribution steps](harness/README.md) and [agent boundaries](harness/agent-boundaries.md). Keep private paths, usernames, credentials, authenticated browser state and real datasets out of shared artifacts. Report unrun validation explicitly.

## License

Apache-2.0; see [LICENSE](LICENSE).

## Data and project results

Follow the [asset contract](harness/assets.md). Shared data outside Git uses `assets/data/<stage>/<dataset-name>/<version>/` with actual dataset names. Projects reference fixed versions in configuration without cross-stage duplication. New results use `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`, with records and temporary files inside that run. New calls provide project and stage together. Compute/check, obtain human review, then register selected data in a fresh version; never overwrite originals or existing versions. Personal settings, authentication and credentials remain separate. Existing files are not migrated; automatic approval and registration services are not implemented.

Repository `assets/` publishes only declared synthetic inputs and reference results; see the [asset entry](assets/README.md). Start with the [toy walkthrough](harness/usage/toy-demo.md); its new results also go to the private root. The package is `airmosaic`; checks and parameter examples are maintained in `harness/checks/` and `config/examples/`.
