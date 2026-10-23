---
name: timexer-forecasting
description: Explain and adapt the official TimeXer model for time-series forecasting with exogenous variables. Use for TimeXer method review, historical covariate input, training and evaluation setup, checkpoint inference planning, and tracking thuml/TimeXer within AirMosaic.
---

# TimeXer 方法与使用

TimeXer 用于借助外生变量预测目标时间序列。本目录跟踪 [thuml/TimeXer](https://github.com/thuml/TimeXer) 的官方实现；项目名称按官方拼写使用 TimeXer。它与 mlr3 的表格建模流程并列，使用 Python/PyTorch。

**当前状态**：`timexer_workflow_reference` 是 `reference / catalogued`，`execution.enabled: false`。AirMosaic 提供方法与适配说明，没有 TimeXer 训练、推理或下载适配器；不能通过 run-tool 执行。上游的 `run.py` 是外部研究代码入口，不是本项目工具 ID。

## 使用顺序

1. **定义预测时点**：明确目标、采样间隔、历史长度、预测步数和业务用途。对每个协变量记录在预测时点能否获得；实测未来天气、事后修订值不能冒充当时可用输入。
2. **选择任务**：单目标加协变量优先核对 `features=MS`；多目标核对 `M`。当前模型只实现预测分支，不能因通用 CLI 列出分类/插补选项就宣称 TimeXer 支持它们。
3. **理解模型与输入**：阅读[方法和能力边界](references/method.md)，区分论文设定和所跟踪代码的实际张量入口。历史协变量直接进入当前实现；未来已知协变量、异频数据和多站点面板需要任务适配。
4. **准备环境和数据**：按[使用方法](references/usage.md)核对独立 Python 环境、固定上游提交、CSV 列顺序、时间连续性和训练期缩放。先用合成数据做小规模检查，不在 AirMosaic 核心环境安装整套旧依赖。
5. **训练与评估**：规定资源预算和时间划分。上游基准训练会每轮计算测试误差，正式任务应适配为仅用训练/验证集开发，冻结方案后评估保留集。原有授权已覆盖的任务无需重复确认。
6. **新数据预测**：保存模型配置、权重、训练期 scaler、列顺序、单位和时间编码；实现仅含历史输入的推理入口。`--is_training 0` 仍是带标签测试，不能代替上线推理。
7. **验收和记录**：检查预测形状、时点、单位、基线、各提前量误差、极端事件表现和失败样本。只共享脱敏摘要；注意力关联和预测提升不能作为因果效应证据。

## 路径与凭据边界

- 数据放在 `${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/` 或已授权的既有 `output/`；新结果放在 `output/<run_id>/timexer_workflow/`。此处目录标签不是工具 ID。
- 上游源码位于单独的仓库外目录，使用本地变量 `TIMEXER_SOURCE_DIR` 表示；它不是 AirMosaic 自动读取的配置，也不授予访问相邻目录的权限。
- 路径/非秘密参数留在 `AIRMOSAIC_CONFIG_DIR`；本地建模无需登录，不读取 `AIRMOSAIC_AUTH_DIR`。数据门户的获取和授权另走数据获取流程，token 留在凭据管理器。
- 原始脚本没有 run-tool 的路径预检、超时清理、环境隔离或脱敏记录。全部产物、原始日志、权重和逐条预测保留在本地任务目录；不要在共享仓库根启动训练。

参考[存储约定](../../../../harness/storage-and-credentials.md)、[agent 边界](../../../../harness/agent-boundaries.md)及[机器学习分类查询](../../../../harness/usage/machine-learning.md)。

## 来源与验证

[UPSTREAM.md](UPSTREAM.md)记录论文、固定提交、许可核对及更新方法。当前完成源码与参数核对、文档/语法检查；没有安装 PyTorch、下载训练数据或训练模型。不要将此记录表述为实跑通过。
