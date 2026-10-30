# 配置与适配健康模板

[English](operations.md) | **中文**

## 不执行的接口检查

在仓库根目录：

```sh
python -m runtime.cli describe-tool pm25_hia_calculate_template
python -m runtime.cli describe-tool pm25_hia_visualize_template
```

计算模板为技能目录下 `templates/calculate_pm25_deaths.R`，依赖 data.table；绘图为 `templates/visualize_pm25_deaths.R`，依赖 data.table、ggplot2、sf、RColorBrewer。两者 source 时直接执行，没有 CLI 参数或任务 JSON/YAML 加载器。

## 显式任务配置

输入放在外部 assets，非秘密任务设置放 CONFIG_DIR，适配脚本及结果放新的外部 `results/<project_id>/` 任务目录。直接 R 调用不具备 runner 路径检查或脱敏回执。

| 变量 | 用途 |
|---|---|
| `PM25_HIA_CONC_DIR` | `pm25_annual_<year>.csv`：X_Lon、Y_Lat、concentration |
| `PM25_HIA_POP_DIR` | `Population_g0.1_<year>.Rds`、`Age_Structure_Fraction_g0.1_<year>.Rds` |
| `PM25_HIA_MORT_FILE`、`PM25_HIA_RR_FILE` | 基线死亡率、RR 查询 CSV |
| `PM25_HIA_OUTPUT_DIR` | 显式指定新的外部输出目录 |
| `PM25_HIA_YEARS`、`PM25_HIA_CURVE` | 逗号分隔目标年、曲线名称 |
| `PM25_HIA_POP_FILE`、`PM25_HIA_SHP_DIR` | 绘图人口 RDS、边界目录 |
| `PM25_HIA_PLOT_YEAR` | 单一绘图年，与计算年份分别设置 |

其余字段见[输入要求](data_requirements_ZH.md)。在 `source()` 前仅设置同名 R 变量不足以配置：模板会用 `Sys.getenv()` 覆盖。需设置环境变量或明确修改副本配置。

适配完成且计算已授权后，个人 R 驱动可传入设置并 source 副本：

```r
Sys.setenv(PM25_HIA_CONC_DIR = conc_dir, PM25_HIA_POP_DIR = pop_dir,
           PM25_HIA_MORT_FILE = mort_file, PM25_HIA_RR_FILE = rr_file,
           PM25_HIA_OUTPUT_DIR = result_dir, PM25_HIA_YEARS = target_years,
           PM25_HIA_CURVE = curve_label)
source(adapted_calculation_file)
```

这些 R 字符串由调用者定义，不是已有默认值。完成后以 `Rscript --vanilla <personal-driver.R>` 执行。绘图另设上表三个附加变量并 source 适配绘图文件。`examples/workflow_pm25_hia.R` 仅作示意，路径占位符和 `../../templates/` 路径需按实际工作目录替换。

## 必须适配与检查的假设

当前计算写死 China/Rate 筛选、重写死亡率 `Year`、浓度封顶 200、0.1 舍入、80+ 子组率相加。这些是待审查的实现假设，不能当已验证科学默认。年份筛选必须保留并使用原始年份。细年龄率应按对应人口加权，不能直接相加。明确年龄/性别比例以总人口还是性别人口为分母，再与 Pop 相乘。

核对 RR 参考浓度和范围、病因/年龄匹配、唯一连接键、缺失暴露和排除人口。验证 RR=1 时归因死亡为零，手算小例与适配代码一致。检查 `/100000` 率换算、病因不重复、overall/urban/other 不重叠相加。

计算预期文件为 `pm25_premature_death_grid_<curve>_<year>.csv`、`pm25_premature_death_summary_<curve>_<year>.csv`。核对 Mort 为人数、适配代码中 `MortRate_PM25` 的实际尺度及汇总与格点和。地图需检查单位、范围、人口支持和缺测。保存配置、来源版本和验证结论；文件存在不足以证明计算有效。

模板还会将连接后缺失归因率替换为零。需适配为保留并报告暴露/RR 支持缺失；匹配失败不是零负担的证据。

## ER 选择与停止条件

适配对数线性任务前阅读[实际 ER 来源](exposure_response_ZH.md)，运行其只读系数检查。非秘密任务配置记录源 ID/版本、参考及低于参考规则、确切适用人群、完整病因集、情景估计对象、基线率是基准暴露下观察率还是标准化/参考率，以及暴露支持。源哈希有效不等于科学选择获批。源行缺失、哈希不符、年龄/参数标题歧义、单位未知或暴露统计量错配即停止。目前没有向 R 查询表格式的转换器。

上述两个 `describe-tool` ID 仍为真实目录项，`execution.enabled=false`；不能改用 run-tool 绕过。新增 Python 辅助程序直接调用，没有工具 ID。R 的 `source()` 仍以任务副本适配与审查为前提。模板只计算固定率归因负担；按风险缩放的避免死亡需单独审查任务实现，不能把直接相减标成相同估计对象。

用 `python -m runtime.cli describe-dataset pm25_exposure_response` 查看独立 ER 数据参考；这是详情元数据，不是自动下载器，也不表示采集专用的 `list-datasets` 已提供曲线。
