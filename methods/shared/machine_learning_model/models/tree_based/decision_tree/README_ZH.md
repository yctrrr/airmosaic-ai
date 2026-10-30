# 决策树回归

[English](README.md) | **中文**

单棵树把变量空间划分为局部区域，规则可以检查，但小幅数据变化也可能改变划分。结合噪声、独立样本支撑及应用域覆盖，约束深度、节点或叶样本支撑和剪枝复杂度。使用开发期证据选择这些控制项。拟合树中的分裂表示预测关联，不等同于因果机制。

参数理由和文献依据见[模型比较](../../README_ZH.md)。

R 与 Python 暴露的控制项不同，需要分别遵循操作契约；数值相同不代表两棵树等价。 配置、代码调用及当前检查见[对应技能](../../../../../../skills/model/shared/machine_learning_model/models/tree_based/decision_tree/README_ZH.md)。

使用[公共评估设计](../../../evaluation_ZH.md)，在生成实验代码前提交[建模计划](../../../../model_planning_ZH.md)。
