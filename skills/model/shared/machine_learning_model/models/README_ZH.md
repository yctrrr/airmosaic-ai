# 模型分类

[English](README.md) | **中文**

先选模型族，再选择已经实现的 R/Python 路径。配置和公共计算代码与模型导航分开存放。

| 模型族 | 入口 | 当前状态 |
|---|---|---|
| 线性回归 | [线性回归](linear_regression/README_ZH.md) | Python 预测器；R 适配器未启用 |
| 树模型 | [决策树与随机森林](tree_based/README_ZH.md) | R 和 Python 均提供回归路径 |
| Transformer 软件案例 | [表格、序列、网格及融合](transformer/README_ZH.md) | 直接运行的 Python CPU 合成助手；无真实数据或 run-tool 适配器 |
| 时序模型 | [TimeXer](time_series/README_ZH.md) | 仅外部 Python/PyTorch 使用指导；无 run-tool 适配器 |

[均值基线](../evaluation/README_ZH.md)归公共评估，不作为模型族选择。另见[贡献](../references/contribution_ZH.md)和[因果](../references/causal_ZH.md)。本索引不启用分类、聚类、提升树或其他神经网络训练适配器。

完整任务与 runner 参数仍归 `config/examples/`。注册回归示例回放清单内合成输入，Transformer 助手在内部生成独立输入。数量及上限不规定科学样本或划分。新研究需先[审核计划](../references/planning_ZH.md)。框架接口说明归 [R/mlr3](../frameworks/r/mlr3/SKILL_ZH.md)，公共计算代码保留 `scripts/r/` 和 `scripts/python/`。
