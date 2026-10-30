# 暴露响应数据：版本、来源与可用状态

[English](exposure_response.md) | **中文**

本页用于版本选择与外部来源收据核查。科学解释见[方法](../../../../../methods/04_integrated_impacts/health_impacts_ZH.md)。共享版本相对 `AIRMOSAIC_ASSETS_DIR` 存放：`data/04_integrated_impacts/ExposureResponse/<version>/`。ER 原始资料与 GBD 基线死亡率分开，取得其中一项不代表取得另一项。读取技能不能自动触发下载。

## 已取得的来源记录（2026-10-29）

| 外部版本 | 实际内容与来源 | 可用状态 |
|---|---|---|
| `gemm-2018-c0640d8-20261029` | `gemm_fit_parameter_cells.csv`：作者工作簿参数页 988 个非空单元格，保留坐标、值和公式文本；`provenance.json`。[固定作者版本](https://github.com/mszyszkowicz/DataGEMM/tree/c0640d86a852e2e3565392ba014964bd43edb8ff)，`GEMM Calculator (PNAS)_ab.zip` → `GEMM Calculator (PNAS)_ab.xlsx` → `GEMM fit parameters`。 | 已取得真实拟合参数单元格；尚非规范化或验证后的 RR 曲线。 |
| `who-hrapie-2013-pm25-20261029` | `loglinear_parameters.csv`：一条实际建议，RR **1.062**，95% CI **1.040–1.083**，每 **10 µg/m³**，年均 PM2.5、**30+** 自然原因死亡、合并性别。[WHO 2013](https://iris.who.int/handle/10665/153692)表 1 印刷页 5；[HRAPIE 作者总结表 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4480843/)交叉核实。 | 历史复现/敏感性入口；仍需任务明确参考浓度。 |
| `who-hrapie2-2025-pm25-20261029` | `loglinear_parameters.csv`：RR **1.10**，95% CI **1.06–1.13**，每 **10 µg/m³**，年均 PM2.5、**A00–R99** 自然死亡、成人、合并性别。[WHO 2025 官方记录](https://www.who.int/publications/i/item/9789289062633)，表 2 印刷页 14/PDF 第 22 页，成人说明印刷页 13/PDF 第 21 页；保留来源许可页与相关两页文本及哈希。 | 新 HIA 可考虑的当前指南入口；仍需明确成人最低年龄与参考浓度。 |

WHO 2025 原版报告可从 [Swiss TPH 机构托管副本](https://www.swisstph.ch/fileadmin/user_upload/SwissTPH/Institute/Ludok/Aktuelle_Berichte/WHO2025_HRAPIE-2_UpdatedGuidanceCRFunctionsHRAAirPollution.pdf)取得，已核实 ISBN 9789289062633、标题与版权。表 2 建议的圆整值 **1.10/10** 不同于原始荟萃分析森林图的 **1.095/10**、附录 1 的 **1.046/5**。保持所选记录的精度与 CI 配对，不能与双污染物调整例子混用。本记录不采用臭氧函数。

2025 建议的 **5–70 µg/m³** 是 HRA 人群平均/中位暴露范围（页 13），不是通用逐格上限。纳入研究多数成人为 25+，但 WHO 明确最低成人年龄取决于人口/死亡数据与地区；不能静默沿用 2013 的 30+。地区迁移、高暴露与人口适用性需论证。增量 RR 本身不提供生物学阈值，必须声明参考浓度及低于参考时的处理；5 µg/m³ 指南值不自动等于 TMREL。

## GEMM 尚待解决的事项

[原文的数据存放声明](https://doi.org/10.1073/pnas.1803222115)指向作者仓库。固定 commit：`c0640d86a852e2e3565392ba014964bd43edb8ff`。参数块包括 NCD+LRI、IHD、stroke、COPD、lung cancer、LRI；包含/排除中国队列；25+ 总体和到 80+ 的细年龄。这些替代口径不能混合或加总。

仅检查并保留参数工作表单元格，未读取基线、人口和暴露工作表数值。收据记录源 ZIP/工作簿哈希，但未保留整工作簿，因为其包含基线/暴露页。希腊参数标题是绘图对象而非单元格文本，系数列映射尚未确认。源年龄标签 `30-35` 与 `35-39` 重叠，应保留证据，在核实源/作者说明前停止年龄规范化。排除中国的 LRI 参数含同页公式引用，原样保留且不执行。这些是停止条件，不能静默推断。没有伪造 GEMM 置信限或指定浓度风险；标准误单元格不是 RR 置信边界。尚未取得完整 IER 数据。

## 许可与存储

固定 DataGEMM 仓库根未发现 LICENSE；公开可见不证明可再分发。本研究抽取仅存外部，再分发前审查权利。本轮未确认 2013 报告的再分发许可。2025 报告标明 **CC BY-NC-SA 3.0 IGO**：非商业使用、署名、相同方式共享、不得暗示 WHO 背书或使用其标志，第三方权利需单独检查。外部页文本保留该声明。Git 中不包含原始 PDF、工作簿或参数表；超出许可的使用需另行审查。通用字段和来源说明不能替代下载资料的许可。

## 小型系数字段与只读检查

`loglinear_parameters.csv` 字段：`parameter_id`、`pollutant`、`exposure_metric`、`concentration_unit`、`endpoint`、`age_min_years`、`age_max_years`（上界开放时留空）、`sex`、`function_type`、`rr`、`rr_lower`、`rr_upper`、`ci_level`、`increment`、`source_url`、`source_version`、`source_locator`；未定成人最低年龄另用 `age_rule=adult_task_selection_required`。`provenance.json` 记录来源/版本、许可、文件 SHA256、确切适用范围，以及显式反事实对象（`value`、`unit`、`status`、`meaning`）。待选参考使用 null `value` 与 `status=task_selection_required`，不能自动改成零。

从仓库根执行，先选外部版本：

```sh
python skills/model/04_integrated_impacts/health_impact_analysis/scripts/validate_loglinear_er.py "<external-version-directory>" --assets-dir "<external-assets-root>"
```

仅需 Python 标准库。该直接调用的只读辅助程序验证哈希、必需字段、RR/CI/增量顺序与有限性、来源一致性，以及年龄/参考缺口是否显式记录；只接受本页限定的合并性别自然原因年均 PM2.5 系数。它不是已注册工具、转换器、GEMM 校验器或死亡计算器；成功仍返回 `scientifically_approved=false`、`health_adapter_executable=false`。失败退出码 2；输入缺失/源不匹配必须修正后才能适配任务副本。程序不读取暴露、人口或基线死亡率。

外部收据只是获取记录，不是晋升为已验证数据集。任何授权计算前阅读[操作](operations_ZH.md)与[输入要求](data_requirements_ZH.md)。

必须显式传入 `--assets-dir` 或设置 `AIRMOSAIC_ASSETS_DIR`；版本必须是上述 ER 目录的直接子目录。拒绝链接/目录联接、Git 祖先和配置/认证目录。失败输出只含错误类型，不回显真实路径；此有界检查不替代 run-tool 或科学审查。
