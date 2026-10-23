# 空间清单重建与对齐：方法目录

**步骤**：02 排放清单。**状态**：仅方法说明；无具体数据、代码或执行入口。

## 方法选择顺序

1. 确定点源、面源、行政区与网格之间的空间映射方法。
2. 讨论投影、网格方向、边界、空间分辨率与变量单位的一致性要求。
3. 选择空间权重、缺失/零权重和回退策略，说明适用条件。
4. 设计分配前后总量守恒、重复源、有效范围及跨尺度比较检查。
5. 为下一步讨论时间分配、垂直分配和化学物种映射；总量与浓度采用不同聚合方法。

## Skill 与交接

对应[排放方法 skill](../../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md)及[输入方法 skill](../../skills/data_acquisition/02_emission_inventory/inventory-input-methods/SKILL.md)。与[排放核算](emission_accounting.md)共用边界和单位约定；交接方法选择、守恒和映射契约，不附本地数据、脚本名称、实现参数或源码指纹。

## 阶段与 Skill 映射

主目录：02_emission_inventory；适用阶段：02_emission_inventory。对应 [inventory-input-methods](../../skills/data_acquisition/02_emission_inventory/inventory-input-methods/SKILL.md)、[emission-inventory-methods](../../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
