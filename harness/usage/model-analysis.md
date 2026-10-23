# 模型分析与人工适配

先区分“分析已有结果”“修改配置”“启动模拟”。当前支持 GCAM 已有数据库的 Python 提取和 CSV 汇总，没有统一模型模拟启动器、跨层编排或科学自动验收服务。

## 1. 真实入口

```powershell
python -m airmosaic_core.cli list-tools --category model
python -m airmosaic_core.cli describe-tool gcam_extract_market_sector
python -m airmosaic_core.cli check-tool gcam_extract_technology_components
```

| 工具 ID | 调用方式 | 范围 |
|---|---|---|
| `gcam_extract_market_sector` | run-tool | 已有市场/行业价格、数量和单位行 |
| `gcam_extract_technology_components` | run-tool | 已有技术组件行及汇总；没有 method 参数 |
| `gcam_aggregate_provinces` | run-tool | 已有市场/行业 CSV 的省级汇总 |
| `gcam_inspect_output_structure` | 准备后单独 Rscript | 固定查询和数据库布局，runner disabled |
| `gcam_plot_sector_change` | 准备后单独 Rscript | 固定比较 2021/2035，runner disabled |
| `gcam_configuration_reference` | 参考与人工任务 | 无通用配置读写或模型启动 API |
| `pm25_hia_calculate_template`、`pm25_hia_visualize_template` | 人工适配 R 模板 | 尚非可执行服务 |

全部条目可用 describe-tool 查询，只有前三项支持 run-tool。登记、静态 ready、任务 can_execute、进程 succeeded 和科学验收分别判断。

## 2. 提取：资源与参数

阅读 [GCAM 导航](../../skills/model/IAM/gcam/SKILL.md)及[提取 skill](../../skills/model/IAM/gcam/03_data_extraction/SKILL.md)。显式设置 GCAM_RELEASE_DIR，位于 Git 和数据/config/auth 根之外。模型发行包不随核心安装；提取需要 pandas、local Java、兼容 BaseX JAR。执行器检查：

```text
${GCAM_RELEASE_DIR}/libs/jars/BaseX-*.jar
${GCAM_RELEASE_DIR}/output/<scenario>/database_basexdb/
```

模型资源逻辑上按读取使用，并非 OS 强制只读；不把临时文件和新结果写回发行包。Java/库内部行为没有完整沙箱隔离。

[市场参数](../../examples/run-tool/gcam-market.json)和[技术参数](../../examples/run-tool/gcam-technology.json)都是扁平 JSON：

```json
{"scenarios":"example_scenario","regions":"AH,BJ","sectors":"cement","years":"2021,2035"}
```

| 字段 | 约定 |
|---|---|
| scenarios | 必填，逗号分隔实际情景名；安全标识符，不能是路径 |
| sectors | 必填，逗号分隔实际行业名；行业名的空格保留在字符串内 |
| regions | 逗号分隔地区代码；显式缩小到任务范围，避免原默认范围扩大 |
| years | 逗号分隔四位年份字符串，核对数据库实际年份 |
| out_dir | 通常省略，自动分配到本次任务 |

把 example_scenario 换成已有情景；实际范围放在 CONFIG_DIR 中明确指定的非秘密 JSON。AH/BJ 是两省样例，不能称为完整全国汇总。

```powershell
python -m airmosaic_core.cli run-tool gcam_extract_market_sector --params-file examples/run-tool/gcam-market.json --dry-run
python -m airmosaic_core.cli run-tool gcam_extract_technology_components --params-file examples/run-tool/gcam-technology.json --dry-run
# 条件与授权满足后，去掉 --dry-run 执行选定工具
```

缺模型根、依赖或数据库时先解决 blocker，不换成原始 Java/Python 命令绕过检查。这些工具分析已有输出，不生成新模拟。

## 3. 输出与汇总衔接

每次调用有独立 run_id，结果在 `output/<run_id>/<tool_id>/`：

| 工具 ID | 文件 |
|---|---|
| `gcam_extract_market_sector` | market_sector_rows.csv、market_sector_summary.csv |
| `gcam_extract_technology_components` | technology_component_rows.csv、technology_component_summary.csv |
| `gcam_aggregate_provinces` | province_aggregate.csv |

先确认市场提取成功并核对 CSV 的来源、地区、行业、年份、单位和覆盖。汇总读取市场/行业行，不读取技术组件表。[汇总参数](../../examples/run-tool/aggregate.json)需要把 source_run_id 替换为成功的市场提取 ID：

