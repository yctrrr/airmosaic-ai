---
name: mlr3-modeling
compatibility: "R; mlr3; rpart; automatic tuning additionally requires mlr3tuning, paradox and future"
metadata:
  version: "1.1.0"
  reviewed: "2026-10-30"
description: 在经审查的 R 代码中配置 mlr3 任务、学习器和验证，并跟踪外部 ml-mlr3 参考项目。
---

# 使用 mlr3 框架

[English](SKILL.md) | **中文**

这是框架操作说明。`mlr3_workflow_reference` 已列入目录，但不能通过 run-tool 执行。支持的数值回归使用[回归技能](../../../SKILL_ZH.md)及 `ml_regression_workflow`。

## 准备与配置

使用 R、`mlr3` 和所选学习器后端。合成示例需要 `rpart`；学习型预处理使用 `mlr3pipelines`，调参需合适版本的 `mlr3tuning`/`paradox` 及明确预算。

写明目标、样本单位、特征和类型、预测时点可用性、划分、指标方向及资源预算。分类任务还需声明类别水平、正类和概率或阈值决策。

在任务环境中检查可用接口：

```r
stopifnot(requireNamespace("mlr3", quietly = TRUE))
print(packageVersion("mlr3"))
print(mlr3::mlr_learners$keys())
learner = mlr3::lrn("regr.rpart")
print(learner$packages)
print(learner$param_set$ids())
```

## 使用代码

[合成回归与分类示例](examples/basic-model-use_ZH.md)提供完整 R 代码，包含 Task、三折开发期交叉验证、拟合及新数据预测。输入全部在内存中合成，不写文件；这些是直接 R 示例，不是注册工具。

1. 创建适当的 Task 和学习器，保留声明的样本角色与划分身份。
2. 将拟合型填补、编码、缩放和筛选放入重抽样图。
3. 比较基线与有界候选，内层调参与外层性能评估分开。
4. 冻结设置，评估最终留出，并对新输入复用已拟合预处理及学习器。

图、调参和最终拟合细节见[操作与验证](references/workflow.md)。反复选型后再次交叉验证，不会形成独立测试。

[自动调参路径](../../../references/automatic-tuning_ZH.md)补充具体直接 R 助手和[合成脚本](examples/automatic-tuning.R)：传入分组折、显式搜索范围、评估/拟合预算并隔离最终测试。所检查默认环境仅通过基础 R 契约检查，完整调参示例还需补齐依赖后验证。已注册工具仍使用原固定候选契约。

## 检查与保存

检查失败折、有限预测、样本键和目标单位；概率输出核对类别顺序及行和。在新的外部项目结果目录保存学习器或图、设置、划分键、预测、指标和依赖版本。读回模型，在相同的整理后输入上比较预测。

通用框架代码不继承 run-tool 的路径及记录处理。项目输出遵循[资产规范](../../../../../../../harness/assets_ZH.md)。[方法选择](../../../../../../../methods/shared/machine_learning_ZH.md)说明何时采用表格学习；[上游记录](UPSTREAM.md)记录外部参考版本，不是自动同步服务。
