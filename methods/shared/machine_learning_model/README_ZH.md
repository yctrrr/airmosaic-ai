# 机器学习模型方法

[English](README.md) | **中文**

回归用于描述一组变量与数值结果之间的关系。一项有用的研究，需要先明确问题，将模型开发与评估分开，再说明结果能够回答什么。本说明按这个顺序展开；配置和代码见[回归技能](../../../skills/model/shared/machine_learning_model/SKILL_ZH.md)。

先阅读[通用设计](common_ZH.md)，明确问题、变量角色、产品来源、抽样、预处理、时空验证及结果审查，再选择[模型](models/README_ZH.md)、[预测贡献](contribution_ZH.md)或[因果设计](causal_ZH.md)。贡献解释拟合模型的预测；因果效应需要单独论证识别设计。

模型目录按[线性回归](models/linear_regression/README_ZH.md)、[树模型](models/tree_based/README_ZH.md)和[时序模型](models/time_series/README_ZH.md)分类，决策树与随机森林同属树模型。训练均值基线归[公共评估参照](evaluation_ZH.md)，不作为独立研究模型分类。方法页说明科学选择；对应技能页负责配置、代码和实际执行状态。

跨任务的 [Transformer 架构方法](models/transformer/README_ZH.md)解释注意力及研究设计，[数据说明](models/transformer/data_ZH.md)区分表格、序列、网格和多源输入。本项是方法参考，不是新启用的模型，已有专门入口保留原位置。

[规划方法](../model_planning_ZH.md)、[需求驱动建模](../requirements_driven_model_building_ZH.md)及[复现方法](../model_reproduction_ZH.md)各自保持权威。先设计科学问题，再由[技能](../../../skills/model/shared/machine_learning_model/SKILL_ZH.md)选择 R 或 Python 实现。第02阶段仅可讨论概念方法。
自动选择参数时，阅读[调参方法](tuning_ZH.md)，明确仅开发数据搜索、分组验证、最终重拟合与测试隔离；其中链接的技能说明维护实际配置和运行限制。
