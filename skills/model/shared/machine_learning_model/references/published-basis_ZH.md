# 正式发表的方法依据

[English](published-basis.md) | **中文**

依据为最终发表文章 **Interpretable machine learning for ambient air pollution modeling: A systemic review**，刊于 *Atmospheric Research* **336**（2026），108869，DOI：[10.1016/j.atmosres.2026.108869](https://doi.org/10.1016/j.atmosres.2026.108869)。

方法对应关系于 2026-10-27 按正式发表版核对。

| 发表内容 | 可复用实现 | 边界 |
|---|---|---|
| 第 4.2 节特征工程 | 训练集内缺失、变异、相关性筛选及 VIF 诊断 | 不自动选择因果调整集 |
| 第 4.3 节与图 2 | 显式处理、结果与调整角色，DAG 检查和交叉拟合 PLR | 识别假设仍为声明，非数据证明 |
| 第 4.4 节与图 3–6 | 性能重要性、ICE/PDP、经验背景排列 Shapley 估计 | 属于预测解释，H 统计量及论文全套图形复现另行适配 |
| 第 5.1–5.2 节 | 明确解释范围、相关特征限制和科学复核 | 更低预测误差不证明因果机制 |

代码独立编写，连续处理的 PLR 得分和样本划分另参照一手的 [DoubleML 模型说明](https://docs.doubleml.org/stable/guide/models.html)及[重抽样说明](https://docs.doubleml.org/stable/guide/resampling.html)。本实现不等同于 DoubleML 软件包，也不声称数值上复现论文估计。

合成演示具有已知的数据生成效应。对观测 AQ-Bench 做因果研究，需要专项因果图、变量、空间相关处理、单位和科学假设；预测示例不会自动启动这项分析。
