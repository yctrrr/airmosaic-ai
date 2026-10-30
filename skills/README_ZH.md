# 技能：四个研究步骤中的操作

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

技能说明怎样准备软件和输入、完成操作并检查输出。[方法](../methods/README_ZH.md)解释研究依据，[工作流](../workflows/README_ZH.md)组合数据与技能。

## 找到研究步骤

| 步骤 | 操作覆盖范围 | 数据获取 | 建模与分析 |
|---|---|---|---|
| 01 社会经济与自然变化 | 准备活动、人口和自然条件等上游输入 | [分类](data_acquisition/01_socioeconomic_natural_change/README_ZH.md) | [分类](model/01_socioeconomic_natural_change/README_ZH.md) |
| 02 排放清单 | 选择核算和输入方法，仅提供概念说明 | [分类](data_acquisition/02_emission_inventory/README_ZH.md) | [分类](model/02_emission_inventory/README_ZH.md) |
| 03 大气输送与化学 | 准备大气输入，支持模拟与观测分析 | [分类](data_acquisition/03_atmospheric_transport/README_ZH.md) | [分类](model/03_atmospheric_transport/README_ZH.md) |
| 04 综合影响评估 | 准备结果输入，评估人类或自然影响 | [分类](data_acquisition/04_integrated_impacts/README_ZH.md) | [分类](model/04_integrated_impacts/README_ZH.md) |

跨阶段操作在共享[数据获取](data_acquisition/shared/README_ZH.md)或[建模](model/shared/README_ZH.md)目录维护一份，其他阶段按需引用。

项目维护另设[代理维护类别](agent_operations/README_ZH.md)，统一放在共享目录，不增加研究步骤。

## 确认当前能力

分类页和具体 `SKILL.md` 维护可用操作及状态。阅读所选技能的依赖、配置、实际入口和结果检查，通过[工具查询](../harness/usage/tool-registry.md)查看已注册执行支持及静态前置条件，经审查适配器使用 [run-tool](../harness/usage/run-tool.md)。

详细方法关系保留在 [methods/index.yaml](../methods/index.yaml)。技能文档、参考或模板、可执行登记属于不同对象，应查看所选入口，不能根据文件夹名称推断支持情况。

## 贡献

专属阶段技能保留在主阶段，跨阶段能力放在 `shared`。能力变化时同步双语说明及相应分类或索引，本总览保持研究步骤和范围介绍。

具体操作遵循[技能编写](../harness/skill-authoring_ZH.md)、[注册](../harness/tool-registration_ZH.md)和[资产存储](../harness/assets_ZH.md)规范。
