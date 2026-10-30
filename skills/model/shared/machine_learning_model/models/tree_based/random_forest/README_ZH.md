# 随机森林回归

[English](README.md) | **中文**

科学选择见[随机森林方法](../../../../../../../methods/shared/machine_learning_model/models/tree_based/random_forest/README_ZH.md)。

明确森林计算预算和树复杂度参数，按已审核留出设计比较森林候选与基线。

R 使用 `regr.ranger`，示例参数为 `num.trees`、`mtry`、`min.node.size`、`max.depth`、`sample.fraction`、`replace`；Python 使用 `random_forest`，参数为 `n_estimators`、`max_depth`、`min_samples_leaf`、`max_features`。两条路径均限制运行线程，参数映射和随机种子不保证跨语言数值等价。

## 配置与调用

先准备[对应语言环境](../../../references/operations_ZH.md)和[共同审核流程](../../../references/planning_ZH.md)；Python 另见[依赖及任务契约](../../../references/python-path_ZH.md)。以下命令从仓库根运行。

R：[完整任务](../../../../../../../config/examples/machine-learning-model/r/random_forest.synthetic.json)、[runner 参数](../../../../../../../config/examples/run-tool/ml-model-r-random-forest.json)。

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/ml-model-r-random-forest.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/ml-model-r-random-forest.json --timeout 180
```

Python：[完整任务](../../../../../../../config/examples/machine-learning-model/python/random_forest.synthetic.json)、[runner 参数](../../../../../../../config/examples/run-tool/ml-model-python-random-forest.json)。

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-random-forest.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-random-forest.json --timeout 180
```

示例只用于获授权的固定合成回放。Python 示例不计算贡献；R 树/森林示例保留当前 R 契约要求的置换方法。除仅基线任务外，候选仍与均值基线比较，最终选择基线也属于正常结果。预检不读取数据行或证明依赖可用；实际执行按三根目录及结果范围规则保存新产物。真实数据不能直接沿用技术回放设置。

## 实现位置与检查

- R：[公共拟合](../../../scripts/r/models/fit.R)、[留出评估](../../../scripts/r/common/evaluate.R)。
- Python：[模型构造与公共预处理](../../../scripts/python/models/regression.py)、[运行与验证](../../../scripts/python/run_regression.py)。

从 `artifacts.json` 查找候选、指标、预测、预处理和重载检查。核对实际样本数、候选学习器及参数，独立重算留出指标；不能仅凭退出码或模型文件存在验收。此目录未复制训练代码，也未新增工具 ID。返回[模型分类](../../README_ZH.md)。
