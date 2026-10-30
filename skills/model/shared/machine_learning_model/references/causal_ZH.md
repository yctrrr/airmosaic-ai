# DAG与连续处理PLR

[English](causal.md) | **中文**

实现前先采用[因果设计方法](../../../../../methods/shared/machine_learning_model/causal_ZH.md)，明确处理、结果、时序、物理机制、混杂、备选 DAG、重叠及敏感性检查。图结构有效不证明因果识别成立。

R [`causal/causal.R`](../scripts/r/causal/causal.R) 由 `analysis=causal_plr` 选择，共享目标与准备模块，替代预测的拟合/评估/解释分支。要求声明 DAG、有依据的人工调整集且等于 `features`、一个数值处理、单位、处理尺度、恰好一个辅助模型候选、`missing.policy=drop` 及六项有依据的假设声明。不能仅为通过验证而勾选假设。

保留的训练和验证池合并交叉拟合，测试行不参与。采用 2–10 折且至少 `max(30,10*folds)` 行；分组模式要求至少 `max(5,folds)` 组并声明组间独立。这些实现保护不证明有效样本量充足或因果设计成立。[R操作](operations_ZH.md#6-因果与复现选项)保留完整调用/配置、系数单位定义及输出角色。通过 `artifacts.json` 读取效应、残差、折号、辅助模型和 DAG，并说明识别限制。Python 预测候选不提供该 R PLR 分支。
