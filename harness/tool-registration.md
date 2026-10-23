# 技能、数据集与工具的注册和展示

本规范定义 AirMosaic 的协作约定和实现要求。已实现核心 CLI、Python 服务、数据声明扫描、工具注册查询及有限适配器 [run-tool](usage/run-tool.md)。安装器、工具面板和 MCP 适配器尚未实现。

## 1. 四种登记对象分别管理

| 对象 | 标识与声明位置 | 谁读取 | 登记后的实际效果 |
|---|---|---|---|
| Skill | `SKILL.md` 的 `name`、`description` | Agent 或宿主技能发现机制 | 让 agent 找到专业流程 |
| 宿主展示元数据 | skill 内 `agents/openai.yaml` | 支持该格式的宿主 | 配置名称、提示词、依赖等；不创建可执行函数 |
| Dataset | acquisition skill 内 `datasets.yaml` 的 `dataset_id` | `DataCatalogService` | 出现在 `list-datasets`；不自动下载或校验数据 |
| Tool | `catalog/tools/*.yaml` | `ToolRegistryService` 和工具查询 CLI | 校验并展示实际入口；不自动执行或注册为 MCP 工具 |

Workflow YAML 和请求示例属于流程/参数说明。它们不能代替处理函数、安装步骤或 MCP 注册。

## 2. 标识规则与现有映射

新 skill 使用稳定的英文小写连字符名称，工具使用稳定的英文小写下划线名称；人类可读标题可以使用中文。名称不能包含个人账号、机器名、绝对路径或凭据。

现有标识有历史差异，调用时使用以下准确值，不按目录名猜测：

| 目录或能力 | `SKILL.md name` | `datasets.yaml skill_id` |
|---|---|---|
| WorldPop | `worldpop` | `worldpop` |
| CSMAR | `csmar-downloader` | `csmar` |
| 工业年鉴 | `ind-yearbook` | `ind_yearbook` |
| IHME GBD | `ihme-gbd-results` | `ihme-gbd-results` |
| 健康影响 | `health-impact-analysis` | 无数据获取登记 |
| GCAM 总入口 | `gcam` | 无数据获取登记 |
| GCAM 输出结构 | `gcam-output-structure` | 无数据获取登记 |
| GCAM 配置 | `gcam-configuration` | 无数据获取登记 |
| GCAM 提取 | `gcam-data-extraction` | 无数据获取登记 |

因此 `airmosaic list-datasets --skill csmar` 使用数据目录的 ID；宿主中选择技能则使用其实际名称。后续统一标识时保留明确别名和迁移记录。

`population`、`worldpop`、`gdp`、`health`、`gbd`、`mortality`、`ind_yearbook` 是当前代码中的部分数据集别名。尤其 `gdp` 当前解析到工业年鉴地区行业指标，并不表示已经有完整 GDP 数据，必须检查实际元数据及字段。

## 3. 新增 skill 的步骤

1. 选择现有领域目录，定义一个可独立描述的任务及其范围。
2. 编写 `SKILL.md`：frontmatter 包含 `name` 和 `description`，正文写输入输出、步骤、条件、失败处理和验证要求。
3. 方法资料放 `references/`，确定性动作放 `scripts/`，需适配的代码放 `templates/`，示例使用合成值或通用变量。
4. 需要宿主展示时添加 `agents/openai.yaml`。它是可选宿主元数据，不是 AirMosaic 的执行注册表。
5. 涉及数据获取时按下一节添加 `datasets.yaml`；纯分析 skill 不为出现在列表中而虚构数据集。
6. 在[工具清单](tool-catalog.md)中注明真实入口、状态、条件和分类说明链接。
7. 验证实际发现、调用和失败案例，检查私人信息后提交审核。

独立分发 skill 时，检查跨目录引用是否随包提供。指向本仓库 `harness/` 的导航链接不能假定在单独复制的技能包中仍然有效；应一并提供所需说明，或改为指向对应版本的公开仓库文档。

标准技能结构示意：

```text
<skill-directory>/
  SKILL.md
  agents/openai.yaml       可选：宿主展示信息
  datasets.yaml           仅数据获取/处理能力需要
  scripts/                可选：确定性工具
  templates/              可选：需适配的模板
  references/             方法与来源
  examples/               通用参数与任务示例
```

## 4. 数据集登记步骤

