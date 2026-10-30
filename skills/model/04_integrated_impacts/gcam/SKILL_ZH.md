---
name: gcam
description: 使用已审查工具检查和分析已有 GCAM 输出，或查阅人工配置、编译与运行说明；没有模拟启动器。
compatibility: "Python >=3.10; Java; Rscript; optional C++ toolchain"
metadata:
  version: "1.0.0"
  reviewed: "2026-10-30"
---

# GCAM 准备与输出分析

[English](SKILL.md) | **中文**

按任务选择入口，再读取所需参考：

| 任务 | 入口 |
|---|---|
| 人工准备发行包、编译源码、生成输入 XML 或运行模型 | [编译与运行](references/build-and-run_ZH.md) |
| 检查固定数据库结构与单位 | [输出结构](01_output_structure/SKILL_ZH.md) |
| 解释配置，或在任务副本中适配 | [配置](02_configuration/SKILL_ZH.md) |
| 提取、汇总或绘制已有结果 | [提取](03_data_extraction/SKILL_ZH.md) |
| 诊断编译、链接及运行错误 | [构建排错](references/build-troubleshooting.md) |

只有输出检查、提取、汇总和绘图有经过审查的 `run-tool` 适配器。配置、编译、模拟仍是人工任务。编译运行说明要求选定模型版本、兼容依赖、经审查任务副本，并分别检查进程与求解状态；它不增加执行适配器。[GCAM 方法](../../../../methods/04_integrated_impacts/gcam_ZH.md)解释情景设计、编译运行选择、单位和结果含义。

在仓库根目录通过 `python -m runtime.cli describe-tool <tool_id>` 查看真实接口。显式配置既有外部存储根及 `GCAM_RELEASE_DIR`，个人配置不会自动加载。[操作参考](references/operations_ZH.md)提供依赖、参数文件、调用及结果检查。发行包与数据库保存在 Git 外，参见[数据边界](data_boundary.md)。

需要区分 GCAM-China 与 GCAM-Core 时读[模型差异](references/gcam-china-vs-official.md)；追踪指定输入链时读[输入架构](references/input-data-architecture.md)。历史参考保持原语言。提取成功不证明模拟有效或成本估计通过科学验收。
