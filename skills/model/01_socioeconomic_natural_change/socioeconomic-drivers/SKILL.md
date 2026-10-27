---
name: socioeconomic-driver-methods
description: Plan socioeconomic activity, energy and technology driver workflows and route to existing shared modeling references. No driver simulation adapter.
---

# 社会经济驱动方法

**状态**：文档指导，未注册执行适配器；没有可供 run-tool 调用的工具 ID。

## 使用顺序

定义变量和研究范围 → 关联获取方法 → 明确去重、映射与单位 → 需要预测时选择共享模型和验证设计 → 交接活动、能源及技术的接口。

具体方法与交接见[对应说明](../../../../harness/four-step-workflow.md)。

## 行为边界

mlr3/TimeXer 是共享参考，GCAM 只分析已有输出；此 skill 不会自动训练或运行情景。

方法维护和常规验证只使用文档、接口与合成输入。真实数据任务须另有明确范围。个人路径与非秘密参数在 CONFIG_DIR，凭据在凭据管理器，会话在 AUTH_DIR；三类根独立且位于 Git 外。参考型 skill 不提供自动路径检查或脱敏记录。
