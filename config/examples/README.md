# 个人配置示例

这里只提交可公开复用的模板。实际配置复制到仓库外的 `${AIRMOSAIC_CONFIG_DIR}`，不得提交个人路径、账号、密码、token 或浏览器状态。

从仓库根目录开始，选定一个位于所有 Git 仓库之外的现有本地根目录。代码仓库可作为该目录的子目录。以下示例采用“仓库与 config/local_workspace/auth 并列”的布局：

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
foreach ($amDir in @($env:AIRMOSAIC_LOCAL_WORKSPACE, $env:AIRMOSAIC_CONFIG_DIR, $env:AIRMOSAIC_AUTH_DIR)) {
    New-Item -ItemType Directory -Force -Path $amDir | Out-Null
}
```

`environment.ps1` 仅设置当前 PowerShell 会话的三个路径变量，不创建目录、不连接网络、不读取凭据，也不修改系统级环境变量。它拒绝把 `LocalRoot` 设在 Git 仓库内部；不提供通用路径隔离或秘密存储。

新会话需再次加载已审查的个人配置。可以按已有授权在个人副本中设置 `GCAM_RELEASE_DIR` 等非秘密路径。不要让 agent 自动遍历、加载未知的个人脚本或扫描整个配置目录。

`AIRMOSAIC_LOCAL_WORKSPACE` 已由核心缓存服务读取。`AIRMOSAIC_CONFIG_DIR` 与 `AIRMOSAIC_AUTH_DIR` 是文档、配置示例和调用方共用的约定；核心服务不会自动加载其中的文件。当前 `.env`、YAML、JSON 中的变量也不会自动展开，需调用方显式处理。

Linux/macOS 可在自己的 shell 配置中显式设置这三个变量，详见[工作区与凭据管理](../../harness/storage-and-credentials.md)。
