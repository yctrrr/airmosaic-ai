# 显式固定折数值表格模型

[English](fixed-fold-tabular.md) | **中文**

这些直接调用的 Python 模块需要已审核方案、数值特征、有限目标值、固定的开发集划分和未参与选择的最终测试集。它们不是新注册的 run-tool/MCP 操作，现有注册工具及合成 Transformer 演示仍遵循原契约。

## 传统模型路径

加载 [fixed_fold_regression.py](../scripts/python/models/fixed_fold_regression.py)，依赖 NumPy、scikit-learn、threadpoolctl。`candidates(search_space, n_iter=..., seed=...)` 固定候选参数；`fit_once(X_train, y_train, family=..., parameters=..., seed=..., max_threads=...)` 只拟合一次并返回处理流水线。

支持 `linear_regression`、`decision_tree`、`random_forest`、`histogram_gradient_boosting`。参数需显式提供；直方图梯度提升需指定 `early_stopping=False`，避免内部随机验证替代已审核的划分。填补及线性模型的标准化只使用训练行。调用者分别传入剔除空间缓冲后的训练索引和验证索引，接口本身不划分地理区域。

## 神经网络路径

加载 [tabular_torch.py](../scripts/python/models/tabular_torch.py)，依赖 NumPy 和 CPU PyTorch。输入为数值 `[行, 特征]`；目标、标识、坐标、日期不作为特征，除非逐项批准。特征数量可配置。

- `mlp`：指定 `hidden`、`dropout`、`learning_rate`、`weight_decay`。
- `numerical_tabular_transformer`：指定可被四整除的 `d_model`，以及 `layers`、`dropout`、`learning_rate`、`weight_decay`。采用逐特征线性标记、CLS 读出和预归一化注意力，是受 FT 启发的改写，不代表精确复现发表架构。

```python
fit = neural.fit_tabular(
    X_train, y_train, family=family, config=reviewed_config, seed=seed,
    max_epochs=reviewed_epoch_cap, batch_size=reviewed_batch_size,
    x_validation=X_validation, y_validation=y_validation,
    patience=reviewed_patience, min_delta=reviewed_min_delta,
    max_seconds=reviewed_fit_seconds, max_threads=reviewed_threads,
)
predicted = neural.predict(fit["model"], fit["artifact"]["preprocessing"], X_validation)
neural.save_model(fit["artifact"], fresh_checkpoint)
model, artifact = neural.load_model(fresh_checkpoint, max_threads=reviewed_threads)
```

其中 `neural` 是加载的模块。检查点保存仅由训练集得到的中位数、特征及目标均值和标准差；预测返回目标原单位。缺失目标和训练集中整列缺失的特征被拒绝。最终拟合不传验证集，使用已从开发集选定的训练轮数。多随机种子取平均时，保留每个种子的预测值。

## 控制与检查

调用者应绑定方案、输入和代码哈希；启动进程前记录每次拟合预算，失败计数不退还；限制原生库及 Torch 线程，设置进程硬超时，保留未完成任务且不暗中重跑。助手自身的协作式超时不能代替进程硬超时。参数、轮数和种子只能在开发集内选择。对自行保存且已核对哈希的最终模型，重载后预测全部共同测试行，独立重算原单位 RMSE、MAE、R²，并确认预测一致，不额外拟合。网格输入和各随机种子的预测也需纳入记录。合成实现检查不等于新真实研究已通过验证。
