# 模型复现任务示例

[English](README.md) | **中文**

本示例比较两侧各五行的合成预测，参考侧顺序刻意打乱。需要已安装的项目 Python 环境和显式分离的 ASSETS、CONFIG、AUTH 根，不需要登录或真实观测。按[工作流](../../../workflows/model_reproduction/README_ZH.md)和[技能](../../../skills/model/shared/model_reproduction/SKILL_ZH.md)执行。

```sh
python skills/model/shared/model_reproduction/scripts/make_synthetic_fixture.py --fixture-id synthetic_v1 --execute
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo --execute
```

候选侧预期 RMSE、MAE、R² 为 0、0、1；参考侧为 1、1、0.5。顺序不同仍应匹配全部五个 ID。既有示例和比较目录不覆盖；再次运行需选择新名称，并更新显式指定的任务副本。

真实案例先将任务复制到个人 CONFIG，设置冻结的外部结果根、清单、预测来源、模型编号、标识/观测/预测列、单位及可选的已报告指标 JSON 指针。由保存模型恢复的预测应与原始导出预测区别记录。来源审计和模型恢复先于比较入口完成。可选 `audit_matrix.path` 指向同一外部项目结果边界内由代理提供的审计 JSON，并保留依据和限制。

`output_files` 按产物角色选择相对文件名，`--out-dir` 可在项目结果根下选择新目录，均不解释 shell 表达式。字段见[结构](../../../catalog/schemas/model-reproduction-task.schema.json)。远程获取、训练、YAML 执行、科学批准和资产入库不自动发生。