```json
{"input_csv":"${AIRMOSAIC_LOCAL_WORKSPACE}/output/<source_run_id>/gcam_extract_market_sector/market_sector_rows.csv"}
```

把解析后的参数保存为 CONFIG_DIR 下的 gcam-aggregate.json：

```powershell
$aggregateParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-aggregate.json"
python -m airmosaic_core.cli run-tool gcam_aggregate_provinces --params-file $aggregateParams --dry-run
python -m airmosaic_core.cli run-tool gcam_aggregate_provinces --params-file $aggregateParams
```

输入须在 workspace 的 data_cache 或既有 output 下。JSON 仅展开 `${AIRMOSAIC_LOCAL_WORKSPACE}`；source_run_id 要手工替换，其他环境变量、工具 envelope、运行记录 JSON 不可当作参数。

汇总排除 China/Global，按 scenario/source/sector/year 输出 weighted_price、quantity_sum、province_count。先检查省份覆盖与价格/数量单位；China-only 行不能做省级加权，零权重退回普通均值等行为需专业审查。脚本不自动完成选价、收入估算或全国价格的科学验收。

## 4. R 结构检查与绘图：人工准备

两项已有脚本均未接入 runner。先查询真实 ID、核对输入/依赖/输出及本次授权，再单独执行；无 runner 环境隔离或脱敏记录。

`gcam_inspect_output_structure` 读取 `${GCAM_RELEASE_DIR}/output/database_basexdb` 和 database_R/Prov_code_china.csv，与 Python 按情景布局不同。只支持 --release-dir=、--output-dir=、--max-memory=，没有 action/scenario 筛选 API。更换布局或查询需适配任务副本。

```powershell
$structureRunId = [guid]::NewGuid().ToString("N")
$structureOutput = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/$structureRunId/gcam_inspect_output_structure"
Rscript skills/model/IAM/gcam/01_output_structure/scripts/inspect_gcam_xml_structure.R "--release-dir=$env:GCAM_RELEASE_DIR" "--output-dir=$structureOutput" "--max-memory=1g"
```

必须显式输出目录，原默认位置可能在模型发行包内；脚本捕获部分查询错误，不能只看完成提示。

`gcam_plot_sector_change` 接受 --input-csv、--sectors、--scenarios，没有 --out-dir。把已核对的市场行 CSV 映射到 marketCsv，并设置新任务目录：

```powershell
$plotRunId = [guid]::NewGuid().ToString("N")
$env:UNIT_PRICE_OUT_DIR = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/$plotRunId/gcam_plot_sector_change"
# $marketCsv 必须已映射且含 2021/2035 和所需情景，替换示例情景名
Rscript skills/model/IAM/gcam/03_data_extraction/scripts/plot_sector_change.R --input-csv $marketCsv --sectors "cement" --scenarios "example_scenario"
```

更换比较年份或方法需适配副本，检查 R 包和输出；原始日志在本地审查、脱敏，不能当作 runner 已处理的共享记录。

## 5. 配置与健康影响：人工适配

`gcam_configuration_reference` 只提供[配置参考](../../skills/model/IAM/gcam/02_configuration/SKILL.md)。解释时只读核对所需组件、顺序和引用。获授权的修改先复制配置及必要依赖到新任务目录，检查 XML、顺序、引用及差异。示例 JSON 是人工计划，不是 --params-file 或 API；修改配置不自动授权运行模型。

[健康计算和绘图](../../skills/model/04_impact/health_impact_analysis/SKILL.md)是待适配模板。计算读取 PM25_HIA_CONC_DIR、PM25_HIA_POP_DIR、PM25_HIA_MORT_FILE、PM25_HIA_RR_FILE、PM25_HIA_OUTPUT_DIR、PM25_HIA_YEARS、PM25_HIA_CURVE；绘图另用 PM25_HIA_POP_FILE、PM25_HIA_SHP_DIR，没有自动配置加载器。

适配输入命名、网格、人口分母、年龄/性别、死亡率年份、RR 曲线、浓度截断和缺失；source 会执行计算。PAF 为无量纲比例，每十万人率另换算。用 RR=1、零人口、相同基线/政策、缺失输入等案例检查，再核对分组闭合；模板或退出码不代表方法已验收。

## 6. 验证与共享

记录模型/数据版本、情景、区域、年份、单位、来源与验收结果。run-tool 记录仅保留允许字段，实际科学文件仍须审核才能共享。当前不自动衔接数据—模型、修改情景或进行科学验收。执行边界见[执行指南](run-tool.md)和[存储约定](../storage-and-credentials.md)。
