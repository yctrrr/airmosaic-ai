# Runtime, installation and checks

<!-- README-I18N:START -->

**English** | [中文](runtime_ZH.md)

<!-- README-I18N:END -->

The `runtime/` package implements the common CLI, MCP and execution services. Installation metadata is at the repository root. Tool IDs and specialist calculations are unchanged.

```sh
python -m pip install -e '.[dev]'
python -m runtime.cli list-tools
python -m runtime.cli list-datasets
python -m pytest -q -p no:cacheprovider
```

The installed commands are `airmosaic` and `airmosaic-mcp`. MCP needs the optional `mcp` extra; specialist adapters require their own declared dependencies. Only source checkouts and editable installs are currently supported. Discovery is independent of the caller's working directory.

Checks are maintained under `harness/checks/`; they verify interfaces, execution, privacy and synthetic behavior. Parameter examples are under `config/examples/`. They have different roles and are not duplicate test suites. The MCP connection check is `python harness/checks/mcp_smoke.py`.

See [layout](../project-layout.md), [run-tool](run-tool.md), [MCP](mcp.md), [toy walkthrough](toy-demo.md) and [assets](../assets.md). Workflow orchestration, automatic review/promotion and a general scientific validator remain unimplemented.
