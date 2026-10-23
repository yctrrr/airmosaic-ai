# 当前工具与技能清单

按 2026-10-15 的源码核对。此清单描述仓库能力，不证明当前成员已经安装依赖、具备数据权限或通过真实数据验证。源码变更时同步更新清单及对应类别说明。

本次核对的方法和限制见[验证记录](verification.md)。

## 基础工具

入口位于 [CLI](../src/airmosaic_core/cli.py)，安装后可运行 `airmosaic` 或同一 Python 环境中的 `python -m airmosaic_core.cli`。详见[基础工具使用](usage/core.md)。

| 实际命令 | 功能 | 输出 | 边界 |
|---|---|---|---|
| `list-datasets` | 按 layer / skill / domain 筛选数据声明 | JSON 数组 | 只扫描 acquisition 声明，不查远端或本机数据内容 |
| `describe-dataset <dataset_id>` | 返回数据详情，支持现有别名 | JSON 对象 | 可后备查找 `catalog/datasets/` |
| `search-datasets <query>` | 检索声明元数据 | JSON 数组 | 按空白切词，各词均需匹配；不是互联网搜索 |
| `check-availability <dataset_id>` | 查找缓存根中匹配的文件 | JSON 对象 | 不验证文件内容、年份或校验和；结果可含本机绝对路径 |
| `draft-causal-plan` | 生成本地因果设计模板 | JSON 对象 | 不调用 LLM，不生成实际 DAG 或因果估计结果 |

核心 SDK 导出 `DataCatalogService`、`DataAccessService`、`CausalDesignService` 三个类；未导出可直接导入的同名自由函数。分类文档给出真实方法调用。

## 数据获取与处理

详见[数据获取使用说明](usage/data-acquisition.md)。脚本入口存在的项目仍需单独核对依赖及数据条件。

| 能力与 skill | 当前入口 | 实现状态 | 执行条件/副作用 |
|---|---|---|---|
| [WorldPop](../skills/data_acquisition/01_socioeconomic/worldpop/SKILL.md) | [download_worldpop.py](../skills/data_acquisition/01_socioeconomic/worldpop/scripts/download_worldpop.py) | Python 脚本 | 联网；发现也写元数据；`--download` 额外下载文件 |
| [CSMAR](../skills/data_acquisition/01_socioeconomic/csmar/SKILL.md) 下载 | 技能描述的浏览器流程 | 操作流程 | 个人授权登录；未提供统一下载 CLI |
| CSMAR 企业信息处理 | [process_listed_company_basic_info.py](../skills/data_acquisition/01_socioeconomic/csmar/scripts/process_listed_company_basic_info.py) | Python 脚本 | 读取已下载 ZIP，写候选企业表；不代表所有财务表处理器 |
| [工业年鉴](../skills/data_acquisition/01_socioeconomic/ind_yearbook/SKILL.md) | [地区模板](../skills/data_acquisition/01_socioeconomic/ind_yearbook/templates/process_regional_sector.R)、[产品模板](../skills/data_acquisition/01_socioeconomic/ind_yearbook/templates/process_product_output.R) | R 模板 | 需适配本地输入、年份和输出；未提供独立 national-sector 模板 |
| [IHME GBD](../skills/data_acquisition/04_impact/ihme-gbd-results/SKILL.md) | [fetch_gbd_results_redux.py](../skills/data_acquisition/04_impact/ihme-gbd-results/scripts/fetch_gbd_results_redux.py) | Python 脚本 | 已登录浏览器、CDP、页面结构兼容；写 CSV 和 JSON sidecar |

`list-datasets` 当前可读取 9 条声明，数量是此版本快照，不是未来固定验收标准：

