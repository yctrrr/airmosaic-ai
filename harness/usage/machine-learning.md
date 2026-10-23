# 机器学习模型使用

模型层的 [machine_learning 分类](../../skills/model/machine_learning/README.md)目前提供两类参考流程：

| 方法 | 用途 | 真实目录 ID |
|---|---|---|
| [mlr3](../../skills/model/machine_learning/mlr3/SKILL.md) | R 表格回归/分类、模型比较、调参与预测 | mlr3_workflow_reference |
| [TimeXer](../../skills/model/machine_learning/timexer/SKILL.md) | Python/PyTorch 外生变量时间序列预测 | timexer_workflow_reference |

## 1. 查询入口和执行状态

```powershell
python -m airmosaic_core.cli list-tools --category model --query mlr3
python -m airmosaic_core.cli describe-tool mlr3_workflow_reference
python -m airmosaic_core.cli check-tool mlr3_workflow_reference
python -m airmosaic_core.cli list-tools --category model --query TimeXer
python -m airmosaic_core.cli describe-tool timexer_workflow_reference
python -m airmosaic_core.cli check-tool timexer_workflow_reference
```

这两个条目均为 reference / catalogued，状态 not_executable，execution_supported 为 false。查询只展示说明和静态依赖条件，不加载 R/PyTorch、不安装包、不读取个人数据。它们没有 run-tool 训练、预测、调参命令；R 包 API 或上游 run.py 不能当作 AirMosaic 工具 ID。reference 状态也不证明列出的模型依赖版本兼容。

## 2. mlr3 使用步骤

1. 确定预测目标、数据许可、样本单位和下游用途，按 [mlr3 skill](../../skills/model/machine_learning/mlr3/SKILL.md)核对边界。
2. 准备任务 R 环境；基础示例需 mlr3/rpart，其余依赖由选定的 learner、PipeOp 与调参方法决定。当前指南不自动安装或加载个人启动文件。
3. 先参考[合成模型使用示例](../../skills/model/machine_learning/mlr3/examples/basic-model-use.md)理解 API，再为授权数据实现任务副本；示例本轮仅解析语法，未完成模型实跑。
4. 按[工作流与验收](../../skills/model/machine_learning/mlr3/references/workflow.md)定义划分、图内预处理、预算、开发比较、最终评估及新数据契约。
5. 保存本地模型、预测和验证记录，检查失败/缺失和数据泄露；只分享经审查的聚合摘要。

## 3. TimeXer 使用步骤

1. 阅读[模型方法](../../skills/model/machine_learning/timexer/references/method.md)，确定 MS 单目标或 M 多变量预测、历史窗口、预测步数，以及协变量在预测时点的可用性。
2. 根据[使用方法](../../skills/model/machine_learning/timexer/references/usage.md)准备独立 Python 环境、固定源码和规则时间 CSV；目录示例不代表依赖已安装。
3. 在工作区的新任务目录用足量合成数据核对参数和产物；真实任务另适配时间划分、实体内滑窗和缺失处理。上游默认训练每轮查看测试误差，需在正式开发流程移除这部分访问。
4. 固定方案后评估，核对预测单位、提前量及基线。保存训练期 scaler、输入顺序、配置和权重；带标签测试命令不能代替未知未来的推理入口。
5. 未来外生变量、指定日期切分、多实体面板和纯推理均需适配并验证；当前没有下载、训练或部署适配器，也没有自动脱敏运行记录。

## 4. 路径、个人配置与模型产物

| 内容 | 位置与管理 |
|---|---|
| 已授权输入 | `${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/` 或既有 `output/`；原始数据保持不变 |
| 新模型/预测/本地记录 | 新的 `output/<run_id>/mlr3_workflow/` 或 `output/<run_id>/timexer_workflow/`；目录标签不是工具 ID，不复用旧结果覆盖 |
| TimeXer 外部源码 | 仓库外的独立源码目录，以本地 `TIMEXER_SOURCE_DIR` 表示；不是自动加载配置，不在此运行产生结果 |
| 非秘密个人配置 | `${AIRMOSAIC_CONFIG_DIR}`；显式读取本次需要的路径/参数，不扫描全目录 |
| 登录状态/凭据 | 本地建模不需要登录；AUTH_DIR 的会话内容不参与建模；密码/token 留在凭据管理器 |
| 共享仓库 | 可公开的方法、合成示例、来源提交和依赖说明；不包含真实数据、模型 RDS/checkpoint 或私人路径 |

上述三类根须独立且位于 Git 外，详见[存储约定](../storage-and-credentials.md)。这份参考指南不执行路径预检、环境隔离或自动脱敏；实际任务代码应实现相应检查。模型对象与完整 R 会话记录可能携带训练数据、身份字段、后端或路径，不能默认作为可共享附件。

## 5. 跟踪参考项目与后续接入

[mlr3 跟踪记录](../../skills/model/machine_learning/mlr3/UPSTREAM.md)和 [TimeXer 跟踪记录](../../skills/model/machine_learning/timexer/UPSTREAM.md)分别记录参考仓库、核对 SHA/日期、许可核对、采用内容及更新步骤。跟踪是按需复核，没有自动拉取、安装或定时任务。上游版本或验证报告不能替代本机运行证据。

后续若接入 run-tool，应先明确有限的训练/预测参数、数据 schema、模型格式、资源预算与结果契约，提供合成测试、失败处理和隐私检查，再审查允许清单并启用适配器。当前的参考登记不授予任意 R/Python 代码执行权限。
