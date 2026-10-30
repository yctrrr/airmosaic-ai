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

Project/stage requirements, result scopes and review/registration follow the [asset contract](../../harness/assets.md) and [execution guide](../../harness/usage/run-tool.md). The environment example selects roots only. [Asset/project/review templates](assets/README.md) describe manual records; [asset-paths.example.json](asset-paths.example.json) documents non-secret path fields and is not loaded automatically.

Regression task settings in `ml-regression/` include prediction and synthetic causal examples. Omit the project ID for a generic demonstration; supply it for a study and choose the supported layout within its project root. See the machine-learning classified guide for dependencies and operations.

The [direct synthetic regression parameters](run-tool/synthetic-regression.json) call the skill without workflow code. The [air-pollution prediction template](ml-regression/air-pollution-prediction.template.json) is schema-valid but has no associated dataset: adapt fields, units, coverage, split design, missingness and sample caps before use. Its settings are small computation examples, not validated scientific recommendations. Follow the skill's [operation contract](../../skills/model/shared/machine_learning_model/references/operations.md) and [domain cases](../../skills/model/shared/machine_learning_model/references/air-pollution.md).

[local-sources.example.yaml](local-sources.example.yaml) is an optional non-secret external-source mapping template, formerly kept in methods. Root fields are empty; the user completes and reviews a personal copy in CONFIG_DIR. The project does not automatically load it, scan source directories or read authentication. It is not run-tool parameters.

`run-tool/aq-bench-repository.json` reads the registered public repository snapshot. The existing AQ-Bench parameter file reads the byte-identical external copy. Published data and synthetic fixtures use separate input manifests; both remain read-only.

[model-reproduction/](model-reproduction/README.md) provides a sealed five-row synthetic comparison task and explicit fixture-generation instructions. Real comparisons select a personal CONFIG task and frozen external result snapshots; the reviewed direct script is not a registered execution tool.


The [synthetic workflow prediction task](ml-regression/workflow-synthetic.json) supports the [prompt-to-code check](../../workflows/ml_regression/examples/README.md), using only registered synthetic inputs and the explicit workflow result scope.
