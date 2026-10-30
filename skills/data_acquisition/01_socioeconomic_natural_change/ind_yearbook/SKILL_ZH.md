---
name: ind-yearbook
description: Adapt industrial-yearbook regional-sector and product-output R templates to authorized Excel inputs; templates require review and are disabled in run-tool.
---

# 工业年鉴表格整理

[English](SKILL.md) | **中文**

从已有 Excel 整理省份×行业经济指标或省份×产品产量。全国行业表需要另行实现。

## 准备任务副本

使用装有 `data.table`、`readxl`、`stringr` 的 R，以及核对原表的电子表格阅读器。记录版次、实际数据年、授权文件/工作表、单位和行业标准版本。原件保存在外部版本化数据目录；任务规格与映射放在 `AIRMOSAIC_CONFIG_DIR`，工作副本和产物放在新的项目结果目录。

两份 R 模板均需适配：`yearbook_regional_sector_template` 和 `yearbook_product_output_template` 不能通过 `run-tool` 执行。可先查询真实元数据：

```sh
python -m runtime.cli describe-tool yearbook_regional_sector_template
python -m runtime.cli describe-tool yearbook_product_output_template
```

## 适配后仅运行已审核任务脚本

1. 在电子表格阅读器中核对授权代表表。地区表预期位于 `中国工业统计年鉴{edition}（Excel）/3分地区数据/`，产品表位于各版次下的 `工业产量/` 或 `分地区工业主要产品产量/`。
2. 将所需[地区模板](templates/process_regional_sector.R)或[产品模板](templates/process_product_output.R)复制到任务工作区，载入前审核。当前文件含未完成/无效表达式及简化处理，不是可直接运行的方案。另行修复任务副本并验证语法，再以合成表测试。
3. 在审核后的副本中明确输入文件、版次范围、工作表、映射和新输出目录。[config.yaml](templates/config.yaml) 仅为声明：模板不会自动读取或展开占位符。已有 examples 只用于说明结构。
4. 逐项检查写入位置：地区模板即使设置最终 `output_dir`，逐年处理仍向版次目录写入；产品模板向版次目录及 `root` 写入，没有独立输出目录参数。使用任务工作副本，或先适配所有写入；只设置一个最终目录不能保护原件。
5. 检查表头/单位、`地区` 面板边界、续表、数值转换失败、版次—数据年、排除表及行业代码。模板假设数据年=版次−1，必须对照实际表格验证。
6. 导出清洗表、来源/版次清单、映射、转换问题、覆盖缺口及填补规则；独立核对若干原表单元格和年/地区/行业/产品合计。缺失不自动当零；插值、外推、补充来源需在任务中单独论证并实现。

布局和历史设计详见[处理技术](references/processing-guide.md)、[流水线蓝图](references/pipeline_blueprint.md)、[行业匹配](references/industry_code_matching.md)、[编码修复](references/encoding_repair.md)。历史长参考保留原语言。科学选择与解释见[年鉴方法](../../../../methods/01_socioeconomic_natural_change/statistical_yearbooks_ZH.md)。
