# AirMosaic AI / 清空智枢

Atmospheric environment decision intelligence: reusable domain skills, data acquisition workflows, model-analysis templates and local Python services.

[**中文**](README_ZH.md)

## Start here

Read the [Harness guide](harness/README.md) for team roles, execution steps, boundaries and validation. Shared detailed guides are currently in Chinese.

| Goal | Documentation |
|---|---|
| Install and call existing CLI/SDK services | [Core tools](harness/usage/core.md) |
| Acquire population, enterprise, yearbook or GBD data | [Data acquisition](harness/usage/data-acquisition.md) |
| Use GCAM scripts or health-impact templates | [Model analysis](harness/usage/model-analysis.md) |
| Let an agent modify the project | [AGENTS.md](AGENTS.md), [agent boundaries](harness/agent-boundaries.md) |
| Run reviewed CLI/Python tools | [run-tool](harness/usage/run-tool.md) |
| Find available capabilities | [Registry queries](harness/usage/tool-registry.md), [tool catalog](harness/tool-catalog.md) |
| Separate data, personal configuration and authentication | [Storage and credentials](harness/storage-and-credentials.md) |
| Add skills/tools and configure discovery/display | [Registration specification](harness/tool-registration.md) |

## Repository layout

```text
AGENTS.md                 Agent operating instructions
harness/                  Shared collaboration and tool-use documentation
catalog/                  Dataset metadata and schemas
config/examples/          Public templates for private environment configuration
workflow/                 Four-layer workflow design templates
skills/
  data_acquisition/       WorldPop, CSMAR, industrial yearbook, IHME GBD
  model/                  Health-impact templates and GCAM analysis skills
src/airmosaic_core/        Python CLI and service classes
tests/                    Core service tests
```

Data and runtime outputs use `AIRMOSAIC_LOCAL_WORKSPACE`; personal non-secret settings use `AIRMOSAIC_CONFIG_DIR`; browser sessions use `AIRMOSAIC_AUTH_DIR`. Keep all three roots outside Git checkouts and separate from each other. Passwords and tokens belong in a credential manager. Model releases and private notes also remain outside the repository. See the [environment example](config/examples/README.md) for explicit session setup.

## Workflow scope

```text
Socioeconomic drivers → emissions → atmospheric transport/chemistry → impacts
```

These layers organize the research workflow. They are not all implemented as executable services. Method selection requires suitable data, baselines and domain review; sample counts alone do not establish that an AI model or causal method is appropriate.

## Quick start

From the repository root, with Python 3.10+:

```powershell
python -m venv .venv
$amPython = (Resolve-Path ".venv/Scripts/python.exe").Path
& $amPython -m pip install -e ".[dev]"
& $amPython -m airmosaic_core.cli --help
& $amPython -m airmosaic_core.cli list-datasets
& $amPython -m airmosaic_core.cli list-tools
& $amPython -m airmosaic_core.cli list-tools --category data_acquisition --format json
```

The [core guide](harness/usage/core.md) provides Windows and Linux/macOS configuration. Set `AIRMOSAIC_LOCAL_WORKSPACE` before cache checks or data work. `.env` is not loaded automatically. Optional model/browser dependencies must be configured separately. `AIRMOSAIC_CONFIG_DIR` and `AIRMOSAIC_AUTH_DIR` are caller conventions, not automatically loaded stores.

After configuring and creating all three separate roots, preview then run a local adapter:

```powershell
& $amPython -m airmosaic_core.cli run-tool airmosaic_list_datasets --dry-run
& $amPython -m airmosaic_core.cli run-tool airmosaic_list_datasets
& $amPython -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run
```

## Current interfaces

The CLI provides dataset/cache/template commands plus `list-tools`, `describe-tool` and `check-tool`. The SDK also exports `ToolRegistryService` and `ToolRunnerService`. Tool queries support categories, skill/keyword/status filters, structured details and local prerequisite checks; see the [query guide](harness/usage/tool-registry.md).

Dataset listing reads acquisition skill declarations. Cache inspection only finds files; it does not validate contents or checksums. The causal-plan command returns a local template without calling an LLM or producing a causal estimate.

The registry loader validates `catalog/tools/*.yaml` against its schema and distinguishes executable entries from templates/references. Querying never runs scripts, logs in or reads credentials. Login and R-library status remain unverified without independent checks. The reviewed `run-tool` adapters support 8 core CLI commands and 6 Python scripts with parameter validation, dry-run, path preflight and sanitized receipts; see the [execution guide](harness/usage/run-tool.md). R/templates/references are not enabled. This is not an OS sandbox. MCP, REST and workflow orchestration remain planned. Symbolic names in old examples are not registered aliases.

## Skills and agents

Open the repository root and ask the agent to read `AGENTS.md`, locate the relevant skill and verify its actual entry point before running it. Skills may contain instructions, scripts, references, templates and examples.

`datasets.yaml` registers acquisition data declarations with the current catalog service. `agents/openai.yaml` is optional host metadata; it does not register an executable tool. Codex skill discovery requires a supported location or installation, as described in the [registration guide](harness/tool-registration.md).

## Contributing and privacy

Contribute a bounded capability with documented inputs/outputs and validation cases. Follow the [contribution steps](harness/README.md) and [agent boundaries](harness/agent-boundaries.md). Keep private paths, usernames, credentials, authenticated browser state and real datasets out of shared artifacts. Report unrun validation explicitly.

## License

Apache-2.0; see [LICENSE](LICENSE).
