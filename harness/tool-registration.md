# 技能、数据集与工具的注册和展示

本规范定义 AirMosaic 的协作约定和后续实现要求。当前已生效的是核心 CLI、Python 类方法、skill 文件和 acquisition `datasets.yaml` 扫描。统一工具清单加载器、自动安装器、工具面板与 MCP 适配器尚未实现。

## 1. 四种登记对象分别管理

| 对象 | 标识与声明位置 | 谁读取 | 登记后的实际效果 |
|---|---|---|---|
| Skill | `SKILL.md` 的 `name`、`description` | Agent 或宿主技能发现机制 | 让 agent 找到专业流程 |
| 宿主展示元数据 | skill 内 `agents/openai.yaml` | 支持该格式的宿主 | 配置名称、提示词、依赖等；不创建可执行函数 |
| Dataset | acquisition skill 内 `datasets.yaml` 的 `dataset_id` | `DataCatalogService` | 出现在 `list-datasets`；不自动下载或校验数据 |
| Tool | 当前为源码中的 CLI/方法/脚本；未来使用统一 manifest | 对应运行入口；未来由 harness 加载 | 只有实际适配器和处理函数存在，才可调用 |

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

## 5. 工具 manifest 设计

建议后续以 `catalog/tools/*.yaml` 为执行工具元数据的唯一来源，再生成列表、详情和宿主适配器声明。**当前没有这类加载器，以下 YAML 是规范示例，不会自行注册工具。**

```yaml
schema_version: 1
tool_id: airmosaic_list_datasets
title: 查询可获取的数据集
description: 按领域、层级或负责技能列出数据声明，返回元数据。
category: core
owner_role: core-maintainer
implementation_status: implemented
registration_status: proposed
entrypoint:
  kind: python_module_cli
  module: airmosaic_core.cli
  subcommand: list-datasets
  argument_bindings:
    layer: --layer
    skill: --skill
    domain: --domain
input_schema:
  type: object
  properties:
    layer: {type: string}
    skill: {type: string}
    domain: {type: string}
  additionalProperties: false
output_schema:
  type: array
  items:
    type: object
    required: [dataset_id, name, domain, layer, skill_id, skill_path, access_mode, description]
effects:
  reads: [repository_dataset_metadata]
  writes: []
  network: false
  credentials: false
requirements:
  python: '>=3.10'
  python_packages: [PyYAML]
documentation: harness/usage/core.md
```

示例的 `implemented` 只指现有 CLI，`proposed` 指未来工具登记。解释器由本地环境解析；不能将某成员的 Python 绝对路径写入 manifest。角色需在实际审核流程中对应明确维护者，不可把角色字符串当作访问授权。

新增工具的登记流程：

1. 确认最小动作和副作用，给出稳定 ID、标题、描述与分类。
2. 实现或定位真实入口；参数与真实解析器逐项对应，禁止使用无法执行的示例名称。
3. 定义输入和输出 schema、单位及缺失值语义；参数绑定使用白名单，不接收任意 shell 命令。
4. 声明依赖、网络、认证、可读数据根、输出根、覆盖行为、预期耗时及取消方式。按照[存储约定](storage-and-credentials.md)区分数据、非秘密配置与认证根；工具只声明认证方式或逻辑 profile ID，不登记密码/token。
5. 为成功、错误输入、依赖缺失和越界请求编写案例；通过后记录证据级别。
6. 加入统一目录，并验证列表、详情、调用和分类文档一致。
7. 面向某宿主发布时再完成相应安装/连接，实测该宿主的发现与调用。

运行时可用性按当前成员环境计算，不硬编码在仓库 manifest 中。相同工具在甲成员处可以就绪，在乙成员处可以因未登录或缺少数据而不可用。

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

当前以 Markdown 清单提供入口。未来增加列表命令、工具面板和自动生成文档时，应从同一 manifest 派生，检查变更后无差异；具体命令名称在实现前仅作为设计讨论，不放进“可直接运行”的示例。
