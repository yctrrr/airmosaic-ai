# 公共评估与均值基线

[English](README.md) | **中文**

训练均值基线是各数值回归候选共用的评估参照，不作为独立研究模型族。它对每个留出样本预测训练集目标均值，不能用验证集或测试集目标估计该均值。

## 既有 R/Python 行为

- R 在[公共拟合](../scripts/r/models/fit.R)中自动加入 `robust = FALSE` 的 `regr.featureless`。不要把它写入 `models`，也不要传空候选列表。指标由[公共评估](../scripts/r/common/evaluate.R)计算。
- Python 任务 JSON 仍需显式声明 `baseline_mean`，已有模型示例均包含它。[公共构造器](../scripts/python/models/regression.py)使用 `DummyRegressor(strategy='mean')`，[运行入口](../scripts/python/run_regression.py)统一评分并独立复核。本次没有增加自动补入候选的行为。

两条路径保持原选型规则：验证误差最优时，基线也可能被选中。公共对照不限于随机森林，候选标识、参数键及选型计算保持不变。

## 配置、运行和检查

使用任一[已实现模型示例](../models/README_ZH.md)，即可同时得到基线与候选评分。先准备 [R 环境](../references/operations_ZH.md)或 [Python 任务与环境](../references/python-path_ZH.md)，再遵循[计划审核](../references/planning_ZH.md)。

保留一个可选的仅基线 Python 工程检查，归公共评估示例：[任务](../../../../../config/examples/machine-learning-model/python/evaluation/baseline.synthetic.json)、[runner 参数](../../../../../config/examples/run-tool/ml-evaluation-python-baseline.json)。它不是主要模型选择入口。

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-evaluation-python-baseline.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-evaluation-python-baseline.json --timeout 180
```

先检查 `can_execute` 和 `blockers`，再核对实际进程及产物状态。通过 `artifacts.json` 定位候选、按样本键保存的预测和指标，在相同保留样本上独立重算指标并检查模型重载。预览不训练或读取数据行。新结果仍遵循所选 runner 的既有范围。科学比较依据见[评估方法](../../../../../methods/shared/machine_learning_model/evaluation_ZH.md)，不直接沿用工程示例参数。
