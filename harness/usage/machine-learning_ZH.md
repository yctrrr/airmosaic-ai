# 机器学习操作

[English](machine-learning.md) | **中文**

| 层次 | 职责 | 入口 |
|---|---|---|
| 方法 | 目标定义、变量角色、DAG 识别、回归及解释假设 | [回归方法](../../methods/shared/machine_learning_model/README_ZH.md) |
| 任务技能 | 经审查的目标与特征准备、拟合、评估、预测解释和已支持因果估计 | [回归技能](../../skills/model/shared/machine_learning_model/SKILL_ZH.md) |
| 模型族 | 线性回归、树模型及序列模型参考 | [模型目录](../../skills/model/shared/machine_learning_model/models/README_ZH.md) |
| 公共评估 | 训练均值参照及共同候选检查 | [评估](../../skills/model/shared/machine_learning_model/evaluation/README_ZH.md) |
| 软件演示 | 直接运行 CPU 合成 Transformer 输入、训练及重载案例；不是注册工具 | [软件案例](../../skills/model/shared/machine_learning_model/references/transformer-software_ZH.md) |
| 框架技能 | mlr3 环境、接口与扩展说明 | [mlr3](../../skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL_ZH.md) |
| 序列参考 | 外部 Python/PyTorch TimeXer 操作说明；无 runner 适配器 | [TimeXer](../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL_ZH.md) |
| 工作流 | 通用数据与技能组合、DAG 设计环节、分支与交接 | [回归组合](../../workflows/ml_regression/README_ZH.md) |
| 项目 | 具体问题、实验、比较和复核 | [项目 0001](../../projects/0001_ozone_environmental_drivers/README_ZH.md) |

R 的真实执行编号仍为 `ml_regression_workflow`，后端为 mlr3。独立 Python 回归入口为 `ml_python_regression_workflow`，其[语言路径](../../skills/model/shared/machine_learning_model/references/python-path_ZH.md)说明独立任务契约、依赖和审核包。`mlr3_workflow_reference` 和 `timexer_workflow_reference` 继续作为不可执行参考；软件包接口不是工具编号。

```powershell
python -m runtime.cli list-tools --category model --query mlr3
python -m runtime.cli describe-tool ml_regression_workflow
python -m runtime.cli check-tool ml_regression_workflow
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/aq-bench-ml-regression.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-causal.json --dry-run
```

[预测配置](../../config/examples/ml-regression/aq-bench-prediction.json)可设定目标、特征、训练与验证及测试标签、缺失处理、有界的 rpart/ranger 候选、种子和解释。训练集内筛选记录缺失、变异、相关性和 VIF 诊断。预测解释包括置换重要性、PDP、ICE 和可选的经验背景排列 Shapley 估计，解释的是预测，不是因果效应。

[合成因果配置](../../config/examples/ml-regression/synthetic-causal.json)用于单个连续处理变量的交叉拟合部分线性斜率，需要声明 DAG、总效应调整集、人工协变量、完整样本、一个辅助模型配置及科学假设。支持独立样本或独立分组折分；任意因果估计目标、工具变量、双重差分与自动因果发现需适配。已知效应合成例子只提供实现证据，观测因果分析需专项研究设计。

未提供项目编号时，结果进入回归技能被 Git 忽略的本地 `results/<run_id>/`。提供项目编号后，结果限制在外部 `assets/results/<project_id>/`，通过 `out_dir` 和相对 `output_files` 自选内部布局。适配器保留已有文件，将记录与临时文件保存在内部 `.airmosaic/<run_id>/`，通过 `artifacts.json` 提供本地产物索引。不发布生成结果；其他适配器保留原契约。

模型计算不需登录或联网。可显式设置 `AIRMOSAIC_R_LIBRARY` 指向审查过的外部包目录，包含 mlr3、mlr3learners、ranger、rpart 和 jsonlite；否则仅使用 R 标准包库。禁用个人启动文件及隐式个人或站点包库。仍需配置三个私人根。MCP 复用同一配置与检查，实际执行需启动授权 `--execute-tool ml_regression_workflow`。

分类、其他学习器、自动调参、预测交叉验证、新数据推理与通用实验编排需继续适配。[发表依据](../../skills/model/shared/machine_learning_model/references/published-basis_ZH.md)区分参考论文的设计与数值复现。科学复核和批准入库独立于执行完成。


工作流合成检查可显式选择 `result_scope=workflow`，按[资产规范](../assets_ZH.md)限定为固定的、被 Git 忽略的工作流结果树及清单登记合成输入。正式项目仍使用外部结果根，默认范围不变。
