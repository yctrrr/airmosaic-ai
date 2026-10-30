# 论文原实现与候选结果对照

[English](README.md) | **中文**

本实验使用 [model_reproduction 工作流](../../../../workflows/model_reproduction/README_ZH.md)的 `compare_existing` 模式，将[首轮独立实现](../../prediction_ZH.md)作为冻结候选，核对已授权来源中的原代码、保存模型和最终图表。模型比较、代码证据与科学复核分别记录。

## 任务与执行

1. 将 [task.example.json](task.example.json)复制到个人 CONFIG，显式选择已有候选批次及新的原版快照；示例中的批次名需要替换，不含服务器位置。
2. 代理按已授权访问方式核验端点，只读收集相关代码与结果。核对代码、调参档案、保存模型和最终图表的关系；把真实位置映射保留在 CONFIG，不执行完整旧脚本。
3. 本例原始输入与共享 AQ-Bench 哈希一致。按照审查的原代码规则准备参考特征：国家样本数 `>=50`，排除不能归并的气候标签，人口密度除以 1000，规范化列名并保留原始行顺序。保留独立样本键并核验两组特征的队列。
4. 若缺少最终逐站预测，用[恢复函数](../../../../skills/model/shared/model_reproduction/scripts/reference_ranger.R)及经审查的项目调用，在最小 R 环境中对保存森林预测，记录为 `recovered_from_saved_model`。不训练、不重写模型，也不导出对象中的调用或环境。原保存图表只用于核对其显示精度下的指标。
5. 冻结快照与派生视图，保留审计矩阵，然后运行[比较入口](../../../../skills/model/shared/model_reproduction/SKILL_ZH.md)。检查共同/非共同 ID、观测一致性、已报告指标断言、逐站预测差异和输入未变回执。
6. 按工作流给出实现正确性、数值可复现性、历史来源缺口和科学适用范围。必要受控实验需固定预算并写入新批次，不能以接近旧指标为调参目标。

```sh
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <personal-config.json> --batch-id <fresh-comparison>
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <personal-config.json> --batch-id <fresh-comparison> --execute
```

## 当前状态与保存

本案例已完成源代码与保存森林的只读核对、恢复预测及冻结两侧结果比较；工程与数字核验完成，历史训练版本链和解释图的科学复核保留证据缺口。它不表示重跑了完整历史调参，也不表示新增了通用自动复现引擎。

外部 `assets/results/ozone_environmental_drivers/` 分别保留首轮候选、原版快照与新对照批次。实际审计矩阵、指标、预测、模型、时间、源代码证据和人工复核记录留在该范围，内部布局按本次任务选择。当前配置不自动加载或连接服务器，结果不自动覆盖、提交或入库。
