---
name: model-reproduction
description: 比较冻结的回归预测，按样本键重算指标，诊断来源、预处理和划分差异，并保留两套结果。
---

# 对照已有模型结果

[English](SKILL.md) | **中文**

使用经过审查的直接入口 `scripts/compare_existing.py`，它没有注册为 run-tool 或 MCP 执行 ID。[方法说明](../../../../methods/shared/model_reproduction_ZH.md)解释可比性和可靠性判断。

## 配置

使用已安装的项目 Python 环境，按[环境示例](../../../../config/examples/environment.ps1)设置三个既有且分离的 ASSETS/CONFIG/AUTH 根。CSV/JSON 比较不需要模型框架。

将[完整任务](../../../../config/examples/model-reproduction/compare-existing.json)复制到个人配置，再修改：

| 字段 | 含义 |
|---|---|
| `project_id`、`target` | 共用项目、目标身份与单位 |
| `candidate.root`、`reference.root` | 该外部项目中两个独立冻结结果目录 |
| `manifest`、`prediction_origin` | 文件与哈希清单，以及预测来源 |
| `models[].id` | 显式配对的模型编号 |
| `predictions`、`id_column`、`truth_column`、`prediction_column` | CSV 及列映射 |
| `reported_metrics` | 可选的来源 JSON 及指标指针 |
| `tolerances` | 观测、指标的绝对与相对比较容差 |
| `output_files` | 新比较目录内可选的产物名 |

字段见[结构](../../../../catalog/schemas/model-reproduction-task.schema.json)。来源审计表是可选的外部证据，脚本不会自动审查任意代码。

## 运行合成示例

从仓库根目录执行：

```sh
python skills/model/shared/model_reproduction/scripts/make_synthetic_fixture.py --fixture-id synthetic_v1 --execute
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo --execute
```

首条命令仅创建合成证据，第二条预检清单与配置但不解析预测，第三条进行比较。重复运行使用新名称并更新匹配的任务副本。`--out-dir` 可在项目结果根下指定新目录。

## 检查结果

执行前应为 `preflight_passed`，执行后为 `completed`。查看 `artifacts.json`、比较报告、自身队列与共同样本指标、未匹配标识和来源保留证据。五行示例预期候选 RMSE/MAE/R² 为 0/0/1，参考为 1/1/0.5。

分别核对观测与单位、队列覆盖、指标断言和容差。进程完成不表示指标断言通过；观测恒定时 R² 未定义，没有共同标识时没有配对评分。保留两侧输入，恢复或规范化另行记录。

对可信的已保存森林，`reference_ranger.R` 向经审查的 R 调用方提供 `reference_ranger_model()`、`reference_ranger_predict()`、`reference_ranger_metadata()`。它不训练或执行原始源码；模型加载、预处理与路径验证由调用方负责，其他格式需适配。

[比较工作流](../../../../workflows/model_reproduction/README_ZH.md)组织来源审查、对齐与诊断，[合成示例细节](../../../../config/examples/model-reproduction/README_ZH.md)说明产物，[资产存储](../../../../harness/assets_ZH.md)规定外部结果边界。
