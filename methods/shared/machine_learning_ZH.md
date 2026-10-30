# 如何选择机器学习方法

[English](machine_learning.md) | **中文**

根据研究问题和数据结构选择模型。熟悉的框架只是实现选择的工具，不能代替科学目标和验证设计。

## 模型需要预测什么？

数值结果适合考虑回归；明确类别适合考虑分类，并关注类别频率、正类和不同误判的代价。序列预测还需明确起点、提前量和信息可获得边界。[回归设计](machine_learning_model/README_ZH.md)与[预测设计](time_series_forecasting_ZH.md)分别展开这些选择。

## 数据有什么结构？

识别重复实体、空间关系、时间顺序和测量支持范围。独立样本表、站点面板和连续序列需要不同抽样与留出设计。先决定新样本与开发数据可能有何不同，再选择模型类别。

## 需要比较什么？

采用可理解的基线和样本能够支持的复杂度。在有意义的比较中保持目标、样本与指标一致，学习型预处理放在训练边界内。开发数据用于选择，冻结留出用于最终评估。

分类需要时检查各类别误差和概率校准，不能只看总体准确率；回归检查目标单位下的误差和残差规律。[mlr3 评估说明](https://mlr3book.mlr-org.com/chapters/chapter3/evaluation_and_benchmarking.html)介绍性能估计与模型比较。

## 解释支持什么？

预测解释描述特定数据与参考条件下的模型。因果效应还需识别假设和相应估计方法，实施前通过[需求驱动设计](requirements_driven_model_building_ZH.md)明确这种区别。

## 进入实现

[回归技能](../../skills/model/shared/machine_learning_model/SKILL_ZH.md)实现有界数值预测及声明 PLR 分支；[mlr3 说明](../../skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL_ZH.md)支持直接使用 R 框架及扩展；[TimeXer 说明](../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL_ZH.md)面向需适配的外部序列模型。依赖、配置和执行状态由各技能维护。
