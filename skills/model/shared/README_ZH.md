# 跨阶段模型技能

[English](README.md) | **中文**

这些操作可用于多个研究阶段，与 [methods/shared](../../../methods/shared/README_ZH.md) 中的方法说明对应。具体研究引用同一能力，不在各阶段复制。

| 能力 | 技能 | 方法 | 可执行状态 |
|---|---|---|---|
| 空间分析与制图 | [spatial_analysis](spatial_analysis/SKILL_ZH.md) | [空间关系、坐标系与支撑](../../../methods/shared/spatial_analysis_ZH.md) | R 与 Python 直接函数通过合成检查；地理编码/栅格提供指导；未接入 run-tool 或 MCP |
| 机器学习模型、贡献与因果分析 | [machine_learning_model](machine_learning_model/SKILL_ZH.md) | [回归目标、DAG 与解释](../../../methods/shared/machine_learning_model/README_ZH.md) | R：`ml_regression_workflow`；Python：`ml_python_regression_workflow`；PLR 仍仅 R 实现 |
| 复现与比较 | [model_reproduction](model_reproduction/SKILL_ZH.md) | [对照与可靠性](../../../methods/shared/model_reproduction_ZH.md) | 已审查的直接比较与恢复函数；未新增 run-tool 或 MCP 执行适配器 |

`machine_learning_model/` 是共享机器学习能力的统一位置。`models/` 分类线性、树模型和序列模型参考，`evaluation/` 提供公共基线对照，`frameworks/r/mlr3/` 保存 R 框架说明。公共计算代码保留 `scripts/r/` 与 `scripts/python/` 分层。框架和专用序列入口保留各自契约及参考状态。通用[回归工作流](../../../workflows/ml_regression/README_ZH.md)说明数据与技能组合，[项目](../../../projects/README_ZH.md)定义具体科学实验。

空气污染任务先阅读[过程与影响方法](../../../methods/shared/air_pollution_regression_ZH.md)，再查看回归技能的[操作契约](machine_learning_model/references/operations_ZH.md)和[领域特例](machine_learning_model/references/air-pollution_ZH.md)。科学示例不增加可执行模型或因果估计目标。

专属阶段操作仍归其主阶段，第二步只接收概念方法引用。工具编号与发现取决于目录声明和显式映射，不由文件夹名称决定。参见[分类用法](../../../harness/usage/machine-learning_ZH.md)及[资产规范](../../../harness/assets_ZH.md)。新的通用回归结果使用被 Git 忽略的 `machine_learning_model/results/`；此前本地结果保留原位，不自动迁移。

治理成本、分配情景与 GCAM 输出分析由[第四步](../04_integrated_impacts/README_ZH.md)维护。其他阶段可引用第四步的同一技能，不在共享目录重复放置。
