# 模块布局与迁移

[English](layout.md) | **中文**

公开源文件从 `skills/model/shared/ml_regression/` 移至 `skills/model/shared/machine_learning_model/`。原空技能目录及陈旧缓存已清理；本次源文件归并不迁移结果产物。

模型导航现分为 `models/linear_regression/`、`models/tree_based/{decision_tree,random_forest}/` 和 `models/time_series/timexer/`，均值基线归 `evaluation/`。原共享层 `mlr3/` 说明保留到 `frameworks/r/mlr3/`，其参考工具和 TimeXer 参考保留标识且仍不可执行。来源跟踪、示例和元数据均保留。面向研究者的模型族在 `methods/shared/machine_learning_model/models/` 中对应分类。

可执行代码保留 `scripts/r/` 与 `scripts/python/`，公共规划位于 `scripts/common/`。模型族目录提供导航和契约，不复制训练流水线。R 仍自动加入均值基线，Python 仍需显式候选，选型及计算逻辑不变。

| 原相对路径 | 现相对路径 |
|---|---|
| `scripts/run_regression.R` | `scripts/r/run_regression.R` |
| `scripts/lib/io.R` | `scripts/r/common/io.R` |
| `scripts/lib/target.R` | `scripts/r/common/target.R` |
| `scripts/lib/prepare.R` | `scripts/r/common/prepare.R` |
| `scripts/lib/select.R` | `scripts/r/common/select.R` |
| `scripts/lib/evaluate.R` | `scripts/r/common/evaluate.R` |
| `scripts/lib/fit.R` | `scripts/r/models/fit.R` |
| `scripts/lib/reproduction.R` | `scripts/r/models/reproduction.R` |
| `scripts/lib/explain.R` | `scripts/r/contribution/explain.R` |
| `scripts/lib/causal.R` | `scripts/r/causal/causal.R` |
| `scripts/review_plan.py` | `scripts/common/review_plan.py` |

R 模块算法正文保持不变；仅修改入口 source 向量以定位新目录，加载顺序仍是 I/O、目标、选择、准备、拟合、评估、贡献和因果。独立复现函数库仍由调用方显式加载。执行器设置 `AIRMOSAIC_R_ENTRYPOINT`，模块位置相对该入口目录解析。直接调用 R 不代替执行器的任务校验与输出保护。

R 工具 ID 仍为 `ml_regression_workflow`，适配器仍为 `mlr3_regression`，任务结构、默认学习器及 PLR 限制不变。Python 位于 `scripts/python/`，有独立契约、依赖及工具 `ml_python_regression_workflow`，见[实际支持能力](python-path_ZH.md)。经验证的纯 Python 路径不自动要求 R 库。通用规划助手不是数值训练实现。

原 `methods/shared/ml_regression_ZH.md` 科学正文保留在[通用设计](../../../../../methods/shared/machine_learning_model/common_ZH.md)（第1–4、8节及规划）、[模型](../../../../../methods/shared/machine_learning_model/models/README_ZH.md)（第5节）、[贡献](../../../../../methods/shared/machine_learning_model/contribution_ZH.md)（第6节）及[因果](../../../../../methods/shared/machine_learning_model/causal_ZH.md)（第7节），由[索引](../../../../../methods/shared/machine_learning_model/README_ZH.md)导航。通用规划和复现方法保留原位置。
