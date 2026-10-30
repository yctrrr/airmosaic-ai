---
name: autoskill
description: 审查明确选择的 AirMosaic 任务记录，展示有边界的字面匹配复用证据，并为代理审查准备脱敏技能提案。
compatibility: Python 3.10+ standard library; explicit external task and storage roots
metadata:
  version: "1.0.0"
---

# 根据证据维护技能

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->

用于对指定项目记录 JSON/Markdown 或明确审查的来源文本开展有边界的复盘。阅读权威[改进契约](../../../../harness/skill-improvement_ZH.md)和[操作与格式](references/operations_ZH.md)。只在明确的 Git 外任务根内选择具体脱敏文件；辅助脚本不发现任务历史或提议技能。提供仅含公开技能名称与描述的受控目录。

辅助脚本产生字面匹配证据，并建议 `reuse`、`revise`、`compose` 或 `novel` 路由。代理自行审查实际证据和科学假设。描述词重合只是可见检索线索，不代表语义理解。过期或转述记录不能建立已观察到的复用依据。`compose` 的组合放工作流，操作代码放技能，科学推理放方法。本流程不设置科学验收结论。

可选草稿必须来自明确提供的脱敏结构化提案，由当前代理编写或由用户提供审查。脚本只格式化提案，不从日志推断科学方法或编写操作正文。用[技能编写](../skill_authoring/SKILL_ZH.md)修订和检查草稿。可运行的合成示例及完整参数见操作参考。

输出仅写入新的外部 `assets/results/skill_maintenance/<UTC-minute>_<task-id>/`。生成摘要不保留原始正文、来源路径、来源记录标识或数据行。不得提供原始数据集、凭据、浏览器状态、认证或配置文件、私人 harness 计划、会话历史和屏幕捕获。配置和认证根仅核对分离，不枚举内容。隐私启发式检查辅助输入脱敏，不能证明任意正文属于公开内容。

本技能包含已实现的直接标准库脚本和审查流程，无注册工具编号，`run-tool` 不支持调用。不执行被检查源码，不调用外部模型、嵌入服务或屏幕记录器；不自动提升、安装、注册、提交或修改仓库。已接受动作在既有授权范围内持续有效；后续安装或发布需有相应授权。拒绝后针对固定诊断码修正条件，不扩大检索或放松边界。I/O 失败后检查新目录的部分输出，再选择新任务编号重试。

本适配参考已公开审查的 [scientific-agent-skills 固定修订](https://github.com/K-Dense-AI/scientific-agent-skills/tree/5f2bc0341354fd5590aef76a533ada1e1e5b4e62)。AirMosaic 的有边界实现和合成示例为原创，不引入上游运行时或采集流程。