1. 在负责 acquisition skill 的目录中写 `datasets.yaml`，声明 `skill_id`、`layer`、`skill_path`。
2. 每条记录至少提供当前服务所需的 `dataset_id`、`name`、`domain`、`description`，并明确 `access_mode`、来源、覆盖范围及缓存根。
3. `skill_path` 使用仓库相对路径，缓存根使用 `${AIRMOSAIC_LOCAL_WORKSPACE}`。不要提交实际缓存清单、账户信息或私有地址。
4. 运行 `list-datasets`、`describe-dataset` 和相关筛选，检查新记录和来源路径。
5. 审核 ID 全局唯一、引用存在、字段合法。当前加载器不自动完成完整 JSON Schema 校验或重复 ID 拒绝，需补充验证后才能称为自动约束。

`catalog/datasets/` 当前还用于详情查询的后备查找。`list-datasets` 的主要来源是 acquisition skill 中的声明；仅添加 `catalog/datasets/*.yaml` 不保证出现在列表中。维护同一 ID 时明确唯一权威来源，避免两份内容漂移。

## 5. 工具 manifest：已实现

`catalog/tools/*.yaml` 是注册工具元数据的唯一来源，一项工具一个文件；使用 [tool.schema.json](../catalog/schemas/tool.schema.json) 校验。可参考真实的 [WorldPop 声明](../catalog/tools/worldpop_download.yaml)和[工具列表声明](../catalog/tools/airmosaic_list_tools.yaml)，避免复制一份过时的示例。

| 字段 | 要求 |
|---|---|
| `schema_version` / `tool_id` | 当前版本为 1；ID 稳定且全局唯一 |
| `title` / `description` / `category` / `skill_id` / `owner_role` | 公共用途、分类、实际 skill 标识和维护角色，不含个人配置 |
| `implementation_status` / `registration_status` | 可执行项为 implemented/registered；模板和参考为 template 或 reference/catalogued |
| `entrypoint` | 真实相对路径；kind 为 cli/python_script/r_script/template/reference；CLI 声明模块和子命令 |
| `input_schema` / `argument_bindings` | 字段一一对应；命令旗标或 `positional:0` 等位置绑定，不能登记任意 shell |
| `default_arguments` | 可选，位于 entrypoint 内；机器查询接口固定 `format: json`，查询返回相应命令 token |
| `output_schema` | 机器调用的 JSON 结果类型；脚本仅声明预期产物，不代表原脚本会返回 JSON API 响应 |
| `requirements` | Python 发行包、可执行程序、R 包、允许的非秘密配置名、固定模型资源和人工检查 |
| `authentication` / `effects` | 认证方式/逻辑 profile ID，以及读写对象、联网副作用；不能登记密码、token 或实际 profile 路径 |
| `documentation` | 存在的仓库相对分类说明路径 |
| `execution` | 必填；`enabled: false` 表示仅查询。启用时声明受支持 `adapter` 与 `path_parameters`，必须与代码允许清单完全一致 |

加载时拒绝未知字段、重复 YAML 键/工具 ID、缺失绑定、不支持的版本、路径穿越或链接位置、外部 schema 引用。仅添加 YAML 不能启用任意代码执行：还必须在 `tool_policies.py` 审查登记 ID/适配器/路径角色，并在 `ToolRunnerService` 实现必要的输入、资源和结果检查，提供合成测试。CLI 适配器必须匹配已审查的子命令；两个 GCAM R 适配器使用 r_script；参考与模板保持 disabled。R 绘图的 out_dir 使用唯一允许的 env:UNIT_PRICE_OUT_DIR 绑定，不能声明任意环境键。schema 本身不授予操作权限。

参数文件不包含工具 envelope；ID 由 run-tool 命令行指定。输出字段可由执行器补齐后再按 input_schema 校验。WorldPop/GBD 的 skill.schema.json 是调用方参数快照，省略自动输出字段的必填要求；它们不注册工具，权威接口仍是 manifest。维护时同步快照与参数示例，逐项验证参数名、类型和默认输出；人工计划须明确 execution_supported 为 false，不能用伪造 action 代替未实现接口。

新增工具步骤：

1. 定义稳定 ID 与最小动作，核对实际入口和参数解析器。
2. 添加 manifest，按[存储约定](storage-and-credentials.md)声明非秘密配置、认证及副作用。资源检查只允许已配置模型根下的固定相对位置。
3. 运行 `list-tools --format json` 加载并校验全部声明，再用 `describe-tool` 和 `check-tool` 检查新项。
4. 运行对应测试，核对声明与实际 CLI/脚本参数一致，并检查错误注册和依赖缺失案例。
5. 模板/参考资料保持非可执行，不为展示“就绪”而虚构处理函数或登录状态。
6. 更新分类文档和清单；审查私人信息后按任务授权提交。

