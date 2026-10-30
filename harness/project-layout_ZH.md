# 项目布局与迁移

<!-- README-I18N:START -->

[English](project-layout.md) | **中文**

<!-- README-I18N:END -->

仓库顶层统一为一个可安装的 Python 项目。`runtime/` 保存公共运行服务及 CLI/MCP 接口，两种接口共用能力目录和执行器；公开命令和已注册工具编号保持不变。

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

| 位置 | 职责 |
|---|---|
| `methods/` | 面向人的科学解释、假设、质量标准和完整计算路径叙述 |
| `skills/` | 计算机操作、软件准备、参数和操作检查 |
| `catalog/` | 共用声明；`tools/*.yaml` 仍是唯一工具注册来源 |
| `runtime/` | CLI、MCP 通信与公共执行、数据服务 |
| `workflows/` | 可复用的数据与技能组合说明及交接契约 |
| `projects/` | 按四位编号组织科学问题、实验、生成结果、评价与审核 |
| `assets/` | 经人类审核的成果复用入口；内部组织后续完善 |
| `config/examples/` | 可复用的非秘密参数、项目和路径模板 |
| `harness/` | 安装、协作、代理边界和自动检查 |

```sh
python -m pip install -e '.[dev]'
python -m runtime.cli list-tools
python -m runtime.cli list-datasets
python -m pytest -q -p no:cacheprovider
```

## 迁移对应

移除原外层包装目录后，程序包位于 `runtime/`，安装信息位于顶层 `pyproject.toml`，工作流定义位于 `workflows/`，检查位于 `harness/checks/`。参数示例位于 `config/examples/run-tool/`，MCP 连接检查为 `harness/checks/mcp_smoke.py`，不再保留独立的顶层测试或示例树。

程序包改名后，使用 `python -m pip install -e '.[dev]'` 重新安装。Python 导入使用 `runtime`，模块入口为 `python -m runtime.cli` 和 `python -m runtime.mcp_server`。安装后的命令仍为 `airmosaic`、`airmosaic-mcp`，发行包名称仍为 `airmosaic-core`。已有 MCP 客户端配置需更新模块入口，参见[客户端示例](../config/examples/mcp-client.example.json)。

## 资产边界

项目保存实验结果与审核依据，选定成果经人类科学审核后才可纳入 `assets/`；本轮不设计资产内部结构。个人配置与认证继续独立并保留在私人位置。当前输出接口不变，见[结果与审核约定](assets_ZH.md)。

CLI 和 MCP 共用同一注册表与执行器，不新增第二套清单。数据声明继续使用技能内 `datasets.yaml`，目录详情保留现有回退；目录迁移不合并这些声明，也不产生资产编号解析器。科学脚本与工具编号保留。当前仍需完整源码及可编辑安装，独立资源发行尚未实现。

四步导航及跨阶段共享能力保留，第二步限于方法及其已明确声明的有界合成清单路径。新说明使用英文默认文件和 `_ZH.md` 中文版。参见[编写规范](skill-authoring_ZH.md)、[运行说明](usage/runtime_ZH.md)和[存储约定](storage-and-credentials_ZH.md)。

## 编号研究项目

[项目索引](../projects/README_ZH.md)使用 `0001_<topic>`、`0002_<topic>` 编排具体研究。展示编号与研究阶段、运行标识分开；稳定 `project_id` 不含编号，用于结果归集。公共目录保存可共享的研究设计和引用，实际数据、配置及结果保留原有私人根。工作流提供通用组合示范，项目确定具体科学问题、实验设计及验收依据。当前项目清单不自动加载或执行。

项目结果归属 `projects/<number_topic>/results/`，内部产物不采用固定模板。私人结果留在 Git 外，仓库本地项目结果被忽略。执行器尚未实现这一新目的地的直接写入支持：继续使用所选适配器已有的兼容位置并保留历史结果。见[项目说明](../projects/README_ZH.md)。

技能类别下只使用四个研究阶段及 `shared` 作为阶段目录，与 `methods/<stage>/` 对应。`methods/index.yaml` 显式连接方法与技能；跨阶段技能不按软件类别在阶段目录之外另建入口。具体能力清单由分类导航维护。

有明确主阶段的能力在该阶段维护，跨阶段使用通过引用实现；只有没有明确主阶段的通用能力才归 shared。

配置模板统一在 `config/examples/`，通用科学设计在 `methods/shared/`，数据与技能组合在 `workflows/`，具体案例与实验依据在对应 `projects/<number_topic>/`。方法库只保留阶段目录、共享方法及必要索引，不另设配置示例或平行路径目录。


## 工作流合成检查

显式合成工作流结果范围、输入限制与固定输出树统一见[资产规范](assets_ZH.md#工作流合成检查)；生成程序及过程记录见[统一交接规范](usage/workflow-handoff_ZH.md)。

## 维护与语言路径

项目维护归 `skills/agent_operations/shared/`，遵循[编写](skill-authoring_ZH.md)和[改进](skill-improvement_ZH.md)规范，不增加研究步骤或科学方法。机器学习操作统一归 `skills/model/shared/machine_learning_model/`，分别提供 `scripts/r/`、`scripts/python/` 及共享规划助手。既有回归与复现工作流保留名称。历史本地结果保留在原先忽略位置，不自动迁移结果。