| Dataset ID | 负责 skill_id | 声明范围 |
|---|---|---|
| `worldpop_population_grid` | worldpop | 人口栅格产品 |
| `worldpop_zonal_statistics` | worldpop | 分区统计能力声明；尚无独立本地处理入口 |
| `csmar_listed_company_basic` | csmar | 上市公司基础信息 |
| `csmar_financial_statements` | csmar | 财务表获取声明；需按实际表核对流程 |
| `industrial_yearbook_national_sector` | ind_yearbook | 全国行业指标；需补齐/适配实现 |
| `industrial_yearbook_regional_sector` | ind_yearbook | 地区行业指标 |
| `industrial_yearbook_product_output` | ind_yearbook | 地区产品产量 |
| `ihme_gbd_mortality_rates` | ihme-gbd-results | 死亡率数据 |
| `ihme_gbd_population` | ihme-gbd-results | 人口数据声明；需核对具体请求维度 |

## 模型分析

详见[模型使用说明](usage/model-analysis.md)。

| 能力 | 当前入口 | 状态与范围 |
|---|---|---|
| [GCAM 总导航](../skills/model/IAM/gcam/SKILL.md) | 输出结构、配置、提取三个子 skill | 参考/路由技能 |
| GCAM 输出结构 | [inspect_gcam_xml_structure.R](../skills/model/IAM/gcam/01_output_structure/scripts/inspect_gcam_xml_structure.R) | R 脚本；读取特定数据库布局并导出检查表 |
| GCAM 配置 | [配置 skill](../skills/model/IAM/gcam/02_configuration/SKILL.md) | 参考说明；没有通用配置读写工具处理函数 |
| GCAM 市场/行业提取 | [xquery_market_sector.py](../skills/model/IAM/gcam/03_data_extraction/scripts/xquery_market_sector.py) | Python 脚本；需要 Java/BaseX 及模型输出 |
| GCAM 技术组件提取 | [xquery_technology_components.py](../skills/model/IAM/gcam/03_data_extraction/scripts/xquery_technology_components.py) | Python 脚本；当前没有 `--method` 参数 |
| GCAM 省级汇总 | [xquery_province_aggregator.py](../skills/model/IAM/gcam/03_data_extraction/scripts/xquery_province_aggregator.py) | Python 脚本；读取提取 CSV 并写汇总 |
| GCAM 变化绘图 | [plot_sector_change.R](../skills/model/IAM/gcam/03_data_extraction/scripts/plot_sector_change.R) | R 脚本；当前固定比较 2021/2035，输出由环境变量控制 |
| [PM2.5 健康影响](../skills/model/04_impact/health_impact_analysis/SKILL.md) | [计算模板](../skills/model/04_impact/health_impact_analysis/templates/calculate_pm25_deaths.R)、[绘图模板](../skills/model/04_impact/health_impact_analysis/templates/visualize_pm25_deaths.R) | R 模板；数据适配与科学验收待各任务完成 |

## 哪些名称尚未注册为工具

以下名称见于技能契约、请求示例或流程设计。它们当前没有相应 AirMosaic MCP 注册或统一工具处理器；部分有可供未来封装的脚本。

- WorldPop：`discover_worldpop`、`acquire_worldpop_population`。
- GBD：`fetch_gbd_results`。
- GCAM 结构与配置：`explore_gcam_output_structure`、`inspect_gcam_config`、`update_gcam_configuration`、`explain_scenario_setup`、`trace_input_to_output`、`diagnose_ccs_config`。
- GCAM 提取与展示：`extract_gcam_market_sector_data`、`extract_gcam_technology_components`、`aggregate_gcam_province_data`、`plot_gcam_sector_change`。
- Workflow：`WorkflowOrchestrator`、`get_workflow_output`、`audit_trace`、`compare_methods`。

当前未提供统一 `list-tools`、`run-tool`、`doctor` 命令、REST 服务或自动技能安装器。新成员可按本清单调用真实入口；后续封装遵循[注册规范](tool-registration.md)。

## 维护时必须同步的事项

新增或更改一个入口时，核对其参数解析器/方法签名、分类说明、skill 元数据、数据声明及本清单。记录验证层级；只有静态读取源码的能力不能标成真实数据集成通过。

现有 `workflow/SKILL.md` 是工作流设计说明，未含标准 skill frontmatter；不能因文件名相同就把它计入宿主技能发现清单。