查询入口、返回码、状态优先级与 SDK 用法见[工具查询说明](usage/tool-registry.md)。同一工具在不同成员或解释器环境中的检查结果可能不同，状态不写回仓库。

## 6. Codex 中如何发现和展示

目前最稳妥的项目使用方式：打开仓库根目录，让 agent 阅读 `AGENTS.md`，再按路径读取相关 `SKILL.md`。这不要求把所有技能先安装为全局技能。

如希望通过宿主技能选择器发现，按以下步骤配置：

1. 保留 `skills/` 为源码唯一来源，选择需要暴露的实际 skill 目录；GCAM 可以先暴露总入口，按需阅读子技能。
2. 在 Codex 支持的位置安装或链接这些目录，例如仓库的 `.agents/skills/`。当前仓库尚未提供自动安装脚本；不能假设普通 `skills/` 自动成为发现入口。
3. 不将绝对路径的链接目标或机器生成的配置提交到仓库。生成入口时检查与个人已安装技能的同名冲突；不要静默覆盖个人技能。
4. 在宿主实际查看是否发现了目标名称。Codex CLI/IDE 可使用其技能选择入口确认；若未发现，检查位置、frontmatter、链接支持及宿主刷新行为。
5. 用一个范围明确的任务验证：能找到正确 skill、读取资源、调用实际工具，并正确处理依赖缺失。

`agents/openai.yaml` 可配置 `interface.display_name`、`short_description`、`default_prompt` 等；这些字段不提供 Python 函数注册、MCP 服务启动或账号认证。跨仓库分发可以后续打包为插件，保持版本可追踪。

参考：[OpenAI 官方技能说明](https://learn.chatgpt.com/docs/build-skills)。宿主行为会更新，发布安装流程时重新核对文档和实际客户端。

## 7. MCP 工具注册设计

当前没有 AirMosaic MCP 服务。接入时必须先实现适配器，再由服务通过 `tools/list` 声明工具，并处理 `tools/call`。每项声明提供稳定 `name`、用途描述和 `inputSchema`，可增加显示用 `title` 及 `outputSchema`。客户端显示方式由宿主决定。[MCP 工具规范](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

适配器应由受控入口调用现有服务，校验参数和结果，返回结构化数据及可操作的错误。若把当前 CLI 的数组响应包装为对象，需要明确这个适配差异；不能宣称两者原样兼容。行为 annotations 仅用于描述，实际权限由宿主和服务端执行。

不得将参考型 skill、未适配模板或只有示例名称的功能导出为可调用工具。登录状态留在独立认证根，非秘密路径映射留在个人配置根，密码/token 留在凭据存储；这些信息由本地/服务端管理，工具参数使用受控 ID；对外结果不包含私人路径或认证信息。

## 8. 工具列表和详情如何展示

默认列表按“基础工具、数据获取、模型分析”分组，展示标题、用途、入口类型、实现状态、当前环境状态和下一步。默认突出可调用项；参考资料、模板和规划能力显式标记。

| 状态维度 | 可用值示例 | 解释 |
|---|---|---|
| 实现 | implemented / template / reference / planned | 仓库实际提供了什么 |
| 证据 | source_review / cli_smoke / integration / scientific_validation | 已验证到哪一层，附日期与版本 |
| 当前环境 | unknown / ready / needs_auth / missing_dependency / missing_data | 本次环境检查结果，不能继承作者机器状态 |

例如：“WorldPop 数据发现：脚本已存在；当前环境尚未检查；先确认产品与网络；会写元数据。”不能只显示绿色的“已注册”。

详情应包含：实际命令/调用形式、输入输出、单位、依赖、认证方式、读写范围、网络行为、错误处理、验证证据及分类使用说明。界面默认只展示逻辑路径；成员查看本机完整路径必须限定在本地授权界面，不写入公共页面。

当前以分类 CLI 表格、JSON 和 Markdown 导航提供入口。列表与详情均从同一 manifest 派生；Markdown 只保留导航和领域限制。未来工具面板或 MCP 仍需独立实现适配器，不能把列表登记当成宿主注册。
