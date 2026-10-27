---
name: gcam-configuration
description: 说明 GCAM 情景组件、社会经济与气候情景及碳捕集输入；授权修改使用任务副本和人工核验，没有自动配置工具。
---

# GCAM 配置参考

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`gcam_configuration_reference` 是执行器禁用的参考条目。审查及授权修改在任务副本中手动进行，没有配置修改接口或模型启动器。

## 工作目录与认证

遵守[共享存储约定](../../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../../harness/usage/run-tool.md)。仓库外三个已存在根目录相互独立：`AIRMOSAIC_LOCAL_WORKSPACE` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密设置和显式任务参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态。密码和令牌留在秘密管理器，不读取或分享凭据及浏览器配置内容。命令从仓库根目录使用安装项目的解释器运行；执行器自动分配 `output/<run_id>/<tool_id>/`，没有需要时省略输出参数。个人配置不自动加载。直接运行脚本会绕过检查；执行器不是操作系统沙箱。

## 用途

帮助理解配置，不自动运行模型：

- 配置文件如何定义情景组件。
- 社会经济与辐射强迫情景组合。
- 输入表经 R 处理生成模型配置的数据链。
- 常见配置修改及风险。
- 碳捕集配置和问题。
- 部门命名与内部映射。

## 前置条件

使用明确配置的 `GCAM_RELEASE_DIR`，只读检查授权源码。发行包在仓库及三类个人根之外，公共示例不含真实绝对路径。个人配置根不会自动加载配置文件。

## 按任务阅读

- `references/configuration-files-overview.md`：配置结构。
- `references/ssp-rcp-scenario-setup.md`：情景组合。
- `references/input-data-chain-tracing.md`：输入输出链。
- `references/common-config-manipulation.md`：安全修改。
- `references/ccs-configuration-in-depth.md`：碳捕集配置。
- `references/sector-naming-conventions.md`：部门命名与映射。

## 人工配置边界

真实目录编号为 `gcam_configuration_reference`，用 `describe-tool` 查询；执行器拒绝运行。`examples/` 中的 JSON 是人工计划，不是执行器参数或注册动作。

解释任务只检查请求的配置、组件顺序和引用文件。授权修改时，将必要配置及依赖复制到新任务目录，修改副本并核对解析、顺序、引用，再审查限定范围的差异。不修改共享原件，也不因配置修改授权而启动模拟。只读审查、配置修改和模型执行是不同操作。
