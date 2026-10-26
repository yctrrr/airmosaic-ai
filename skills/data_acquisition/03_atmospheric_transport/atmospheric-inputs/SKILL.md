---
name: atmospheric-input-methods
description: Plan meteorology, initial and boundary conditions and diagnostic input contracts for version-specific GEOS-Chem workflows. No downloader.
---

# 大气模型输入准备

**状态**：文档指导，未注册执行适配器；没有可供 run-tool 调用的工具 ID。

## 使用顺序

先定 Classic/GCHP 与版本 → 列出气象、排放、初始/边界条件和诊断类别 → 检查时间、网格、物种、单位契约 → 单独规划下载范围和授权。

具体方法与交接见[对应说明](../../../../methods/03_atmospheric_transport/README.md)。

需要气象协变量或大气成分资料时，分别阅读 [ERA5](../era5/SKILL.md) 和 [CAMS](../cams/SKILL.md)。它们提供人工获取说明，不能直接替代 GEOS-Chem 的版本专用气象、物种或边界输入；尚无自动转换或下载工具。

## 行为边界

不读取原始数据或认证目录，不自动下载；GEOS-Chem 自身 dry-run 会执行程序并写日志。模型资料中排放输入只作为接口需求，不附清单具体数据或实现。

方法维护和常规验证只使用文档、接口与合成输入。真实数据任务须另有明确范围。个人路径与非秘密参数在 CONFIG_DIR，凭据在凭据管理器，会话在 AUTH_DIR；三类根独立且位于 Git 外。参考型 skill 不提供自动路径检查或脱敏记录。
