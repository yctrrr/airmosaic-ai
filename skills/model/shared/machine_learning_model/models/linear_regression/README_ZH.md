# 线性回归

[English](README.md) | **中文**

当获准问题适合比较线性候选时，使用当前普通线性预测器。此路径提供预测和模型检查，不输出系数推断或建立因果识别。

当前 R 适配器未启用线性回归，不能向 R 工具传入 `regr.lm`。Python 使用 `LinearRegression()`，未暴露学习器参数；这里尚未实现正则化变体。

## 配置与调用

先准备 [Python 依赖及任务契约](../../references/python-path_ZH.md)，再遵循[共同审核流程](../../references/planning_ZH.md)。这个预测器不需要 R。科学选择见[对应方法](../../../../../../methods/shared/machine_learning_model/models/linear_regression/README_ZH.md)。以下命令从仓库根运行。

Python：[完整任务](../../../../../../config/examples/machine-learning-model/python/linear_regression.synthetic.json)、[runner 参数](../../../../../../config/examples/run-tool/ml-model-python-linear-regression.json)。

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-linear-regression.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/ml-model-python-linear-regression.json --timeout 180
```

示例只用于获授权的固定合成回放。Python 示例不计算贡献；R 树/森林示例保留当前 R 契约要求的置换方法。除仅基线任务外，候选仍与均值基线比较，最终选择基线也属于正常结果。预检不读取数据行或证明依赖可用；实际执行按三根目录及结果范围规则保存新产物。真实数据不能直接沿用技术回放设置。

## 实现位置与检查

- Python：[模型构造与公共预处理](../../scripts/python/models/regression.py)、[运行与验证](../../scripts/python/run_regression.py)。

从 `artifacts.json` 查找候选、指标、预测、预处理和重载检查。核对实际样本数、候选学习器及参数，独立重算留出指标；不能仅凭退出码或模型文件存在验收。此目录未复制训练代码，也未新增工具 ID。返回[模型分类](../README_ZH.md)。
