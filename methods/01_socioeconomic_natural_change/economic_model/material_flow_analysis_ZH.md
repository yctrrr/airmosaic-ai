# 物质流分析：实物流量与存量

<!-- README-I18N:START -->

[English](material_flow_analysis.md) | **中文**

<!-- README-I18N:END -->

物质流分析（MFA）以实物单位追踪物质穿过指定系统边界的过程。先确定对象：全国经济的物质流账户、部门或产品链，或特定物质及元素。这些尺度需要不同数据，不能当作覆盖同一批流量的表格直接合并。经济整体物质流账户（EW-MFA）记录国民经济与自然环境、世界其他地区之间的物质交换；更细的过程或特定物质研究还可描述经济内部的转移。[SEEA 物质流账户](https://seea.un.org/en/methodology/other-accounts/material-flow-accounts)与[Eurostat 手册](https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-/ks-gq-18-006)说明经济整体的核算框架。

## 确定边界与平衡关系

绘制流量前，记录物质定义、实物单位、地区、核算期间、系统边界、过程和存量类型。区分开采、进口、中间转移、消费或使用、回收、出口、环境释放和存量增加。内部转移在整个系统边界上相互抵消，但定位部门或过程时不能省略。每条流量都应记录来源和去向，以免同一转移重复计数。

在物质及边界定义一致的前提下，平衡关系为 `投入 + 平衡调整投入 = 产出 + 存量净增加 + 平衡调整产出`。在过程尺度上，化学组成变化，以及选择元素质量还是化合物质量，会影响投入和产出的定义。例如，经济整体物质账户通常需要与氧和水相关的平衡项目；核算残差应作为质量诊断，不能自动分摊到某条流量。[SEEA 技术说明](https://seea.un.org/sites/seea.un.org/files/mfa_final_draft.pdf)区分经济边界流量与经济内部流量；[Eurostat 元数据](https://ec.europa.eu/eurostat/cache/metadata/EN/env_ac_mfa_simsmf_ba.htm)列出官方数据集的物质范围和居民单位口径。

EW-MFA 的国内物质消费指标在其覆盖范围内计算为 `DMC = 国内开采 + 实物进口 − 实物出口`。它描述直接物质使用，不等于完整供应链物质足迹，也不等于年度物质存量变化。估计存量还需物质进入存量、使用寿命和退出的信息。[Eurostat 物质流概览](https://ec.europa.eu/eurostat/en/web/environment/information-data/material-flows-resource-productivity)说明报告的流量与指标。

## 与其他方法衔接

MFA 提供实物账户和系数。实物供给使用表或 IO 环境扩展可沿生产链和最终需求分配物质需求，但必须核查物质与部门映射及重复计量。CGE 可接入物质系数、资源约束或状态变量；MFA 数据本身不能推导价格、替代与收入反应。LCA 可把过程流量用作每单位功能的环境影响评价清单，但还需影响评价模型和不同的产品系统边界。物质质量、排放清单、环境影响及货币成本不能互相等同。参见 [IO](io/README_ZH.md)、[CGE](cge/README_ZH.md)、[SEEA 中心框架](https://seea.un.org/en/methodology/seea-central-framework)与 [ISO 14040](https://www.iso.org/standard/37456.html)。

## 最低检查与报告

检查单位和物质组成、领土与居民单位口径、进出口、回收循环、缺失或估算流量、存量变化，以及各年各地的平衡差。对每个指标报告来源、边界、直接或间接覆盖范围与不确定性。模型使用 MFA 结果时，保留物质与部门映射，并说明实物量是模型约束、校准依据，还是仅在求解后报告。[MFA 技能](../../../skills/model/01_socioeconomic_natural_change/material-flow-analysis/SKILL_ZH.md)提供小型直接脚本计算，但尚未注册为工具。

公开的 [K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)提供先明确边界、再检查质量平衡的工作流参照；本地方法保留更窄且明确的核算方程。
