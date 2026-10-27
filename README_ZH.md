# AirMosaic AI / 清空智枢

大气环境决策智能分析：可复用的领域技能、数据获取流程、模型分析模板和本地 Python 服务。

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

## 从这里开始

先阅读 [Harness 总体说明](harness/README_ZH.md)，了解成员分工、执行步骤、行为边界和验收方式。通用规范与技能导航分别提供中英文版本；历史专业参考资料保留现有语言。

| 目标 | 文档 |
|---|---|
| 按四个研究步骤查找入口、流程和执行状态 | [四步导航](harness/four-step-workflow.md) |
| 安装并调用现有 CLI/SDK | [基础工具](harness/usage/core.md) |
| 获取与整理限定范围的数据 | [数据获取](harness/usage/data-acquisition.md) |
| 按来源完成获取前的准备 | [来源操作指南](harness/usage/copernicus-downloads.md) |
| 规划观测资料获取、整理与质控 | [观测资料参考](skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL_ZH.md) |
| 分析已有结果或适配计算模板 | [模型分析](harness/usage/model-analysis.md) |
| 使用专项方法并跟踪参考项目 | [专项流程](skills/model/README_ZH.md) |
| 查找近期本地实践中的可复用方法 | [方法库](methods/README_ZH.md) |
| 让 agent 修改项目 | [AGENTS.md](AGENTS_ZH.md)、[Agent 行为边界](harness/agent-boundaries_ZH.md) |
| 连接本地 MCP 客户端 | [安装、资源与执行授权](harness/usage/mcp_ZH.md) |
| 查找可用能力 | [注册查询](harness/usage/tool-registry.md)、[工具清单](harness/tool-catalog.md) |
| 统一执行 CLI/Python/R 工具 | [run-tool](harness/usage/run-tool.md) |
| 分开管理数据、个人配置和认证状态 | [工作区与凭据](harness/storage-and-credentials_ZH.md) |
| 跨阶段共享数据、保存项目结果并复核入库 | [资产目录与复核规范](harness/assets_ZH.md) |
| 新增技能/工具并配置发现和展示 | [注册规范](harness/tool-registration_ZH.md) |

## 仓库结构

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

真实数据和新运行输出使用 Git 外私人资产根 `AIRMOSAIC_ASSETS_DIR`，个人非秘密配置使用 `AIRMOSAIC_CONFIG_DIR`，浏览器认证状态使用 `AIRMOSAIC_AUTH_DIR`。三类根分别设置，均位于 Git 仓库外。密码和 token 交由凭据管理器保管。模型发行包和私人记录也保留在仓库外。按[环境配置示例](config/examples/README.md)显式配置当前会话。

## 工作流范围

各目录职责及迁移方式见[布局说明](harness/project-layout_ZH.md)。[计算路径说明](methods/pathways/README_ZH.md)解释研究选择和交接，[核心工作流状态](workflows/README_ZH.md)说明尚未实现的执行层。本地标准输入输出 MCP 已可使用，见[连接指南](harness/usage/mcp_ZH.md)；产物登记和科学结果校验服务仍为规划能力。

```text
社会经济与自然变化 → 排放 → 大气输送与化学 → 综合影响评估
```

这四层组织研究流程，不表示每一步都有可执行服务。方法选择需要合适的输入、基线和领域审核；样本量不能单独证明方法适用性或科学有效性。

具体对应见[四步流程](harness/four-step-workflow.md)、[技能导航](skills/README_ZH.md)和[方法库](methods/README_ZH.md)。仅方法的阶段不提供具体数据或实现代码；其他阶段引用共享能力，不重复维护。逐项核对真实执行状态和输入契约。说明维护只使用文档、接口与合成输入，不读取原始数据。

## 快速启动

在仓库根目录使用 Python 3.10 或以上：

```powershell
python -m venv .venv
$amPython = (Resolve-Path ".venv/Scripts/python.exe").Path
& $amPython -m pip install -e ".[dev]"
& $amPython -m airmosaic.cli --help
& $amPython -m airmosaic.cli list-datasets
& $amPython -m airmosaic.cli list-tools
& $amPython -m airmosaic.cli list-tools --category data_acquisition --format json
```

