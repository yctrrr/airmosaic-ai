# AirMosaic AI / 清空智枢

大气环境决策智能分析：可复用的领域技能、数据获取流程、模型分析模板和本地 Python 服务。

[**English**](README.md)

## 从这里开始

先阅读 [Harness 总体说明](harness/README.md)，了解成员分工、执行步骤、行为边界和验收方式。共享的详细说明目前以中文编写。

| 目标 | 文档 |
|---|---|
| 安装并调用现有 CLI/SDK | [基础工具](harness/usage/core.md) |
| 获取人口、企业、年鉴或 GBD 数据 | [数据获取](harness/usage/data-acquisition.md) |
| 使用 GCAM 脚本或健康影响模板 | [模型分析](harness/usage/model-analysis.md) |
| 让 agent 修改项目 | [AGENTS.md](AGENTS.md)、[Agent 行为边界](harness/agent-boundaries.md) |
| 查找可用能力 | [注册查询](harness/usage/tool-registry.md)、[工具清单](harness/tool-catalog.md) |
| 统一执行 CLI/Python 工具 | [run-tool](harness/usage/run-tool.md) |
| 分开管理数据、个人配置和认证状态 | [工作区与凭据](harness/storage-and-credentials.md) |
| 新增技能/工具并配置发现和展示 | [注册规范](harness/tool-registration.md) |

## 仓库结构

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

数据和运行输出使用 `AIRMOSAIC_LOCAL_WORKSPACE`，个人非秘密配置使用 `AIRMOSAIC_CONFIG_DIR`，浏览器认证状态使用 `AIRMOSAIC_AUTH_DIR`。三类根分别设置，均位于 Git 仓库外。密码和 token 交由凭据管理器保管。模型发行包和私人记录也保留在仓库外。按[环境配置示例](config/examples/README.md)显式配置当前会话。

## 工作流范围

```text
Socioeconomic drivers → emissions → atmospheric transport/chemistry → impacts
```

这四层组织了社会经济、排放、大气输送/化学和影响研究流程；并非每一层都已实现为可执行服务。方法选择需要数据适用性、基线和领域审核，不能仅由样本数量判断 AI 或因果方法是否适用。

## 快速启动

在仓库根目录使用 Python 3.10 或以上：

```powershell
python -m venv .venv
$amPython = (Resolve-Path ".venv/Scripts/python.exe").Path
& $amPython -m pip install -e ".[dev]"
& $amPython -m airmosaic_core.cli --help
& $amPython -m airmosaic_core.cli list-datasets
& $amPython -m airmosaic_core.cli list-tools
& $amPython -m airmosaic_core.cli list-tools --category data_acquisition --format json
```

[基础说明](harness/usage/core.md)提供 Windows 和 Linux/macOS 配置步骤。检查缓存或处理数据前设置 `AIRMOSAIC_LOCAL_WORKSPACE`。当前不会自动加载 `.env`；模型和浏览器依赖需要另行配置。`AIRMOSAIC_CONFIG_DIR` 与 `AIRMOSAIC_AUTH_DIR` 是调用方约定，不是自动加载的存储。

配置并创建三类独立根目录后，先预检，再运行本地适配器：

```powershell
& $amPython -m airmosaic_core.cli run-tool airmosaic_list_datasets --dry-run
& $amPython -m airmosaic_core.cli run-tool airmosaic_list_datasets
& $amPython -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run
```

## 当前接口

CLI 提供数据目录、缓存和模板命令，并新增 `list-tools`、`describe-tool`、`check-tool`。SDK 同时导出 `ToolRegistryService` 和 `ToolRunnerService`。工具查询支持分类、skill/关键词/状态筛选、结构化详情和本机前置条件检查，详见[查询说明](harness/usage/tool-registry.md)。

数据列表读取 acquisition skill 的声明。缓存检查只查找文件，不验证内容或校验和。因果设计命令返回本地模板，不调用 LLM，也不生成因果估计结果。

注册加载器已按 schema 校验 `catalog/tools/*.yaml`，并区分可执行入口与模板/参考资料。查询不运行脚本、不登录、不读取凭据；登录与 R 包状态仍需独立核验。已实现的 `run-tool` 适配器支持 8 个核心 CLI 和 6 个 Python 脚本，提供参数校验、dry-run、路径前置检查及脱敏记录，见[执行指南](harness/usage/run-tool.md)。R、模板和参考资料不能通过它运行；它不是 OS 沙箱。MCP、REST 和工作流编排器仍待实现。旧示例中的名称不是自动注册的别名。

## Skills 与 agents

打开仓库根目录，让 agent 读取 `AGENTS.md`，查找相关 skill，并确认实际入口后再执行。技能可以包含说明、脚本、参考资料、模板和示例。

`datasets.yaml` 将数据获取声明登记到现有目录服务。`agents/openai.yaml` 是可选宿主元数据，不负责注册可执行工具。Codex 技能发现需要正确位置或安装步骤，详见[注册说明](harness/tool-registration.md)。

## 贡献与隐私

每次贡献围绕范围明确的一项能力，配套输入输出说明和验证案例。遵循[协作步骤](harness/README.md)及 [Agent 行为边界](harness/agent-boundaries.md)。共享内容不包含私人路径、账号名、凭据、已认证浏览器状态或真实数据；未执行的验证明确说明。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
