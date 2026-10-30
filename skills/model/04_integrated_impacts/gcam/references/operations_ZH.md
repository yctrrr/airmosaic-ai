# 配置与调用 GCAM 输出工具

[English](operations.md) | **中文**

本页处理已有输出。准备发行包、编译、生成输入或人工适配模拟时，先阅读[编译与运行](build-and-run_ZH.md)。这些操作没有已注册的执行适配器。

## 环境与参数

在仓库根目录使用已安装项目的 Python 3.10+。按[环境示例](../../../../../config/examples/README_ZH.md)设置既有外部 `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR`、`AIRMOSAIC_AUTH_DIR`。另将 `GCAM_RELEASE_DIR` 指向 Git 和上述三根目录之外的既有发行包。工具不会下载或构建模型。

| 操作 | 依赖及固定输入 |
|---|---|
| 结构 | Rscript、Java、data.table、rgcam；发行包下 `output/database_basexdb`、`database_R/Prov_code_china.csv` |
| 市场/技术提取 | pandas、Java、兼容的 `libs/jars/BaseX-*.jar`；`output/<scenario>/database_basexdb/` |
| 汇总 | pandas；assets data/results 内的市场 CSV |
| 绘图 | Rscript、dplyr、ggplot2、readr、tidyr；市场 CSV，路径不能含逗号 |

R 使用 `--vanilla` 和所选安装的标准库，不传入个人库或启动配置。dry-run 不加载 R 包。另行检查所选发行包的 Java/BaseX/rgcam 兼容性。

结构参数为 `max_memory`（默认 `1g`）和 runner 提供的 `output_dir`；忽略调用者的 `GCAM_BASEX_MAX_MEMORY`。提取参数是平面 JSON，例如 `{"scenarios":"example_scenario","regions":"AH,BJ","sectors":"cement","years":"2021,2035"}`。在个人参数文件中替换为真实选定数据库名；AH/BJ 仅为子集。不存在 `release_dir`、`action` 或技术 `method` 参数。

## 调用与交接

公开示例展示语法，不证明本地数据可用。显式选 stage；以下示例用于社会经济输出分析。综合影响任务应在调用及源路径中一致选择 `04_integrated_impacts`。

```powershell
python -m runtime.cli run-tool gcam_inspect_output_structure --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-inspect.json --dry-run
python -m runtime.cli run-tool gcam_extract_market_sector --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-market.json --dry-run
python -m runtime.cli run-tool gcam_extract_technology_components --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-technology.json --dry-run
```

检查 `can_execute`、`blockers`。预检通过且任务已授权后，去掉 `--dry-run` 执行；结构检查可加 `--timeout 600`。runner 分配 `results/<project_id>/<run_id>/<stage>/<tool_id>/`，通常不传输出参数。

先检查提取结果，再做下游调用。将[汇总](../../../../../config/examples/run-tool/aggregate.json)或[绘图](../../../../../config/examples/run-tool/gcam-plot.json)参数复制到 CONFIG_DIR，替换 `<source_project_id>`、`<source_run_id>` 及情景值。`input_csv` 必须是成功提取的 `market_sector_rows.csv`，不能是回执、汇总或技术 CSV。JSON 路径仅展开 `${AIRMOSAIC_ASSETS_DIR}`，尖括号标签需手动替换。

```powershell
$gcamParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-aggregate.json"
python -m runtime.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamParams --dry-run
python -m runtime.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamParams
$gcamPlotParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-plot.json"
python -m runtime.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamPlotParams --dry-run
python -m runtime.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamPlotParams
```

每次调用有独立 run ID。绘图输出通过 `UNIT_PRICE_OUT_DIR` 注入，调用者设置被忽略。参数或路径被拒绝不授权绕过 runner。

## 检查实际结果

| 工具 | 预期文件 |
|---|---|
| 结构 | `inspect_scenarios.csv`、`inspect_province_top_level.csv`、`inspect_industrial_sector_tree.csv`、`inspect_industrial_cost_nodes.csv` |
| 市场 | `market_sector_rows.csv`、`market_sector_summary.csv` |
| 技术 | `technology_component_rows.csv`、`technology_component_summary.csv` |
| 汇总 | `province_aggregate.csv` |
| 绘图 | `sector_change_2021_2035.png`、`sector_change_weighted_mean.csv` |

检查回执状态、非空预期产物，再读 CSV 字段、情景/年份/部门、重复、缺测、省份及单位。结构查询可逐项失败；runner 会拒绝缺少产物的任务，但内容仍需科学检查。

汇总按 scenario/source/sector/year 报告 `weighted_price`、`quantity_sum`、`province_count`，排除 China/Global。绘图保留 sector_cost 筛选、China/Global 排除、非负权重及零权重时均值回退，年份固定 2021/2035。独立核对分母及零权重，目视检查 PNG 的组别和轴单位。产物存在不证明单位兼容、全国覆盖或收入估计有效。见[方法](../../../../../methods/04_integrated_impacts/gcam_ZH.md)。
