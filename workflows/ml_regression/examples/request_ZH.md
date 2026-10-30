# 固定合成任务的代码生成请求

[English](request.md) | **中文**

按[工作流提示词](../prompt_ZH.md)为下述有边界任务生成 `generated_regression.py`，以及显式公共任务 `config/examples/ml-regression/workflow-synthetic.json`：

- 仅使用清单登记的 `assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv`，不检查原始研究数据或个人设置。
- 使用 `x1`、`x2`、`treatment` 预测 `outcome`。这里的 `treatment` 仅为合成预测特征，不要求估计因果效应。沿用 `dataset` 标签，使用全部 400/100/100 条训练/验证/测试样本，以 `id` 为键。
- 比较均值基线、深度 5 的树与 48 棵树的森林。固定种子 20261028、单线程和 180 秒时限。验证集 RMSE 选型，冻结后做最终测试。执行有界的置换/PDP/ICE 诊断。
- 仅围绕 `ToolRunnerService.run('ml_regression_workflow', ...)` 编写薄编排，显式使用 `result_scope='workflow'`。默认预检，执行必须带 `--execute`。不提供项目编号，不执行任意命令，不自动安装或联网。
- 独立核对保存预测的键、观测及指标公式，检查模型重载、来源完整性和本样例的基线条件。在工作流被忽略的结果树保留新批次、本次 gen_script 中的代码、提示词及配置、环境和哈希。
- 保留失败，汇报脱敏状态及数量，仅把审查通过的通用示例代码用于复用。不声称科学验收、自动支持任意模型或按提示词确定性重新生成代码。

预期交付为可检查的代码、符合结构的任务、负向工程检查和实际合成执行证据。代理在当前任务会话中编写、审查代码，不表示新增了代码生成服务。


遵循[统一执行与过程记录规范](../../../harness/usage/workflow-handoff_ZH.md)。新运行使用12 位年月日时分加公开任务名，内部运行编号仅关联回执。保存 gen_script/、events.jsonl、retrospective.md / retrospective_ZH.md 和总体 workflow.json；不新增 source_snapshot/，仅在明确授权后清理已核对的冗余合成批次。生成依据是显式设计摘要，不冒充未捕获的历史生成会话。
