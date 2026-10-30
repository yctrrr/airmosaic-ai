# 回归任务配置

[English](README.md) | **中文**

这些是[回归技能](../../../skills/model/shared/machine_learning_model/SKILL_ZH.md)的非秘密任务设置，不是执行器参数封装。`config/examples/run-tool/` 另行提供输入与任务配置路径对象。

| 示例 | 含义 |
|---|---|
| [aq-bench-prediction.json](aq-bench-prediction.json) | 数值型站点目标、显式特征与发布划分；有界预测示例 |
| [synthetic-causal.json](synthetic-causal.json) | 已知效应的合成处理与结果、声明 DAG 和交叉拟合 PLR |

选定后复制到个人 CONFIG_DIR，只修改已支持字段：目标、单位与定义、特征及排除项、样本键与划分标签、缺失、候选、种子、规模和解释方法。训练集内筛选设为 `feature_selection.mode: train_filter`。因果配置要求人工协变量、完整样本、合适的 DAG 与调整集及声明的假设。自然语言 `requirements` 记录意图，不执行代码或自动选模型。

`output_files` 可在选定输出目录内重命名科学产物，例如：

```json
{"output_files":{"metrics":"statistics/evaluation.json","model":"models/selected.rds"}}
```

`artifacts.json` 固定名称用于本地发现产物。不能使用绝对路径、越界、秘密或内部目录、嵌套仓库及冲突文件名；保留已有产物。具体项目可在执行器参数 JSON 中设置：

```json
{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/AQbench_dataset.csv","task_config":"config/examples/ml-regression/aq-bench-prediction.json","out_dir":"${AIRMOSAIC_ASSETS_DIR}/results/example_project/experiment-a"}
```

先通过 `--project-id example_project --dry-run` 预检该执行器 JSON。省略项目编号则默认使用通用技能结果范围。项目清单不是任务设置，也不会自动加载；公共示例不包含个人路径和生成结果。
