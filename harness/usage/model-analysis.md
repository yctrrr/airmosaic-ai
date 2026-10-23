# 模型分析工具

先阅读对应 skill，明确模型版本、研究范围和输入数据。当前多为脚本或模板，不是完整的统一模型服务。所有例子使用通用参数，实际模型数据与输出留在成员自己的授权目录。

## 1. GCAM：先确认要做什么

| 任务 | 入口 | 边界 |
|---|---|---|
| 理解模型或查询结构 | [输出结构 skill](../../skills/model/IAM/gcam/01_output_structure/SKILL.md) | 先检查数据库布局及字段 |
| 理解或修改情景配置 | [配置 skill](../../skills/model/IAM/gcam/02_configuration/SKILL.md) | 参考型能力；修改须有明确目标并操作副本 |
| 提取已有结果、汇总和绘图 | [提取 skill](../../skills/model/IAM/gcam/03_data_extraction/SKILL.md) | 不等于运行 GCAM 模型本身 |

在本地设置 `GCAM_RELEASE_DIR`，指向经授权的模型发行包。Python 提取脚本依赖 pandas、Java 和发行包中的 BaseX JAR；R 结构检查依赖 `data.table`、`rgcam` 及其 Java 配置。模型发行包和数据库不随核心 Python 包安装。

Python 依赖可在项目环境中用 `& $amPython -m pip install pandas` 安装。R 包、Java 和模型发行包按各自版本要求配置，再检查实际可用性；不要从未审核的安装脚本自动取得运行权限。

## 2. 输出结构检查

当前 R 脚本接受 `--release-dir=...`、`--output-dir=...`、`--max-memory=...`，并非任意 action/scenario 的通用 API。它要求 `${GCAM_RELEASE_DIR}/output/database_basexdb` 和 `database_R/Prov_code_china.csv`；这与 Python 提取脚本按情景子目录定位的方式不同。

从仓库根目录执行，先在本地配置好 `GCAM_RELEASE_DIR` 与 `AIRMOSAIC_LOCAL_WORKSPACE`：

```powershell
$structureScript = "skills/model/IAM/gcam/01_output_structure/scripts/inspect_gcam_xml_structure.R"
$structureOutput = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/example/gcam-structure"
Rscript $structureScript "--release-dir=$env:GCAM_RELEASE_DIR" "--output-dir=$structureOutput" "--max-memory=1g"
```

显式提供输出位置，避免写入模型发行包。脚本逐项查询中有错误捕获，因此终端出现完成提示仍需核对各输出表是否存在、非空且覆盖请求范围。当前脚本内含预设行业列表，不能宣称已经扫描所有可能模型节点。

## 3. 提取、汇总、绘图

以下 PowerShell 示例沿用[基础工具](core.md)中配置的 `$amPython`。先查真实情景和行业名称，将示例值映射到本地模型；命令均从仓库根目录运行。

```powershell
$gcamScripts = "skills/model/IAM/gcam/03_data_extraction/scripts"
$env:UNIT_PRICE_OUT_DIR = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/example/gcam-extraction"
New-Item -ItemType Directory -Force -Path $env:UNIT_PRICE_OUT_DIR | Out-Null
$scenario = "example_scenario"
& $amPython "$gcamScripts/xquery_market_sector.py" --scenarios $scenario --regions "China" --sectors "cement" --years "2021,2035" --out-dir $env:UNIT_PRICE_OUT_DIR
& $amPython "$gcamScripts/xquery_technology_components.py" --scenarios $scenario --regions "China" --sectors "cement" --years "2021,2035" --out-dir $env:UNIT_PRICE_OUT_DIR
```

Python 提取脚本要求数据库位于 `${GCAM_RELEASE_DIR}/output/<scenario>/database_basexdb`。当前技术组件脚本没有 `--method` 参数。上例只提取 China 汇总节点，不能直接拿来做省级加权。

需要省级汇总时，先按任务明确省份列表并提取相应行，检查覆盖和单位，再调用：

