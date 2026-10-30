---
name: machine-learning-model
description: 规划和审核数值机器学习研究，选择 R/Python 预测路径，或运行仅 CPU 的合成 Transformer 软件案例；区分预测贡献与因果估计。
compatibility: "Core Python 3.10+; R path requires Rscript and declared packages; Python training requires Python 3.11+ and separate dependencies; CPU Transformer cases require PyTorch 2.6+"
metadata:
  version: "3.2.0"
  reviewed: "2026-10-30"
---

# 机器学习模型

[English](SKILL.md) | **中文**

用于数值预测、预测贡献及经单独论证的因果估计。[面向研究者的方法](../../../../methods/shared/machine_learning_model/README_ZH.md)说明科学选择，本入口指向实际操作。框架说明和专用序列参考现统一归入本能力目录，各自保留契约及执行状态。

## 规划、审核和准备

生成实验代码前，采用[模型规划](../../../../methods/shared/model_planning_ZH.md)与[计划审核契约](references/planning_ZH.md)，保存依据、证据、备选方案及不确定性。默认由人审核；代理判断须有用户针对准确计划的明确委托。不能将历史研究、样本划分或参数选择当作默认。执行前核查任务与数据未变、实际生成代码、合成证据和预检。通用助手为 `scripts/common/review_plan.py`；审核记录是可信调用方的声明，不认证身份或赋予权限。

明确目标、各变量角色/单位/时序、产品来源及观测重用。在预处理前设计时空或分组留出，训练变换和筛选不得使用留出信息。计算行数上限与科学抽样设计分别设置；保留原始、可用、选中样本数与排除原因。第02阶段仅讨论概念。见[通用设计](../../../../methods/shared/machine_learning_model/common_ZH.md)。

## 只读当前所需分支

按模型查找时，先打开[模型分类目录](models/README_ZH.md)：[线性回归](models/linear_regression/README_ZH.md)、[树模型](models/tree_based/README_ZH.md)或[时序模型参考](models/time_series/README_ZH.md)。决策树和随机森林同属树模型。均值基线归[公共评估](evaluation/README_ZH.md)，不再作为独立研究模型分类。每个已实现模型链接对应的 R/Python 配置和公共计算代码。

直接使用 R 接口及扩展时，阅读 [mlr3 框架说明](frameworks/r/mlr3/SKILL_ZH.md)。内嵌的 [TimeXer 技能](models/time_series/timexer/SKILL_ZH.md)保留外部 Python/PyTorch 操作说明，仍为仅参考；合并目录不增加执行器。

| 操作 | 实现及说明 |
|---|---|
| R 数据准备、拟合及留出评估 | [R操作](references/operations_ZH.md)：注册工具 `ml_regression_workflow`、适配器 `mlr3_regression`，接收整理好的 CSV 与现有任务 JSON |
| Python 数值预测 | [Python路径](references/python-path_ZH.md)：依赖、任务契约及 `ml_python_regression_workflow` 独立；须完成该路径记载的验证及注册检查后使用 |
| Transformer 软件操作案例 | [软件指南](references/transformer-software_ZH.md)：直接运行 CPU 合成表格、序列、网格及融合助手；Python 3.11+、Torch 2.6+，无注册适配器或外部数据选项 |
| 模型族、参数及固定折复现 | [模型](references/models_ZH.md)：通过配置声明候选，不复制每种模型的完整流水线 |
| 仅开发数据的自动调参 | [直接 R 路径](references/automatic-tuning_ZH.md)：固定分组折 AutoTuner 助手；基础契约已检查，完整调参待所需依赖环境验证，无执行器适配器 |
| 预测贡献 | [贡献](references/contribution_ZH.md)：置换/PDP/ICE/Shapley 解释拟合预测 |
| 因果效应 | [因果](references/causal_ZH.md)：R 连续处理 PLR，声明 DAG、手工调整集及有依据的假设 |

R 和 Python 是独立实现路径。Python 调用程序若调用 R 工具，仍需 R；两者任务契约不能互换。通用计划契约保留科学与实现分支，须通过所选实现的任务校验。

## 执行和验收

明确要求固定 R 合成回放时，从仓库根执行：

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --timeout 180
```

执行前检查 `can_execute`、`blockers`。预检不解析数据行，也不证明依赖可用。[R操作](references/operations_ZH.md)完整保留环境、配置生成、CLI/Python/MCP 调用、参数范围和结果读取示例。核查进程成功、文件内容、样本/特征保留情况、独立重算留出指标与模型重载。解释需交代背景及不确定性；PLR 另需科学识别审核。返回文件索引、检查结果和未解决限制。工程回放不等于科学验收，也不批准新研究。

原始数据、凭据、个人计划及研究生成结果按[存储契约](../../../../harness/assets_ZH.md)置于 Git 外。使用所选执行器声明的结果范围和新目录；维护源代码时不移动历史结果。[空气污染案例](references/air-pollution_ZH.md)、[发表依据](references/published-basis_ZH.md)及[工作流](../../../../workflows/ml_regression/README_ZH.md)按需读取。[迁移映射](references/layout_ZH.md)说明模块位置和实现边界。
