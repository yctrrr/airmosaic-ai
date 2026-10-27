# 模型分析与人工适配

按[四步流程](../four-step-workflow.md)定位模型与交接。GEOS-Chem 的[使用与编译排错](../../skills/model/03_atmospheric_transport/geos-chem/SKILL.md)为参考；GCAM [构建排错](../../skills/model/IAM/gcam/references/build-troubleshooting.md)与已有输出分析分开。两者均无编译或模拟 run-tool 适配器。

近期本地排放、成本、浓度健康、GCAM 与机器学习方法另见[方法库](../../methods/README.md)，其中本地项目源码与已接入适配器分别标记。

先区分“分析已有结果”“修改配置”“启动模拟”。当前支持 GCAM 已有数据库的结构检查、Python 提取、CSV 汇总和 R 绘图，没有统一模型模拟启动器、跨层编排或科学自动验收服务。

机器学习方法另见[机器学习分类说明](machine-learning.md)、[mlr3 skill](../../skills/model/machine_learning/mlr3/SKILL.md)和 [TimeXer skill](../../skills/model/machine_learning/timexer/SKILL.md)，当前按参考流程登记，尚无训练/预测适配器。

## 1. 真实入口

```powershell
python -m airmosaic.cli list-tools --category model
python -m airmosaic.cli describe-tool gcam_extract_market_sector
python -m airmosaic.cli check-tool gcam_extract_technology_components
```

| 工具 ID | 调用方式 | 范围 |
|---|---|---|
| `gcam_extract_market_sector` | run-tool | 已有市场/行业价格、数量和单位行 |
| `gcam_extract_technology_components` | run-tool | 已有技术组件行及汇总；没有 method 参数 |
| `gcam_aggregate_provinces` | run-tool | 已有市场/行业 CSV 的省级汇总 |
| `gcam_inspect_output_structure` | run-tool（R） | 固定查询和数据库布局 |
| `gcam_plot_sector_change` | run-tool（R） | 固定比较 2021/2035 |
| `gcam_configuration_reference` | 参考与人工任务 | 无通用配置读写或模型启动 API |
| `pm25_hia_calculate_template`、`pm25_hia_visualize_template` | 人工适配 R 模板 | 尚非可执行服务 |

全部条目可用 describe-tool 查询，前五项支持 run-tool。登记、静态 ready、任务 can_execute、进程 succeeded 和科学验收分别判断。

## 2. 提取：资源与参数

阅读 [GCAM 导航](../../skills/model/IAM/gcam/SKILL.md)及[提取 skill](../../skills/model/IAM/gcam/03_data_extraction/SKILL.md)。显式设置 GCAM_RELEASE_DIR，位于 Git 和数据/config/auth 根之外。模型发行包不随核心安装；提取需要 pandas、local Java、兼容 BaseX JAR。执行器检查：

```text
${GCAM_RELEASE_DIR}/libs/jars/BaseX-*.jar
${GCAM_RELEASE_DIR}/output/<scenario>/database_basexdb/
```

模型资源逻辑上按读取使用，并非 OS 强制只读；不把临时文件和新结果写回发行包。Java/库内部行为没有完整沙箱隔离。