```powershell
$marketCsv = Join-Path $env:UNIT_PRICE_OUT_DIR "market_sector_rows.csv"
& $amPython "$gcamScripts/xquery_province_aggregator.py" --input-csv $marketCsv --out-dir $env:UNIT_PRICE_OUT_DIR
Rscript "$gcamScripts/plot_sector_change.R" --input-csv $marketCsv --sectors "cement" --scenarios $scenario
```

汇总器会排除 China/Global 行；需确保输入中存在有效省级数据。价格的权重、数量口径和各行单位必须先核对。其零权重退回普通均值等行为应由领域案例审查，不能把输出数字直接解释为所有情景下都正确的全国价格。

当前绘图脚本比较 2021 和 2035，支持 `--sectors`、`--scenarios`、`--input-csv`；输出目录由 `UNIT_PRICE_OUT_DIR` 控制，没有已实现的 `--out-dir` 参数。跨年比较前确认输入含这两个年份。

## 4. 配置理解和修改

先只读检查配置组件、顺序和引用文件。用户要求修改情景时，明确目标情景和允许改变的参数，将配置与必要依赖复制到本地任务目录，检查引用可解析后再运行获授权的测试。

`inspect_gcam_config`、`update_gcam_configuration` 等目前是示例名称；没有通用 handler，不能把示例 JSON 发送给一个假设存在的服务。启动新的 GCAM 模拟与“提取已有结果”属于不同操作范围。

## 5. 健康影响：适配与验收

入口：[健康影响 skill](../../skills/model/04_impact/health_impact_analysis/SKILL.md)。计算模板需要 R 与 `data.table`，输入包括浓度、人口、年龄结构、基线死亡率和 RR 曲线。绘图模板另有自己的 `library()` 依赖，应按文件检查。

当前计算模板实际读取以下变量：

| 变量 | 含义 |
|---|---|
| `PM25_HIA_CONC_DIR` | 浓度 CSV 目录 |
| `PM25_HIA_POP_DIR` | 人口及年龄结构 RDS 目录 |
| `PM25_HIA_MORT_FILE` | 基线死亡率文件 |
| `PM25_HIA_RR_FILE` | RR 查找表 |
| `PM25_HIA_OUTPUT_DIR` | 本次任务输出目录，必须显式设置 |
| `PM25_HIA_YEARS` | 逗号分隔的年份 |
| `PM25_HIA_CURVE` | 曲线标识 |

模板期待具体列名和文件命名，例如 `pm25_annual_<year>.csv`、`Population_g0.1_<year>.Rds`、`Age_Structure_Fraction_g0.1_<year>.Rds`。这些命名不证明数据已经满足目标网格、人口口径或时间条件。

执行步骤：

1. 先核对列、单位、网格、年份、年龄/性别和曲线定义，明确各输入来源。
2. 在本地任务副本中完成必要适配。检查死亡率年份处理、年龄权重、浓度截断和缺失处理，不能把模板默认行为直接作为已验收方法。
3. 用独立可计算案例检查 `RR=1`、人口为零、相同政策/基线、单位换算和缺失输入等情况。
4. 明确 PAF 为无量纲比例；死亡率的每十万人换算单独核对。年龄合并与男女加总需与人口分母一致。
5. 科学案例通过后才运行获准范围；核对输出总量与分组闭合，并记录方法限制。

模板在加载时会执行计算，因此在输入映射和输出目录确认前，不要把 `source()` 当成无副作用的帮助命令。`PM25_DEATH_YEARS` 等旧名称不是此模板读取的环境变量。

## 6. 验证与交付

记录模型版本、数据版本、情景、区域、年份、单位、参数、输出及案例结果。公开交付使用逻辑输入 ID 和脱敏摘要；实际模型目录、用户身份及私有数据内容仅保留在授权本地记录中。

程序完成、数据检查通过、科学验收通过分别陈述。当前没有统一模型运行器或科学验收服务，相关状态由成员/agent 根据证据记录。
