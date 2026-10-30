---
name: gcam-data-extraction
description: Extract market or technology rows from existing GCAM databases, aggregate province market rows, and plot the fixed comparison through reviewed run-tool adapters.
---

# 提取与比较 GCAM 结果

[English](SKILL.md) | **中文**

已实现的 ID 为 `gcam_extract_market_sector`、`gcam_extract_technology_components`、`gcam_aggregate_provinces`、`gcam_plot_sector_change`。[操作参考](../references/operations_ZH.md)提供准确依赖、平面 JSON 参数、预检/执行调用和产物。

显式声明情景、地区、部门和年份。列表使用逗号分隔字符串；技术组件工具没有 `method` 参数。检查单位与行覆盖后，才把成功的市场 CSV 交给汇总或绘图。每次调用有独立 run ID，不会自动串联。

汇总排除 China/Global，加权价不证明全国覆盖完整。绘图固定比较 2021/2035，并保留 sector_cost 筛选和权重回退规则。改变年份或查询逻辑需要另行审查人工适配。

按需读：[价格/数量查询](references/xquery-patterns-price-quantity.md)、[技术查询](references/xquery-patterns-technology-inputs.md)、[单位兼容](references/output-unit-compatibility.md)、[价格解释](references/price-unit-interpretation.md)、[技术组件](references/technology-component-logic.md)、[单位价案例](references/unit-price-workflow-as-example.md)。[方法](../../../../../methods/04_integrated_impacts/gcam_ZH.md)解释提取量的研究含义。
