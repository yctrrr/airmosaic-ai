---
name: gcam-output-structure
description: Inspect the fixed GCAM BaseX output layout and query artifacts through run-tool before scoped extraction.
---

# 检查 GCAM 输出结构

[English](SKILL.md) | **中文**

`gcam_inspect_output_structure` 执行固定 R 检查序列。参数仅有 `max_memory`（默认 `1g`）及运行器提供的 `output_dir`；没有 action/scenario/region/sector 查询选择参数。数据库布局是 `${GCAM_RELEASE_DIR}/output/database_basexdb`，另需 `database_R/Prov_code_china.csv`，与 Python 提取器的逐情景布局不同。

按[环境、调用与产物检查](../references/operations_ZH.md)操作。核对四个 CSV 及其查询内容；脚本内部可能捕获单项查询失败，进程完成不足以说明检查成功。

按需读取：[XML 路径](references/xpath-structure-guide.md)、[自定义查询模板](references/xquery-csv-templates.md)、[单位](references/output-price-quantity-units.md)、[省份映射](references/province-region-mapping.md)。自定义查询需另行审查并适配任务副本；参考内容不是额外 runner 参数。结果解释见 [GCAM 方法](../../../../../methods/04_integrated_impacts/gcam_ZH.md)。