[市场参数](../../config/examples/run-tool/gcam-market.json)和[技术参数](../../config/examples/run-tool/gcam-technology.json)都是扁平 JSON：

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
python -m airmosaic.cli run-tool gcam_extract_market_sector --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-market.json --dry-run
python -m airmosaic.cli run-tool gcam_extract_technology_components --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-technology.json --dry-run
# 条件与授权满足后，去掉 --dry-run 执行选定工具
```

缺模型根、依赖或数据库时先解决 blocker，不换成原始 Java/Python 命令绕过检查。这些工具分析已有输出，不生成新模拟。

## 3. 输出与汇总衔接

每次调用有独立 run_id，结果在 `results/<project_id>/<run_id>/<stage>/<tool_id>/`：

| 工具 ID | 文件 |
|---|---|
| `gcam_extract_market_sector` | market_sector_rows.csv、market_sector_summary.csv |
| `gcam_extract_technology_components` | technology_component_rows.csv、technology_component_summary.csv |
| `gcam_aggregate_provinces` | province_aggregate.csv |

先确认市场提取成功并核对 CSV 的来源、地区、行业、年份、单位和覆盖。汇总读取市场/行业行，不读取技术组件表。[汇总参数](../../config/examples/run-tool/aggregate.json)需要把 source_run_id 替换为成功的市场提取 ID：

```json
{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/results/<source_project_id>/<source_run_id>/01_socioeconomic_natural_change/gcam_extract_market_sector/market_sector_rows.csv"}
```

把解析后的参数保存为 CONFIG_DIR 下的 gcam-aggregate.json：

```powershell
$aggregateParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-aggregate.json"
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $aggregateParams --dry-run
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $aggregateParams
```

输入须在 workspace 的 data 或显式引用的 results 下。JSON 仅展开 `${AIRMOSAIC_ASSETS_DIR}`；source_run_id 要手工替换，其他环境变量、工具 envelope、运行记录 JSON 不可当作参数。

汇总排除 China/Global，按 scenario/source/sector/year 输出 weighted_price、quantity_sum、province_count。先检查省份覆盖与价格/数量单位；China-only 行不能做省级加权，零权重退回普通均值等行为需专业审查。脚本不自动完成选价、收入估算或全国价格的科学验收。

## 4. R 结构检查与绘图：统一执行

两项已有 R 脚本均通过 run-tool 执行。需要本地 PATH 上的原生 Rscript；结构检查另需 Java。R 使用 `--vanilla`，不加载个人或站点启动配置，不继承 R_LIBS、R_PROFILE、R_ENVIRON 等注入变量。所需包须装在所选 R 的标准 library 中；本版本不自动使用个人/site 扩展包目录、不自动安装软件。三个数据/config/auth 根仍须分别准备。

| 工具 | R 包 | 参数与资源 |
|---|---|---|
| `gcam_inspect_output_structure` | data.table、rgcam | `max_memory` 默认 `1g`，可用 `512m`；`output_dir` 自动分配。模型根来自本地 GCAM_RELEASE_DIR，不接受 JSON release_dir |
| `gcam_plot_sector_change` | dplyr、ggplot2、readr、tidyr | 必填 `input_csv`；可选逗号字符串 `sectors`、`scenarios`；`out_dir` 自动分配 |

check-tool 和 dry-run 不启动 R，包状态保留为 unverified；实际执行先加载 namespace，再运行脚本，缺包/依赖无法加载返回 failed、r_dependency_unavailable。`can_execute: true` 只表示静态预检未发现阻塞，不能证明包已加载或数据库兼容。运行中的超时/原生崩溃也不能当成验证完成。

### 结构检查

固定读取 `${GCAM_RELEASE_DIR}/output/database_basexdb` 和 `${GCAM_RELEASE_DIR}/database_R/Prov_code_china.csv`。这与 Python 的按情景布局不同；Java classpath 来自 rgcam，不使用 Python 提取器的 libs/jars 选择规则。包和 BaseX/数据库版本兼容性要在实际执行中核验。

```powershell
python -m airmosaic.cli describe-tool gcam_inspect_output_structure
python -m airmosaic.cli run-tool gcam_inspect_output_structure --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-inspect.json --dry-run
python -m airmosaic.cli run-tool gcam_inspect_output_structure --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-inspect.json --timeout 600
```

[参数示例](../../config/examples/run-tool/gcam-inspect.json)：`{"max_memory":"1g"}`。执行器固定传入 max_memory，不继承调用方的 GCAM_BASEX_MAX_MEMORY；输出限制在本次任务目录，不回写原默认 derived 位置。生成 inspect_scenarios.csv、inspect_province_top_level.csv、inspect_industrial_sector_tree.csv、inspect_industrial_cost_nodes.csv。原脚本会继续处理后续查询，因此执行器检查全部四个文件存在且非空；缺少任一文件返回 failed、expected_outputs_missing，保留部分输出。文件存在不表示内容或科学口径已验收。

没有 action、scenario、region 或 sector 筛选参数。自定义查询、不同数据库布局和新增行业需要人工适配任务副本，并另行审查接入；不要因 runner 拒绝参数而改用原始命令绕过检查。

### 绘图与市场提取衔接

[绘图参数](../../config/examples/run-tool/gcam-plot.json)与汇总一样，需要把 source_run_id 和情景名换成本次已核对值：

```json
{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/results/<source_project_id>/<source_run_id>/01_socioeconomic_natural_change/gcam_extract_market_sector/market_sector_rows.csv","sectors":"cement","scenarios":"example_scenario"}
```

保存到 CONFIG_DIR 下的 gcam-plot.json 后调用：

```powershell
$plotParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-plot.json"
python -m airmosaic.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $plotParams --dry-run
python -m airmosaic.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $plotParams --timeout 300
```

input_csv 必须是 workspace data 或显式引用的 results 内的文件；旧 R 参数解析器会按逗号拆分输入，因此路径含逗号时拒绝执行。显式提供 sectors/scenarios 可限定任务范围；省略 sectors 时仍采用原默认 cement、coke、iron and steel，省略 scenarios 时仍使用全部情景。比较年份固定为 2021/2035。

执行器把 out_dir 映射为本次子进程的 UNIT_PRICE_OUT_DIR，不读取调用方该变量，也不向脚本传入不存在的 --out-dir。输出 sector_change_2021_2035.png 和 sector_change_weighted_mean.csv；两者均须存在且非空。保留原 sector_cost 筛选、China/Global 排除、负权重截零与零权重均值回退。检查两年数据、价格/数量单位、完整地区覆盖和零基期价格等问题；修改年份、图式或计算方法仍需人工适配。

## 5. 配置与健康影响：人工适配

`gcam_configuration_reference` 只提供[配置参考](../../skills/model/IAM/gcam/02_configuration/SKILL.md)。解释时只读核对所需组件、顺序和引用。获授权的修改先复制配置及必要依赖到新任务目录，检查 XML、顺序、引用及差异。示例 JSON 是人工计划，不是 --params-file 或 API；修改配置不自动授权运行模型。

[健康计算和绘图](../../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md)是待适配模板。计算读取 PM25_HIA_CONC_DIR、PM25_HIA_POP_DIR、PM25_HIA_MORT_FILE、PM25_HIA_RR_FILE、PM25_HIA_OUTPUT_DIR、PM25_HIA_YEARS、PM25_HIA_CURVE；绘图另用 PM25_HIA_POP_FILE、PM25_HIA_SHP_DIR，没有自动配置加载器。

适配输入命名、网格、人口分母、年龄/性别、死亡率年份、RR 曲线、浓度截断和缺失；source 会执行计算。PAF 为无量纲比例，每十万人率另换算。用 RR=1、零人口、相同基线/政策、缺失输入等案例检查，再核对分组闭合；模板或退出码不代表方法已验收。

## 6. 验证与共享

记录模型/数据版本、情景、区域、年份、单位、来源与验收结果。run-tool 记录仅保留允许字段，实际科学文件仍须审核才能共享。当前不自动衔接数据—模型、修改情景或进行科学验收。执行边界见[执行指南](run-tool.md)和[存储约定](../storage-and-credentials.md)。
