---
name: gcam-data-extraction
description: 通过注册工具提取既有市场、部门及技术组成记录并进行省级汇总；绘图比较固定年份，其他查询需领域适配。
---

# GCAM 结果提取

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`gcam_extract_market_sector`、`gcam_extract_technology_components`、`gcam_aggregate_provinces` 及 R 工具 `gcam_plot_sector_change` 均接入执行器。

## 工作目录与认证

遵守[共享存储约定](../../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../../harness/usage/run-tool.md)。仓库外三个已存在根目录相互独立：`AIRMOSAIC_ASSETS_DIR` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密设置和显式任务参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态。密码和令牌留在秘密管理器，不读取或分享凭据及浏览器配置内容。命令从仓库根目录使用安装项目的解释器运行；执行器自动分配 `results/<project_id>/<run_id>/<stage>/<tool_id>/`，没有需要时省略输出参数。个人配置不自动加载。直接运行脚本会绕过检查；执行器不是操作系统沙箱。

## 用途

两个 Python 工具从已有数据库提取记录，第三个汇总已有表格。只有提取工具接受情景、地区、部门和年份筛选；汇总只接受 `input_csv`。排放或能源查询族、单位价格选取及科学解释需要明确适配，不存在通用动作接口。

## 依赖

显式配置 `GCAM_RELEASE_DIR`，放在仓库及三类个人根之外。提取需要 pandas、本地 Java、兼容的 `libs/jars/BaseX-*.jar` 和 `${GCAM_RELEASE_DIR}/output/<scenario>/database_basexdb/`。模型资源作为逻辑只读输入，执行器不是操作系统只读沙箱。汇总需要 pandas 及工作区 `data/` 或 `results/` 内的已有表。

提取的 `scenarios`、`sectors` 使用逗号分隔字符串，同时限定 `regions`、`years`，因为原默认值可能包含全国、多省份和多年。执行器分配 `out_dir`；参数名以真实声明为准，不虚构动作字段。

## 工具编号与输出

| 工具编号 | 调用方参数 | 任务目录中的文件 |
|---|---|---|
| `gcam_extract_market_sector` | `scenarios`、`sectors`，并限定 `regions`、`years` | `market_sector_rows.csv`、`market_sector_summary.csv` |
| `gcam_extract_technology_components` | 同上 | `technology_component_rows.csv`、`technology_component_summary.csv` |
| `gcam_aggregate_provinces` | `input_csv` | `province_aggregate.csv` |
| `gcam_plot_sector_change` | `input_csv`，可选 `sectors`、`scenarios` | `sector_change_2021_2035.png`、`sector_change_weighted_mean.csv` |

列表是逗号分隔字符串，不是数组。年份为四位数字，情景为安全标识。`out_dir` 由执行器补齐，技术工具没有 `method` 参数。省级汇总排除全国和全球行，按情景、来源、部门、年份输出 `weighted_price`、`quantity_sum`、`province_count`，不自动验证单位或完整全国覆盖。

绘图要求工作区缓存或输出中的输入路径，且路径不含逗号。执行器将输出映射到子进程 `UNIT_PRICE_OUT_DIR`，忽略调用方同名值。R 使用 `--vanilla`，从所选标准库加载 dplyr、ggplot2、readr、tidyr。预检不验证包加载，实际执行检查命名空间及两份产物。年份固定为 2021/2035；默认值和人工适配见[模型指南](../../../../../harness/usage/model-analysis.md)。

## 参数示例及交接

[市场示例](../../../../../config/examples/run-tool/gcam-market.json)和[技术示例](../../../../../config/examples/run-tool/gcam-technology.json)：

```json
{"scenarios":"example_scenario","regions":"AH,BJ","sectors":"cement","years":"2021,2035"}
```

将 `example_scenario` 替换为已有情景。AH/BJ 只是两个省份，不代表全国。真实任务使用个人配置目录内已核对的参数；报告全国前核验完整省级覆盖。

```powershell
python -m airmosaic.cli describe-tool gcam_extract_market_sector
python -m airmosaic.cli run-tool gcam_extract_market_sector --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-market.json --dry-run
python -m airmosaic.cli run-tool gcam_extract_technology_components --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-technology.json --dry-run
```

预检和授权满足后去掉 `--dry-run` 执行，每次调用有独立运行编号。市场任务状态及内容通过后再交给汇总。[汇总示例](../../../../../config/examples/run-tool/aggregate.json)中的 `<source_run_id>` 替换为成功市场任务的真实编号：

```json
{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/results/<source_project_id>/<source_run_id>/01_socioeconomic_natural_change/gcam_extract_market_sector/market_sector_rows.csv"}
```

将已解析的非秘密参数存为个人配置目录中的 `gcam-aggregate.json`：

```powershell
$aggregateParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-aggregate.json"
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $aggregateParams --dry-run
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $aggregateParams
```

JSON 路径只展开 `${AIRMOSAIC_ASSETS_DIR}`；`<source_run_id>` 是需人工替换的说明。不能传入运行记录、工具外壳或技术组成表作为汇总参数。不自动串联工具、发布缓存或完成科学验收。

## 绘制已核验的市场输出

[绘图示例](../../../../../config/examples/run-tool/gcam-plot.json)也需替换源运行编号和情景。保留源表，核对两年、部门、省级覆盖和单位，将参数存入个人配置目录：

```powershell
$plotParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-plot.json"
python -m airmosaic.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $plotParams --dry-run
python -m airmosaic.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $plotParams
```

原有 `sector_cost` 筛选、全国及全球排除、非负权重和零权重均值回退保持不变。其他年份、样式或算法需人工适配并另行验证。不得使用省级汇总表或技术组成记录作为绘图输入。

## 代理执行边界

通过执行器使用四个注册编号。工具或路径被拒绝不授权直接执行 Python 或 Java。预检核对 `can_execute`、`blockers`，执行核对进程状态和真实产物。单位、正或零权重、省份覆盖、方法解释和额外查询逻辑另核。不将提取价格直接认定为收入或已验收的全国单位成本。

## 参考资料

- `references/xquery-patterns-price-quantity.md`：价格、数量查询。
- `references/xquery-patterns-technology-inputs.md`：技术组成查询。
- `references/unit-price-workflow-as-example.md`：单位价格示例。
- `references/output-unit-compatibility.md`：单位兼容性。
- `references/price-unit-interpretation.md`：价格解释及部门差异。
- `references/technology-component-logic.md`：技术成本组成。

数据与结果按[资产目录与复核入库规范](../../../../../harness/assets_ZH.md)管理：数据按阶段、实际名称和版本共享；结果按项目及运行归集。跨阶段引用同一数据，复用入库需人工批准。
