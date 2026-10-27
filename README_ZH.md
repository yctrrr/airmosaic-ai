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
| 查找近期本地实践中的可复用方法 | [方法库](methods/README.md) |
| 让 agent 修改项目 | [AGENTS.md](AGENTS_ZH.md)、[Agent 行为边界](harness/agent-boundaries_ZH.md) |
| 查找可用能力 | [注册查询](harness/usage/tool-registry.md)、[工具清单](harness/tool-catalog.md) |
| 统一执行 CLI/Python/R 工具 | [run-tool](harness/usage/run-tool.md) |
| 分开管理数据、个人配置和认证状态 | [工作区与凭据](harness/storage-and-credentials_ZH.md) |
| 新增技能/工具并配置发现和展示 | [注册规范](harness/tool-registration_ZH.md) |

## 仓库结构

```text
AGENTS.md                 代理操作规则
harness/                  通用协作与使用说明
methods/                  四步方法与共享参考，不提供执行入口
catalog/                  数据和工具元数据及结构定义
config/examples/          通用配置示例
workflow/                 分阶段流程设计
skills/
  data_acquisition/       分步骤及共享的获取入口
  model/                  分步骤及共享的使用入口
src/airmosaic_core/        命令与服务实现
tests/                    合成及接口检查
```

数据和运行输出使用 `AIRMOSAIC_LOCAL_WORKSPACE`，个人非秘密配置使用 `AIRMOSAIC_CONFIG_DIR`，浏览器认证状态使用 `AIRMOSAIC_AUTH_DIR`。三类根分别设置，均位于 Git 仓库外。密码和 token 交由凭据管理器保管。模型发行包和私人记录也保留在仓库外。按[环境配置示例](config/examples/README.md)显式配置当前会话。

## 工作流范围

```text
社会经济与自然变化 → 排放 → 大气输送与化学 → 综合影响评估
```

这四层组织研究流程，不表示每一步都有可执行服务。方法选择需要合适的输入、基线和领域审核；样本量不能单独证明方法适用性或科学有效性。

具体对应见[四步流程](harness/four-step-workflow.md)、[技能导航](skills/README_ZH.md)和[方法库](methods/README.md)。仅方法的阶段不提供具体数据或实现代码；其他阶段引用共享能力，不重复维护。逐项核对真实执行状态和输入契约。说明维护只使用文档、接口与合成输入，不读取原始数据。

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
```

## 当前接口

CLI 提供数据目录、缓存和模板命令，并新增 `list-tools`、`describe-tool`、`check-tool`。SDK 同时导出 `ToolRegistryService` 和 `ToolRunnerService`。工具查询支持分类、skill/关键词/状态筛选、结构化详情和本机前置条件检查，详见[查询说明](harness/usage/tool-registry.md)。

数据列表读取 acquisition skill 的声明。缓存检查只查找文件，不验证内容或校验和。因果设计命令返回本地模板，不调用 LLM，也不生成因果估计结果。

注册加载器校验 `catalog/tools/*.yaml`，区分可执行入口与模板、参考。查询不执行工具、不登录、不读取凭据。已启用适配器按[执行指南](harness/usage/run-tool.md)提供参数检查、预检、路径前置检查与脱敏记录。依赖和授权按任务核对，预检不证明真实执行。执行器不是操作系统沙箱，跨工具编排及额外服务接口仍未实现。使用真实工具编号与普通任务参数文件；不支持的流程需要人工准备或另行适配。

## Skills 与 agents

打开仓库根目录，让 agent 读取 `AGENTS.md`，查找相关 skill，并确认实际入口后再执行。技能可以包含说明、脚本、参考资料、模板和示例。

`datasets.yaml` 将数据获取声明登记到现有目录服务。`agents/openai.yaml` 是可选宿主元数据，不负责注册可执行工具。Codex 技能发现需要正确位置或安装步骤，详见[注册说明](harness/tool-registration_ZH.md)。

## 贡献与隐私

新增或修订技能按[编写规范](harness/skill-authoring_ZH.md)维护双语入口、最小内容要求及登记边界。

每次贡献围绕范围明确的一项能力，配套输入输出说明和验证案例。遵循[协作步骤](harness/README_ZH.md)及 [Agent 行为边界](harness/agent-boundaries_ZH.md)。共享内容不包含私人路径、账号名、凭据、已认证浏览器状态或真实数据；未执行的验证明确说明。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
