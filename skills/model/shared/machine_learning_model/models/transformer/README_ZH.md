# Transformer 软件操作案例

[English](README.md) | **中文**

研究设计先阅读[架构与数据方法](../../../../../../methods/shared/machine_learning_model/models/transformer/README_ZH.md)。选择环境、配置、调用及检查实际操作时，阅读本技能的[软件指南](../../references/transformer-software_ZH.md)。

| 输入路径 | 计算机操作案例 | 当前支持 |
|---|---|---|
| 数值表格 | `--case tabular`：变量单元 | 已实现直接运行的 CPU 合成助手 |
| 数值序列 | `--case sequence`：历史单元 | 已实现直接运行的 CPU 合成助手；不是真实预测适配器 |
| 数值网格 | `--case grid`：空间片段 | 已实现直接运行的 CPU 合成助手 |
| 数值组合输入 | `--case fusion`：静态、历史及网格单元 | 已实现直接运行的 CPU 合成助手 |
| 外部序列模型 | [TimeXer](../time_series/timexer/SKILL_ZH.md) | 已核对上游命令；需人工适配，无 AirMosaic 执行器 |
| 文本或预训练多模态模型 | 软件指南中的外部框架参考 | 需独立实现数据及模型；本项没有文本训练案例 |

四个 CPU 案例均在内部生成全部输入，不接收外部数据集。它们演示张量准备、分支投影、注意力、拟合、留出评分及模型重载，不是 FT-Transformer、PatchTST 或 TimeXer 的复现。融合案例把投影后的单元拼接，再进行共同自注意力，不实现 TimeXer 的交叉注意力。

入口为 [run_transformer_demo.py](../../scripts/python/run_transformer_demo.py)，可复用的合成模型为 [transformer_demo.py](../../scripts/python/models/transformer_demo.py)。既有 R/Python 科学工具及任务契约保持不变。助手未注册到 run-tool 或 MCP，也不继承执行器的环境隔离或科学计划门控。请遵守指南中的外部输出检查，真实数据使用另行审查的新研究实现。
