---
name: enterprise-disclosure-methods
description: 指导企业财务、年报及省级环境披露的来源选择和证据核对；没有采集适配器。
---

# 企业来源与披露方法

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


**状态**：文档指导，未注册执行适配器；没有可供 `run-tool` 调用的工具 ID。

## 使用顺序

明确企业、期间和报告类型 → 区分列表、正文与附件 → 设计可恢复队列和版本标识 → 检查来源证据与覆盖。

具体方法与交接见[对应说明](../../../../methods/01_socioeconomic_natural_change/enterprise_sources.md)。

## 行为边界

共享库不保存企业明细、认证链接或私人会话。仅基础信息 ZIP 处理可引用已有 csmar_process_company_info；它不能替代披露采集。

方法维护和常规验证只使用文档、接口与合成输入。真实数据任务须另有明确范围。个人路径与非秘密参数在 CONFIG_DIR，凭据在凭据管理器，会话在 AUTH_DIR；三类根独立且位于 Git 外。参考型技能 不提供自动路径检查或脱敏记录。
