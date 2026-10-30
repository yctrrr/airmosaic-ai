# 0001 — 环境特征与多年平均臭氧

[English](README.md) | **中文**

**科学问题：** 环境特征和人类活动代理变量能在多大程度上预测站点多年平均臭氧？这些预测关联在不同特征组合、模型选择和验证设计下是否稳定？

稳定项目标识为 `ozone_environmental_drivers`。目录编号 `0001` 用于导航，新结果使用稳定标识归集。目录中的“驱动”指候选解释特征，不表示已识别因果效应。

## 范围与引用

| 项目 | 定义 |
|---|---|
| 公开输入 | AQ-Bench v1 站点指标与变量字典，按 [project.json](project.json) 引用固定版本 |
| 目标 | `o3_average_values`，单位 ppb，2010–2014 年站点臭氧汇总指标 |
| 研究阶段 | `03_atmospheric_transport` |
| 通用工作流 | [ml_regression](../../workflows/ml_regression/README_ZH.md)，版本 1.0.0 |
| 已注册工具 | `ml_regression_workflow` |
| 操作技能 | [回归技能](../../skills/model/shared/machine_learning_model/SKILL_ZH.md) |
| 科学与来源依据 | [臭氧参考案例及公开输入](references/air_quality_o3_reference_ZH.md) |

[研究方案](study-plan_ZH.md)说明假设、实验和解释范围；[复核说明](review_ZH.md)是待复核模板。已有[小样本配置](../../config/examples/ml-regression/aq-bench-prediction.json)演示计算路径，不代表完整研究方案已获认可。

## 实验安排

| 实验 | 科学目的 | 执行状态 |
|---|---|---|
| E01 — 基线比较 | 在共同样本上比较受支持模型与固定均值基线 | 首轮论文预测计算与独立指标核验完成，原模型对照已完成，待人工科学复核 |
| E02 — 特征组比较 | 评估环境特征与人类活动代理变量组合对预测表现和解释的影响 | 九变量与三变量首轮比较完成，原模型对照已完成，待人工科学复核 |
| E03 — 稳健性与解释 | 检查开发期种子、验证设计及相关特征对结论的影响 | 待执行，其他空间划分和解释方法需适配 |
| E04 — 原实现对照 | 核对来源链、共同队列、预测与指标差异 | compare_existing 已完成，历史训练来源链不完整，待人工复核 |

## 当前状态与使用

本项目已完成首轮[论文预测与评估实验](prediction_ZH.md)，使用外部资产、固定 [prompt](prediction_prompt_ZH.md)和[实验协议](prediction.json)，保留 4077 条开发样本和 1009 条测试样本。两组模型经十折选参、全开发集重拟合与最终测试，计算和独立核验已完成；原模型与结果已按 [model_reproduction 工作流](experiments/reference_comparison/README_ZH.md)完成只读对照，历史训练来源链保留证据缺口；稳健性实验及人工科学复核仍待完成。

该论文专项的十折编排由项目脚本实现，复用核心启动机制、回归指标函数与 mlr3 技能，不属于通用 `ml_regression_workflow` 的已实现选项。其入口和真实执行状态见专项说明；通用工作流此前的小样本记录继续保留自身范围。

通用适配器任务先阅读研究方案，在私人配置根准备实验参数，再调用现有工具，指定 `--project-id ozone_environmental_drivers --stage 03_atmospheric_transport`；论文专项按其单独的启动说明运行。每种实验配置使用新批次。项目清单引用工作流，不自动执行。参见[项目操作规范](../README_ZH.md)和[工作流用法](../../workflows/ml_regression/README_ZH.md)。

研究结果仅限定在外部 `assets/results/ozone_environmental_drivers/`；实验可自选内部目录和产物相对名称，保留实验与运行的对应关系。DAG 与因果估计目标的通用设计见方法及工作流；本项目当前问题仍为预测，不因技能增加因果分支而自动开展观测因果实验。

`references/` 保存本问题的旧源码核对、公开输入和复现适配依据。它们是项目参考，不是已完成实验的结果或通用默认值；通用科学设计仍由方法库维护。

输入同时保留哈希一致的[仓库副本](../../assets/data/03_atmospheric_transport/AQ-Bench/v1/README_ZH.md)和外部副本。`project.json` 记录两种路径供显式选择，仍由人工或 agent 阅读选择，不自动加载，结果位置不变。
