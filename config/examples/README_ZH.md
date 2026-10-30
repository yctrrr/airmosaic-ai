# 个人配置示例

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

这里只提交可公开复用的模板。实际配置复制到仓库外的 `${AIRMOSAIC_CONFIG_DIR}`，不得提交个人路径、账号、密码、token 或浏览器状态。

从仓库根目录开始，选定一个位于所有 Git 仓库之外的现有本地根目录。代码仓库可作为该目录的子目录。以下示例采用“仓库与 assets/config/auth 并列”的布局：

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

`environment.ps1` 仅设置当前 PowerShell 会话的三个路径变量，不创建目录、不连接网络、不读取凭据，也不修改系统级环境变量。它拒绝把 `LocalRoot` 设在 Git 仓库内部；不提供通用路径隔离或秘密存储。

新会话需再次加载已审查的个人配置。可以按已有授权在个人副本中设置 `GCAM_RELEASE_DIR` 等非秘密路径。不要让 agent 自动遍历、加载未知的个人脚本或扫描整个配置目录。

`AIRMOSAIC_ASSETS_DIR` 已由核心缓存服务读取。`AIRMOSAIC_CONFIG_DIR` 与 `AIRMOSAIC_AUTH_DIR` 是文档、配置示例和调用方共用的约定；核心服务不会自动加载其中的文件。当前 `.env`、YAML、JSON 中的变量也不会自动展开，需调用方显式处理。

Linux/macOS 可在自己的 shell 配置中显式设置这三个变量，详见[工作区与凭据管理](../../harness/storage-and-credentials_ZH.md)。

`copernicus/` 提供 ERA5 单层、CAMS EAC4 和 CAMS 预报的非秘密请求 JSON。只将选中的文件复制到个人 `CONFIG_DIR/copernicus/`，保留现有配置并按当前门户表单核对。这些是官方 API 的 request 示例，不是 run-tool 参数；不包含令牌或自动配置凭据的逻辑。使用步骤见 [Copernicus 下载指南](../../harness/usage/copernicus-downloads.md)。

`run-tool` 要求三类根目录均已存在且互不包含。它不会自动加载个人环境脚本，仅显式读取 `--params-file` 指定的非秘密 JSON；该路径可以在 CONFIG_DIR。路径参数只展开 `${AIRMOSAIC_ASSETS_DIR}`，不展开 shell 表达式或其他环境变量。公共参数示例位于 `config/examples/run-tool/`，完整步骤见[执行说明](../../harness/usage/run-tool.md)。

`mcp-client.example.json` 是兼容客户端的通用连接模板，需在个人副本中替换解释器与三个已存在根目录，并按客户端格式调整。默认只读查询或预检，不授予实际执行、联网或浏览器权限；不放凭据，不会自动加载此配置。安装和授权见[MCP 指南](../../harness/usage/mcp_ZH.md)。

项目与阶段要求、结果范围及复核入库统一见[资产规范](../../harness/assets_ZH.md)和[执行说明](../../harness/usage/run-tool.md)。环境示例只设置根目录。[assets/ 模板](assets/README_ZH.md)提供人工记录；[asset-paths.example.json](asset-paths.example.json)说明非秘密路径字段，不会自动加载。

回归任务配置位于 `ml-regression/`，分别提供预测与合成因果示例。通用演示省略项目编号；具体研究提供项目编号，在项目根内自选结果布局。依赖与操作见机器学习分类说明。

[直接合成回归参数](run-tool/synthetic-regression.json)不依赖工作流代码即可调用技能。[空气污染预测模板](ml-regression/air-pollution-prediction.template.json)通过任务结构验证，但没有配套数据；使用前适配字段、单位、完整性、划分、缺失与样本上限。参数是小规模计算示例，不是经过科学验证的推荐值。具体操作见技能的[操作契约](../../skills/model/shared/machine_learning_model/references/operations_ZH.md)与[领域特例](../../skills/model/shared/machine_learning_model/references/air-pollution_ZH.md)。

[local-sources.example.yaml](local-sources.example.yaml) 是可选的非秘密外部来源映射模板，原位于方法库。所有根字段为空，个人副本由用户在 CONFIG_DIR 填写并审查；项目不会自动加载该文件、扫描来源目录或读取认证信息。它不是 run-tool 参数。

`run-tool/aq-bench-repository.json` 读取仓库内已登记的公开副本，原有 AQ-Bench 参数文件读取字节一致的外部副本。公开数据与合成示例分别登记，两者均只读。

[model-reproduction/](model-reproduction/README_ZH.md) 提供两侧各五行的冻结合成比较任务及显式生成步骤。真实比较选择个人 CONFIG 任务和已冻结外部结果；经过审查的直接脚本不等于已注册执行工具。


[工作流合成预测任务](ml-regression/workflow-synthetic.json)用于[生成代码与测试示例](../../workflows/ml_regression/examples/README_ZH.md)，仅使用登记的合成输入及显式工作流结果范围。
