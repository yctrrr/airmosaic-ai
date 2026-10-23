# 工具能力与执行边界

真实 ID、参数与执行支持以 `catalog/tools/*.yaml` 和 list-tools/describe-tool 为准。当前 23 个登记条目中 14 个支持 run-tool（8 个核心 CLI、6 个 Python 脚本）；登记不证明本机就绪、登录或科学验证通过。操作见[查询指南](usage/tool-registry.md)和[执行指南](usage/run-tool.md)，验证层级见[记录](verification.md)。

## 核心工具

使用同一项目 Python 环境从仓库根调用 CLI，或通过下列真实 ID 调用 run-tool。查询命令保留公共详情；runner 的核心结果只返回允许的脱敏摘要。

| 工具 ID | 原 CLI 子命令 | runner | 范围 |
|---|---|---|---|
| `airmosaic_list_datasets` | list-datasets | 是 | acquisition 声明，不查实际内容 |
| `airmosaic_describe_dataset` | describe-dataset | 是 | 数据详情及既有数据别名 |
| `airmosaic_search_datasets` | search-datasets | 是 | 本地元数据关键词匹配 |
| `airmosaic_check_availability` | check-availability | 是 | 文件存在性，不验年限/单位/质量；原 CLI 会输出本机路径 |
| `airmosaic_draft_causal_plan` | draft-causal-plan | 是 | 本地模板，不调用 LLM 或建立因果结论 |
| `airmosaic_list_tools` | list-tools | 是 | 工具分类、筛选与静态状态 |
| `airmosaic_describe_tool` | describe-tool | 是 | manifest、参数、实际入口 |
| `airmosaic_check_tool` | check-tool | 是 | 静态前置条件，不验证登录 |
| `airmosaic_run_tool` | run-tool | 否，禁止递归 | 此条目用于展示执行器自身 |

SDK 导出 DataCatalogService、DataAccessService、CausalDesignService、ToolRegistryService 和 ToolRunnerService；详见[基础工具](usage/core.md)。MCP、REST、自动技能安装器和跨层编排未实现。

## 数据获取与处理

具体步骤及参数见[数据获取](usage/data-acquisition.md)。

| 工具 ID | skill | runner | 边界 |
|---|---|---|---|
| `worldpop_download` | [WorldPop](../skills/data_acquisition/01_socioeconomic/worldpop/SKILL.md) | 是 | requests；发现也联网写元数据，下载由参数显式启用 |
| `csmar_process_company_info` | [CSMAR](../skills/data_acquisition/01_socioeconomic/csmar/SKILL.md) | 是 | pandas/openpyxl；只处理已有企业基础信息 ZIP |
| `ihme_gbd_fetch_results` | [GBD](../skills/data_acquisition/04_impact/ihme-gbd-results/SKILL.md) | 是 | 本机已登录浏览器，网络许可与会话声明；版本/维度需核对 |
| `csmar_browser_download` | CSMAR | 否，参考 | 浏览器获取需要本人机构权限及实际可用工具 |
| `yearbook_regional_sector_template` | [工业年鉴](../skills/data_acquisition/01_socioeconomic/ind_yearbook/SKILL.md) | 否，模板 | 人工适配地区行业表头、编码、年份和输出 |
| `yearbook_product_output_template` | 工业年鉴 | 否，模板 | 人工适配产品、单位与缺失规则；无独立全国行业实现 |

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

参考 [GCAM 总导航](../skills/model/IAM/gcam/SKILL.md)和[模型分类说明](usage/model-analysis.md)。

| 工具 ID | runner | 范围 |
|---|---|---|
| `gcam_extract_market_sector` | 是 | 已有数据库的市场/行业行，需 pandas、Java/BaseX 和模型根 |
| `gcam_extract_technology_components` | 是 | 已有技术组件行及汇总，不提供 method 参数 |
| `gcam_aggregate_provinces` | 是 | 已有市场 CSV；排除 China/Global，人工核对覆盖、单位和权重 |
| `gcam_inspect_output_structure` | 否，独立 R | 固定查询、output/database_basexdb 布局；必要时适配副本 |
| `gcam_plot_sector_change` | 否，独立 R | 固定 2021/2035，显式设置 UNIT_PRICE_OUT_DIR |
| `gcam_configuration_reference` | 否，参考 | 只读说明或授权任务副本修改；没有配置 API 或模拟启动器 |
| `pm25_hia_calculate_template` | 否，模板 | [健康影响](../skills/model/04_impact/health_impact_analysis/SKILL.md)输入和方法需适配验收 |
| `pm25_hia_visualize_template` | 否，模板 | 绘图输入、网格、依赖与输出需人工检查 |

## 参数、模板与注册的区别

可执行 JSON 示例只含 manifest 参数，工具 ID 在 run-tool 命令行指定。列表使用逗号分隔字符串，输出通常省略以自动分配任务目录。标为人工计划的配置/结构 JSON 使用 reference_tool_id 和 execution_supported: false，只供阅读，不能传给 run-tool。其余领域蓝图也不会成为可调用 action。

新增工具需同步 manifest、允许清单、参数解析、分类说明和 skill，遵循[注册规范](tool-registration.md)。状态查询的 ready 不表示任务 can_execute；进程 succeeded 不表示科学验收通过。

`workflow/SKILL.md` 保留四层设计，没有标准 skill frontmatter，也没有自动执行器。数据获取、处理、模型使用和结果验收需要显式传递产物及方法，不会自动串联。
