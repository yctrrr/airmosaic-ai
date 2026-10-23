---
name: energy-balance-methods
description: Guide source-version tracking, unit conversion and sector-boundary review for energy-balance processing. No executable adapter.
---

# 能源平衡与单位换算方法

**状态**：文档指导，未注册执行适配器；没有可供 run-tool 调用的工具 ID。

## 使用顺序

明确来源版本和统计分母 → 区分实物量与转换系数 → 检查部门/能源映射 → 设计份额、闭合及缺失审计。

具体方法与交接见[对应说明](../../../../methods/01_socioeconomic/energy_balance.md)。

## 行为边界

本地原入口不在本仓库执行；不能照搬固定输出目录或历史换算规则。

方法维护和常规验证只使用文档、接口与合成输入。真实数据任务须另有明确范围。个人路径与非秘密参数在 CONFIG_DIR，凭据在凭据管理器，会话在 AUTH_DIR；三类根独立且位于 Git 外。参考型 skill 不提供自动路径检查或脱敏记录。
