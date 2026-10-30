# 随机森林回归

[English](README.md) | **中文**

随机森林平均多棵随机化树，相较单棵树可降低不稳定性。分裂时变量抽样、每棵树的样本抽取及树复杂度共同影响多样性和局部拟合。增加树数主要改善数值稳定性，不能修复泄露、样本依赖或外推不足。应在预定验证设计下检查预测和解释的稳定性。

参数理由和文献依据见[模型比较](../../README_ZH.md)。

R 使用 ranger，Python 使用 scikit-learn，须分别理解参数含义、范围和随机种子处理。 配置、代码调用及当前检查见[对应技能](../../../../../../skills/model/shared/machine_learning_model/models/tree_based/random_forest/README_ZH.md)。

使用[公共评估设计](../../../evaluation_ZH.md)，在生成实验代码前提交[建模计划](../../../../model_planning_ZH.md)。
