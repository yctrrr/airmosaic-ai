---
name: gcam
description: 查阅 GCAM 已有输出、配置参考以及已注册的提取和汇总工具；分析既有情景数据库，不启动模拟。
---

# GCAM 模型结果分析

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`gcam_extract_market_sector`、`gcam_extract_technology_components`、`gcam_aggregate_provinces`、`gcam_inspect_output_structure`、`gcam_plot_sector_change` 均通过执行器使用。配置属于参考流程，没有模拟启动工具。

## 工作目录与认证

遵守[共享存储约定](../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../harness/usage/run-tool.md)。仓库外三个已存在根目录相互独立：`AIRMOSAIC_LOCAL_WORKSPACE` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密设置和显式任务参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态。密码和令牌留在秘密管理器，不读取或分享凭据及浏览器配置内容。命令从仓库根目录使用安装项目的解释器运行；执行器自动分配 `output/<run_id>/<tool_id>/`，没有需要时省略输出参数。个人配置不自动加载。直接运行脚本会绕过检查；执行器不是操作系统沙箱。

## 分层导航

GCAM 是跨阶段能力，见[四步导航](../../../../harness/four-step-workflow.md)。[构建排错](references/build-troubleshooting.md)区分源码编译、链接和运行错误，不启动构建或模拟，也不扩大已有分析工具权限。

按任务选择子技能：

| 任务 | 子技能 |
|---|---|
| 列出情景、地区、部门、子部门和技术 | [输出结构](01_output_structure/SKILL_ZH.md) |
| 检查价格与数量单位 | [输出结构](01_output_structure/SKILL_ZH.md) |
| 省份代码映射 | [输出结构](01_output_structure/SKILL_ZH.md) |
| 理解配置和情景组件 | [配置参考](02_configuration/SKILL_ZH.md) |
| 追溯输入到数据库输出 | [配置参考](02_configuration/SKILL_ZH.md) |
| 安全增加或移除情景组件 | [配置参考](02_configuration/SKILL_ZH.md) |
| 检查碳捕集配置 | [配置参考](02_configuration/SKILL_ZH.md) |
| 查询部门命名 | [配置参考](02_configuration/SKILL_ZH.md) |
| 提取市场或部门价格数量 | [结果提取](03_data_extraction/SKILL_ZH.md) |
| 分解技术成本组成 | [结果提取](03_data_extraction/SKILL_ZH.md) |
| 省级加权汇总 | [结果提取](03_data_extraction/SKILL_ZH.md) |
| 绘制价格数量变化 | [结果提取](03_data_extraction/SKILL_ZH.md) |
| 解释价格单位和部门差异 | [结果提取](03_data_extraction/SKILL_ZH.md) |

## 调用与依赖

| 工具编号 | 调用 | 范围 |
|---|---|---|
| `gcam_extract_market_sector` | 执行器 | 既有市场、部门记录 |
| `gcam_extract_technology_components` | 执行器 | 既有技术组成记录 |
| `gcam_aggregate_provinces` | 执行器 | 既有市场、部门表 |
| `gcam_inspect_output_structure` | 执行器，R | 固定检查查询及数据库布局 |
| `gcam_plot_sector_change` | 执行器，R | 固定比较年份及显式输出 |
| `gcam_configuration_reference` | 仅参考，不可执行 | 手动审查或授权任务副本修改 |

先用 `describe-tool <tool_id>` 查声明，再按子技能和[模型指南](../../../../harness/usage/model-analysis.md)操作。提取需要项目解释器、pandas、本地 Java、兼容的 BaseX 组件和所选情景数据库。`GCAM_RELEASE_DIR` 显式配置在仓库与数据、配置、认证根之外，不随项目提供，也不自动发现。汇总仅需 pandas 和输入表。

执行器分配输出，绘图时注入 `UNIT_PRICE_OUT_DIR` 并忽略调用方同名值。R 使用 `--vanilla` 和独立包检查，预检不证明包能加载。配置修改使用任务副本并单独核验，不授权模拟。没有自动跨工具编排、模型启动或科学验收服务。

## 数据边界

技能仅保存可复用方法，不复制模型发行包、数据库、情景输出或原始数据；见 `data_boundary.md`。

不保存凭据、令牌、会话、浏览器配置、私人路径或私有下载链接。

## 共用参考

- `references/gcam-china-vs-official.md`：中国版与官方核心版差异。
- `references/input-data-architecture.md`：原始输入到数据库的数据链。
- `references/privacy-redaction-rules.md`：脱敏清单。
- `data_boundary.md`：技能目录的数据边界。
