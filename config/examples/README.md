# Personal configuration examples

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

Only reusable public templates belong here. Copy reviewed settings to CONFIG_DIR outside Git; never commit personal paths, accounts, passwords, tokens or authenticated browser state.

From the repository root, select an existing local root outside every Git checkout. The source checkout may be its child. This example places the checkout beside assets/config/auth:

```powershell
$amLocalRoot = Split-Path -Parent (Get-Location).Path
$amConfigDir = Join-Path $amLocalRoot "config"
New-Item -ItemType Directory -Force -Path $amConfigDir | Out-Null
$amPersonalConfig = Join-Path $amConfigDir "environment.ps1"
if (-not (Test-Path -LiteralPath $amPersonalConfig)) {
    Copy-Item -LiteralPath "config/examples/environment.ps1" -Destination $amPersonalConfig
}
# Review the personal file before dot-sourcing it; PowerShell config is executable code.
. $amPersonalConfig -LocalRoot $amLocalRoot
foreach ($amDir in @($env:AIRMOSAIC_ASSETS_DIR, $env:AIRMOSAIC_CONFIG_DIR, $env:AIRMOSAIC_AUTH_DIR)) {
    New-Item -ItemType Directory -Force -Path $amDir | Out-Null
}
```

`environment.ps1` sets three variables in the current session. It selects the sibling `assets/` workspace and separate `config/` and `auth/` roots. It does not create directories, use the network, read credentials or change system settings. It rejects LocalRoot inside Git; it is not an OS sandbox or secret store.

Review and explicitly load the personal copy in each new session. Add only authorized non-secret resource mappings to that copy. Do not scan/load unknown personal scripts or rewrite existing configuration. The example leaves old workspaces and outputs in place.

The core reads AIRMOSAIC_ASSETS_DIR. CONFIG_DIR and AUTH_DIR are explicit caller conventions, not automatic configuration loaders. `.env` is not automatically loaded. Supported runner path parameters expand only `${AIRMOSAIC_ASSETS_DIR}`; shell expressions and other variables are not expanded.

For Linux/macOS, explicitly set the same three separate roots using the [storage contract](../../harness/storage-and-credentials.md).

The `copernicus/` directory contains non-secret request examples. Copy only the selected request to private settings, preserve existing files and verify the source form. They are manual API request examples, not run-tool parameters or credential configuration; see the [classified guide](../../harness/usage/copernicus-downloads.md).

The runner requires three existing, separate roots. It reads only the explicitly supplied non-secret JSON via `--params-file`, not an entire personal directory. Public tool parameters are in [config/examples/run-tool](run-tool); see [execution](../../harness/usage/run-tool.md).

`mcp-client.example.json` is a generic client template. Adapt its interpreter and existing roots in a personal copy. It does not grant execution, network or browser access, contain credentials, or load itself. See [MCP setup](../../harness/usage/mcp.md).

New tasks supply both `--project-id` and `--stage` under the [asset contract](../../harness/assets.md). The environment example selects roots, not a project. [Asset/project/review templates](assets/README.md) describe the manual process. Actual project settings stay in CONFIG_DIR; results and review records stay in assets/results.

The public repository assets directory is distinct from the private root selected outside Git by this helper. Public fixtures are read-only. Actual data and every generated result use AIRMOSAIC_ASSETS_DIR; customize its location only in the personal configuration copy. The [path mapping template](asset-paths.example.json) documents the fields; JSON is not automatically loaded.
