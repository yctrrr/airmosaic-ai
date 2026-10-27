# 基础工具：安装、发现与本地检查

本页命令从仓库根目录运行。不同成员使用自己的虚拟环境；示例通过环境变量构造本机目录，不记录实际用户名或专用路径。

## 1. 安装核心环境

获取仓库后进入其根目录：

```sh
git clone https://github.com/yctrrr/airmosaic-ai.git
cd airmosaic-ai
```

Windows PowerShell，先确认 `python` 为 Python 3.10 或以上：

```powershell
python -m venv .venv
$amPython = (Resolve-Path ".venv/Scripts/python.exe").Path
& $amPython -m pip install -e "./core[dev]"
$amLocalRoot = Split-Path -Parent (Get-Location).Path
. ./config/examples/environment.ps1 -LocalRoot $amLocalRoot
foreach ($amDir in @($env:AIRMOSAIC_LOCAL_WORKSPACE, $env:AIRMOSAIC_CONFIG_DIR, $env:AIRMOSAIC_AUTH_DIR)) {
    New-Item -ItemType Directory -Force -Path $amDir | Out-Null
}
& $amPython -m airmosaic_core.cli --help
```

Linux/macOS，核心 Python 服务可按以下形式配置；领域脚本的跨平台支持需各自核验：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e './core[dev]'
export AIRMOSAIC_LOCAL_WORKSPACE="${XDG_DATA_HOME:-$HOME/.local/share}/airmosaic-ai/workspace"
export AIRMOSAIC_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/airmosaic-ai"
export AIRMOSAIC_AUTH_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/airmosaic-ai/auth"
mkdir -p "$AIRMOSAIC_LOCAL_WORKSPACE" "$AIRMOSAIC_CONFIG_DIR" "$AIRMOSAIC_AUTH_DIR"
chmod 700 "$AIRMOSAIC_AUTH_DIR"
.venv/bin/python -m airmosaic_core.cli --help
```

安装会访问包仓库并写入本地环境。`AIRMOSAIC_LOCAL_WORKSPACE` 也可由成员在自己的会话中设置为其他授权目录，须放在代码仓库外。新 shell 需要重新配置变量；复制 `.env.example` 不会自动加载配置。个人持久路径映射按[配置示例](../../config/examples/README.md)复制到仓库外，审查后显式加载。三类根的用途和各 skill 映射见[工作区与凭据](../storage-and-credentials.md)。

核心依赖为 PyYAML 和 jsonschema，开发依赖增加 pytest。pandas、R、Java/BaseX 和浏览器依赖按具体模块安装，不属于核心安装已经完成的事项。

工具入口、类别、依赖、认证和环境状态使用 `list-tools`、`describe-tool`、`check-tool`，详见[注册查询](tool-registry.md)。它们与下面的数据声明列表分别管理。

## 2. 查看和搜索数据声明

以下 PowerShell 示例沿用上一步的 `$amPython`：

```powershell
& $amPython -m airmosaic_core.cli list-datasets
& $amPython -m airmosaic_core.cli list-datasets --layer 01_socioeconomic_natural_change
& $amPython -m airmosaic_core.cli list-datasets --skill csmar
& $amPython -m airmosaic_core.cli list-datasets --domain health
& $amPython -m airmosaic_core.cli describe-dataset worldpop_population_grid
& $amPython -m airmosaic_core.cli search-datasets "population grid"
```

`list-datasets` 返回数据集 ID、名称、领域、层级、负责技能和仓库相对路径。它不包含所有模型技能，也不表示数据已下载。

`search-datasets` 在本地元数据中按空白拆词匹配，所有词都需命中；它不连接搜索引擎。使用声明中实际存在的关键词。

## 3. 检查本地缓存

```powershell
& $amPython -m airmosaic_core.cli check-availability worldpop_population_grid --pattern "raw/**/*.tif"
```

默认 `--pattern "*"` 只匹配缓存根的文件。WorldPop 通常将栅格放在 `raw/` 子目录，需选择合适的递归模式；不要把默认查询无结果解释为所有子目录都没有数据。

返回字段为 `dataset_id`、`cache_root`、`existing_files` 和 `missing_hint`。当前结果会显示本机实际路径，仅供本地查看。共享时转换为 `${AIRMOSAIC_LOCAL_WORKSPACE}` 下的逻辑路径，并检查文件名本身是否含敏感信息。

这个命令只检查匹配文件是否存在，不校验年份、文件内容、schema、校验和或科研适用性，也不自动下载文件。未知 ID 或必要配置缺失会报错；先查元数据和配置，不通过更换为任意私人路径来绕过。

## 4. 生成因果设计草案

```powershell
& $amPython -m airmosaic_core.cli draft-causal-plan --question "政策是否改变了研究区污染暴露？" --treatment "目标政策" --outcome "污染暴露" --unit "county-year"
```

返回研究问题、处理/结果变量、分析单元，以及候选混杂因素、识别策略、估计方法、反驳检验和说明。当前实现为固定结构的本地模板；不调用外部 LLM，不构造实际 DAG，也不验证识别假设。领域成员据实际数据完善设计。

## 5. Python SDK

在上面安装并配置好的 Python 环境中运行：

```python
from airmosaic_core.services import (
    CausalDesignService,
    DataAccessService,
    DataCatalogService,
)

catalog = DataCatalogService()
records = catalog.list_datasets(skill="worldpop")
metadata = catalog.describe_dataset("worldpop_population_grid")
matches = catalog.search_datasets("population grid")

access = DataAccessService(catalog=catalog)
availability = access.check_local_availability(
    "worldpop_population_grid", "raw/**/*.tif"
)
print({"dataset_id": availability.dataset_id,
       "matched_file_count": len(availability.existing_files)})

plan = CausalDesignService().draft_plan(
    question="Did the policy change exposure?",
    treatment="target policy",
    outcome="pollution exposure",
    unit="county-year",
).to_dict()
```

`DataAccessService` 可通过 `local_workspace=` 显式接收本地配置，否则读取 `AIRMOSAIC_LOCAL_WORKSPACE`；两者都缺失时拒绝继续。显式参数优先，不将实际配置写入公共示例。

`DataCatalogService` 还支持构造参数 `catalog_dir` 和 `data_acquisition_dir`；当前没有自动读取 `AIRMOSAIC_CATALOG_DIR` 的实现。

## 6. 调用失败时检查什么

| 情况 | 检查顺序 |
|---|---|
| 找不到 `airmosaic` | 使用安装时同一个解释器执行 `-m airmosaic_core.cli`，检查安装是否成功 |
| 找不到 Python 包 | 核对虚拟环境；不要把另一个 Python 的包目录写死到脚本 |
| 目录为空 | 核对真实 dataset ID、缓存根和递归模式；再检查实际文件 |
| 新声明未出现 | 核对 acquisition `datasets.yaml` 所在位置与字段 |
| 看到计划中的工具名称 | 查[工具清单](../tool-catalog.md)，使用存在的入口或报告待实现 |
| 需要发错误报告 | 分享命令参数类别、错误类别和脱敏日志，不复制完整环境变量或私人路径 |

## 7. 开发验证

```powershell
& $amPython -m pytest core/tests -q -p no:cacheprovider
```

核心测试主要覆盖目录和本地服务，不能替代数据连接器、模型计算或科学验收。验证报告说明实际运行了哪些命令、输入类型和限制，不把安装成功写成全平台已经验证。

## 统一执行

已审查的核心命令可通过 [run-tool](run-tool.md) 调用，先 dry-run，再按已有授权执行。该入口返回脱敏摘要和运行记录；原始查询命令仍可用于查看公共目录详情。
