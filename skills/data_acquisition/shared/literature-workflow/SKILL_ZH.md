---
name: literature-workflow-methods
description: 指导跨阶段文献发现、附件核对及导入规划，不执行采集器或修改文献库。
---

# 跨阶段文献工作流

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


**状态**：文档指导，未注册执行适配器；没有可供 `run-tool` 调用的工具 ID。

## 使用顺序

界定主题 → DOI/标题去重 → 核对全文和附件来源 → 区分归档、摘要与导入计划 → 审核证据。

具体方法与交接见[对应说明](../../../../methods/shared/literature.md)。

## 行为边界

外部收集器的 dry-run 可能联网和写文件。生成导入清单不等于实际导入；当前没有 run-tool 适配器。

方法维护和常规验证只使用文档、接口与合成输入。真实数据任务须另有明确范围。个人路径与非秘密参数在 CONFIG_DIR，凭据在凭据管理器，会话在 AUTH_DIR；三类根独立且位于 Git 外。参考型技能 不提供自动路径检查或脱敏记录。
