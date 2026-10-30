# 经济模型及关联的实物核算方法

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

`economic_model` 是本项目组织经济及其资源环境关联方法的导航目录，不表示其中每种方法都是狭义的经济学模型：投入产出（IO）是核算模型；可计算一般均衡（CGE）按指定行为和闭合规则求经济均衡；计量经济学利用数据估计变量关系；物质流分析（MFA）记录实物流量与存量；生命周期评价（LCA）评价产品系统的潜在环境影响。

| 方法 | 主要问题 | 阅读 |
|---|---|---|
| IO | 给定最终需求对应哪些上游生产及实物足迹？ | [投入产出分析](io/README_ZH.md) |
| CGE | 价格、数量、收入和贸易如何在指定冲击下调整？ | [可计算一般均衡](cge/README_ZH.md) |
| 计量经济学 | 观测变化能够支持哪些关联、预测或已识别效应？ | [计量分析](econometrics/README_ZH.md) |
| MFA | 物质如何进入、经过、积存在并离开指定系统？ | [物质流分析](material_flow_analysis_ZH.md) |
| LCA | 指定产品功能与生命周期边界对应哪些潜在环境影响？ | [生命周期评价](life_cycle_assessment_ZH.md) |

这些方法可以共用部门和地区映射，但货币与实物账户、系统边界和假设必须分别核查。方法之间建立数据连接，并不自动产生经济或环境反馈。参见[阶段 01 方法](../README_ZH.md)和[方法索引](../../index.yaml)。[SEEA](https://seea.un.org/en/methodology/seea-central-framework)提供环境经济核算的总体框架；[ISO 14040](https://www.iso.org/standard/37456.html)说明 LCA 框架。

公开技能参照包括以系统边界和质量平衡组织 MFA、IO、LCA 的 [K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)、[天工 LCA 技能](https://github.com/tiangong-lca/agent-skills)、[EconAgentSkills](https://github.com/JonasWeinert/EconAgentSkills)，以及范围只覆盖纯交换经济、比 CGE 更窄的[一般均衡模型构建技能](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md)。方法软件可参考 [pymrio](https://pymrio.readthedocs.io/en/stable/)、[flodym](https://flodym.readthedocs.io/en/latest/)与 [Brightway](https://docs.brightway.dev/en/latest/)。本库技能中的小型脚本是独立演示，不内置这些软件包或数据库。
