---
name: socioeconomic-driver-methods
description: 规划社会经济活动、能源、技术及自然条件工作流，并引用共享模型；没有驱动模拟适配器。
---

# 社会经济与自然变化方法

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


**状态**：文档指导，未注册执行适配器；没有可供 `run-tool` 调用的工具 ID。

自然条件获取引用 [ERA5](../../../data_acquisition/01_socioeconomic_natural_change/era5/SKILL_ZH.md) 和 [CAMS EAC4 / 预报](../../../data_acquisition/01_socioeconomic_natural_change/cams/SKILL_ZH.md)。土地利用及其他自然过程尚需选择方法；本技能 不提供自然过程模拟。

## 使用顺序

定义变量和研究范围 → 关联获取方法 → 明确去重、映射与单位 → 需要预测时选择共享模型和验证设计 → 交接活动、能源及技术的接口。

具体方法与交接见[对应说明](../../../../harness/four-step-workflow.md)。

## 行为边界

mlr3/TimeXer 是共享参考，GCAM 只分析已有输出；本技能 不会自动训练或运行情景。

方法维护和常规验证只使用文档、接口与合成输入。真实数据任务须另有明确范围。个人路径与非秘密参数在 CONFIG_DIR，凭据在凭据管理器，会话在 AUTH_DIR；三类根独立且位于 Git 外。参考型技能 不提供自动路径检查或脱敏记录。

数据与结果按[资产目录与复核入库规范](../../../../harness/assets_ZH.md)管理：数据按阶段、实际名称和版本共享；结果按项目及运行归集。跨阶段引用同一数据，复用入库需人工批准。
