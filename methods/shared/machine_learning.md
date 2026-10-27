# mlr3 与 TimeXer

**状态**：这两项是近期新增的方法学习和使用说明，当前没有训练/预测适配器，也没有本机模型训练通过记录。保留原有详细文档，方法库只提供选择入口。

| 方法 | 适用任务 | 真实参考 tool_id |
|---|---|---|
| [mlr3](../../skills/model/machine_learning/mlr3/SKILL.md) | R 表格回归/分类、比较、调参与新数据预测 | mlr3_workflow_reference |
| [TimeXer](../../skills/model/machine_learning/timexer/SKILL.md) | Python/PyTorch 外生变量时间序列预测 | timexer_workflow_reference |

## 共用步骤

1. 定义目标、预测时点、实体和特征可获得时间，先设计与部署场景一致的划分。
2. 在任务环境检查依赖与数据契约；拟合型预处理只使用开发训练范围。
3. 设置基线、预算和评价指标，在开发数据中比较/调参；冻结方案后进行约定的独立评估。
4. 保存模型、配置、训练期变换、列顺序、类型、单位和版本；预测新数据时复用同一契约。
5. 检查分布变化、缺失预测和适用范围。模型对象与逐条结果留在本地，预测表现不证明因果机制。

## 方法专属边界

mlr3 的拟合型预处理应置于重抽样流程内；Task/Learner 为可变对象，修改隔离与最终拟合范围见其工作流说明。

TimeXer 当前官方实现主要消费历史窗口；未来已知外生变量和多实体取窗需适配。`--is_training 0` 是带标签测试，不等于未知未来推理；开发期测试集访问、scaler 保存和输出路径见其使用方法。

详细参数、环境、上游 SHA 和验证范围统一维护在[机器学习分类](../../harness/usage/machine-learning.md)及各自 UPSTREAM.md，避免在本方法库产生第二套不一致命令。

## 阶段与 Skill 映射

主目录：shared；适用阶段：01_socioeconomic_natural_change, 02_emission_inventory, 03_atmospheric_transport, 04_integrated_impacts。对应 [mlr3](../../skills/model/machine_learning/mlr3/SKILL.md)、[timexer](../../skills/model/machine_learning/timexer/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
