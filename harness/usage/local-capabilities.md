# Local private capabilities

**English** | [中文](local-capabilities_ZH.md)

Complete provider-specific methods, instructions, scripts and templates can remain in a separate local directory. No private GitHub repository, upload or network connection is required. The public checkout retains summaries and stable identifiers.

## Storage and explicit selection

Keep the private package outside the public checkout, separate from data, results, personal configuration and authentication. Its `methods/` and `skills/` use the same research-stage layout as the public project. `capabilities.json` declares its finite file inventory; `catalog/local-capabilities.json` in the public source defines the reserved slots. Only those files can be selected; this is not an arbitrary plugin importer.

Create a non-secret JSON mapping in the member's external configuration directory, using an absolute local directory for `root`:

```json
{"schema_version": 1, "root": "<absolute local private capability directory>"}
```

The placeholder must be replaced locally. No mapping, password, token, cookie or private filesystem location belongs in Git. The configuration is read only when explicitly passed; setting CONFIG_DIR alone does not load it. No credential or browser profile is inspected by capability selection.

From the installed public source environment:

```powershell
python -m runtime.cli list-tools --skill csmar-downloader
python -m runtime.cli --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json" list-tools --skill csmar-downloader
python -m runtime.cli --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json" describe-capability skill csmar-downloader
python -m runtime.cli --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json" validate-capabilities
```

Place the global option before the command. SDK callers can pass `local_config` to `ToolRegistryService`, then supply that registry to the capability catalog, runner or MCP gateway. Full task parameters and operating examples belong to the selected private skill.

## Readiness and execution

Without selection, the four reserved tool IDs report `private_extension_required` and cannot run. Selection preserves their actual state: the existing local processor has its reviewed execution adapter; browser acquisition remains a reference; yearbook operations remain templates requiring adaptation. No download adapter or new calculation logic is created.

The selected registry resolves declared source files under the private root while inputs, outputs and receipts retain the runner's existing separated-root contracts. Missing files, invalid mappings and escaped paths fail closed. Configuration values and absolute private paths are excluded from registry responses. Local code remains trusted code under the caller's OS identity; this does not isolate other same-user processes.

## MCP

Start a separate local instance for authorized private use:

```powershell
python -m runtime.mcp_server --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json"
```

The flag is a startup choice; MCP callers cannot supply a new root in a tool call. Default execution remains dry-run, and existing execution/network/session grants remain required. This instance serves selected private documentation to its connected client: connect only authorized clients. A server started without the flag serves public summaries. No remote MCP deployment or authentication broker is added.

## Sharing boundary

Keep the private directory and actual mapping outside every public checkout, export and release artifact. Licensed data and authentication stay separate even when source is private. Moving current files out of the public tree does not remove old Git history; no history rewrite or publication is performed by this setup.