[基础说明](harness/usage/core.md)提供 Windows 和 Linux/macOS 配置步骤。检查缓存或处理数据前设置 `AIRMOSAIC_ASSETS_DIR`。当前不会自动加载 `.env`；模型和浏览器依赖需要另行配置。`AIRMOSAIC_CONFIG_DIR` 与 `AIRMOSAIC_AUTH_DIR` 是调用方约定，不是自动加载的存储。

配置并创建三类独立根目录后，先预检，再运行本地适配器：

```powershell
& $amPython -m airmosaic.cli run-tool airmosaic_list_datasets --project-id example_project --stage 01_socioeconomic_natural_change --dry-run
& $amPython -m airmosaic.cli run-tool airmosaic_list_datasets --project-id example_project --stage 01_socioeconomic_natural_change
```

## 当前接口

CLI 提供数据目录、缓存和模板命令，并新增 `list-tools`、`describe-tool`、`check-tool`。SDK 同时导出 `ToolRegistryService` 和 `ToolRunnerService`。工具查询支持分类、skill/关键词/状态筛选、结构化详情和本机前置条件检查，详见[查询说明](harness/usage/tool-registry.md)。

数据列表读取 acquisition skill 的声明。缓存检查只查找文件，不验证内容或校验和。因果设计命令返回本地模板，不调用 LLM，也不生成因果估计结果。

注册加载器校验 `catalog/tools/*.yaml`，区分可执行入口与模板、参考。查询不执行工具、不登录、不读取凭据。已启用适配器按[执行指南](harness/usage/run-tool.md)提供参数检查、预检、路径前置检查与脱敏记录。依赖和授权按任务核对，预检不证明真实执行。执行器不是操作系统沙箱，本地 MCP 从同一目录派生接口并保留执行器检查，跨工具编排和远程服务接口仍未实现。使用真实工具编号与普通任务参数文件；不支持的流程需要人工准备或另行适配。

## Skills 与 agents

打开仓库根目录，让 agent 读取 `AGENTS.md`，查找相关 skill，并确认实际入口后再执行。技能可以包含说明、脚本、参考资料、模板和示例。

`datasets.yaml` 将数据获取声明登记到现有目录服务。`agents/openai.yaml` 是可选宿主元数据，不负责注册可执行工具。Codex 技能发现需要正确位置或安装步骤，详见[注册说明](harness/tool-registration_ZH.md)。

## 贡献与隐私

新增或修订技能按[编写规范](harness/skill-authoring_ZH.md)维护双语入口、最小内容要求及登记边界。

每次贡献围绕范围明确的一项能力，配套输入输出说明和验证案例。遵循[协作步骤](harness/README_ZH.md)及 [Agent 行为边界](harness/agent-boundaries_ZH.md)。共享内容不包含私人路径、账号名、凭据、已认证浏览器状态或真实数据；未执行的验证明确说明。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。

## 数据与项目结果

数据和项目结果按[资产规范](harness/assets_ZH.md)管理。Git 外共享 `assets/data/<stage>/<dataset-name>/<version>/`，数据目录使用实际名称；项目按配置引用固定版本，跨阶段不复制。新结果保存到 `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`，运行记录和临时文件留在该批次内。新调用同时提供项目和阶段。计算与检查 → 人工复核 → 将选定数据登记到新版本；不覆盖原始数据或既有版本。个人配置、认证及凭据继续独立管理。旧文件不迁移，自动审批和入库服务尚未实现。

仓库内 `assets/` 只公开清单声明的合成数据和参考结果，见[资产入口](assets/README_ZH.md)。可先按[合成演示](harness/usage/toy-demo_ZH.md)验证现有工具，演示的新结果同样写入私人资产根。源码包已统一为 `airmosaic`，检查和参数示例分别位于 `harness/checks/`、`config/examples/`。
