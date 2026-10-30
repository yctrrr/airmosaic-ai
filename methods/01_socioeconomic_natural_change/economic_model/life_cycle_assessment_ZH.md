# 生命周期评价：清单与潜在环境影响

<!-- README-I18N:START -->

[English](life_cycle_assessment.md) | **中文**

<!-- README-I18N:END -->

生命周期评价（LCA）将产品系统在规定生命周期内的投入和产出与潜在环境影响联系起来。比较不同系统前，先说明研究问题与**功能单位**。ISO 14040 框架包括目标与范围、生命周期清单（LCI）、生命周期影响评价（LCIA）和解释。单独计算气候指标只覆盖一个影响类别，不能代表完整 LCA。参见 [ISO 14040](https://www.iso.org/standard/37456.html)及 [UNEP 生命周期倡议](https://wedocs.unep.org/items/fcb30686-689c-49fd-afb3-48cf7868cfef)。

## 确定产品系统

明确交付功能单位所需的参考流量、地区与时间、技术、前景和背景过程、截断规则、进口和寿命终点处理，以及联产品分配或系统扩展方法。记录每项过程交换的数据来源和单位。产品比较要求功能等价、边界可比；即使产品的实际物理过程未变，更换清单数据库或分配规则也可能改变结果。

在简单的线性单产出前景模型中，技术圈矩阵 `T` 的行是产品、列是过程，正值表示产出，负值表示消耗的投入。对需求向量 `d`，过程规模满足 `T s = d`。若 `B` 为各过程的基本流，则清单为 `g = B s`；某个明确影响类别的表征因子 `c` 给出 `impact = cᵀ g`。这些方程只演示 LCI 与一个 LCIA 类别。正式评价还需要有依据的数据库、表征方法、分配及结果解释。[Brightway 矩阵说明](https://docs.brightway.dev/en/latest/content/overview/matrix.html)介绍了相应的技术圈、生物圈和表征矩阵。

## 与 MFA、IO 和 CGE 衔接

MFA 在指定系统内追踪实物流量与存量；核对产品和系统边界后，其过程数量可用于编制 LCI。货币最终需求作为起点时，环境扩展 IO 可估算上游需求；过程 LCA 则以过程交换和功能单位为起点，混合方法需要明确映射并检查重复计算。CGE 可提供情景活动、价格或技术变化，但情景输出本身不是 LCA 影响或因果效应。参见 [MFA](material_flow_analysis_ZH.md)、[IO](io/README_ZH.md)与 [CGE](cge/README_ZH.md)。

## 检查与解释

检查产品和基本流单位、适用时的质量与能量合理性、过程完整性、矩阵平衡、所选表征方法对基本流的覆盖，以及清单和分配选择的敏感性。逐个影响类别报告每功能单位的结果和单位，不汇总成未标明含义的数字。潜在影响指标不能直接解释为已观测健康结果或货币成本。[LCA 技能](../../../skills/model/01_socioeconomic_natural_change/life-cycle-assessment/SKILL_ZH.md)演示受限的合成线性计算；正式研究需要独立的数据和审查。

公开的[天工 LCA 技能](https://github.com/tiangong-lca/agent-skills)将清单审阅与模型构建区分，[K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)强调边界与实物流；本地 toy 计算并未使用其数据库或表征因子。
