# 树模型回归

[English](README.md) | **中文**

决策树按变量划分样本，在叶节点给出局部预测。随机森林组合多棵随机化的树并平均预测。两者属于同一模型族，但复杂度和稳定性的控制方式各有区别。

| 模型 | R 学习器 | Python 学习器 | 配置与调用 |
|---|---|---|---|
| 单棵决策树 | `regr.rpart` | `decision_tree` | [决策树](decision_tree/README_ZH.md) |
| 随机森林 | `regr.ranger` | `random_forest` | [随机森林](random_forest/README_ZH.md) |

两者复用各语言的数据准备、拟合和[公共评估](../../evaluation/README_ZH.md)，这些导航目录不复制训练代码。R/Python 参数和随机种子不代表数值拟合一致。选择参数前先审查[科学比较方法](../../../../../../methods/shared/machine_learning_model/models/tree_based/README_ZH.md)及[建模计划](../../references/planning_ZH.md)。返回[模型分类](../README_ZH.md)。
