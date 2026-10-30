# R 自动调参：配置、调用与检查

[English](automatic-tuning.md) | **中文**

获准方案选择仅在开发数据内自动优化参数时使用本路径。科学依据归[方法](../../../../../methods/shared/machine_learning_model/tuning_ZH.md)。直接 [R 模块](../scripts/r/models/auto_tuning.R)使用 `mlr3tuning::auto_tuner()`，在调用者提供的固定分组折上进行有界随机搜索。它与已注册的 `ml_regression_workflow`、`ml_python_regression_workflow` 分开，不向原任务 JSON 添加调参字段。

## 当前范围与环境

助手接收完整、有限的数值开发表、目标、显式特征、折/分组向量、学习器参数及预算。支持 `regr.rpart` 与 `regr.ranger`，不提供文件读取、测试数据参数、缺失拟合、空间折生成、网格推理或导出。加载模块只定义函数。直接 R 函数不继承执行器路径/凭据检查，也不强制科学审批。

依赖为 `mlr3`、`mlr3tuning`、`paradox`、`future`、`rpart`；森林另需 `mlr3learners`、`ranger`。可在启动 `Rscript --vanilla` 前，通过 `R_LIBS_USER` 选择已存在的依赖库。助手不安装包、不加载个人启动文件。核对包版本时不输出私人库路径。使用顺序 future 计划和单线程学习器。

2026-10-30 核对时，默认本地 R 环境缺少调参包。基础 R 的契约与拒绝检查通过，完整调参/留出示例因缺依赖跳过。这不代表模型训练成功或真实数据路径已验收；研究前应在选定依赖环境运行完整示例。

## 显式配置

`ml_autotune_regression()` 要求显式传入以下参数：

| 参数 | 含义 |
|---|---|
| `development`、`features`、`target` | 获准且仅用于开发的数据框、特征名和数值目标；最多 100,000 行、64 个特征 |
| `fold_id`、`group_id` | 与表逐行对应的向量；2–10 个连续编号的非空折，同一分组不得跨折 |
| `learner_id` | `regr.rpart` 或 `regr.ranger` |
| `search_bounds` | 具名列表，各值为有限数值的上下界对，下界小于上界 |
| `fixed_parameters` | 另一个具名列表，声明固定数值，不能与搜索参数重复 |
| `evaluations`、`max_model_fits`、`seed` | 明确候选次数、拟合预算和种子；最多 64 次评估、641 次拟合，包含最终拟合 |

树参数为 `cp`、`maxdepth`、`minbucket`、`minsplit`；森林为 `mtry`、`min.node.size`、`max.depth`、`num.trees`、`sample.fraction`。其他字段拒绝。整数参数保持整数，`mtry` 不超过特征数。森林树数必须显式固定或搜索，最高 512。随机搜索每批一个候选，未实现自动选择优化器或贝叶斯优化。当前按声明数值尺度均匀抽样，对数搜索需另行审查扩展。

`ranger::min.node.size` 与 `rpart::minbucket` 等参数不可互换。凡从数据估计状态的预处理，都应放在每折学习器或图内部。首版要求完整数值输入，不会在交叉验证前静默填补；流水线扩展需单独测试。

## 调用经审查函数

在仓库根执行；获准开发表和审核后的分组已在内存中：

```r
operations <- new.env(parent = baseenv())
source("skills/model/shared/machine_learning_model/scripts/r/models/auto_tuning.R",
       local = operations)
# args 是上述获准参数列表，不是执行器参数文件。
fit <- do.call(operations$ml_autotune_regression, args)
fit$selected_parameters
fit$budget
# 所有选择冻结后再预测，不向预测表传入目标或标识列。
prediction <- fit$learner$predict_newdata(authorized_prediction_features)$response
```

[完整合成脚本](../frameworks/r/mlr3/examples/automatic-tuning.R)给出树与森林的具体参数列表，另含线性模型和训练均值基线。小规模数值仅用于工程示例，不是科学默认参数。脚本在内存生成输入，不写数据或模型文件：

```sh
Rscript --vanilla skills/model/shared/machine_learning_model/frameworks/r/mlr3/examples/automatic-tuning.R --validate-only
Rscript --vanilla skills/model/shared/machine_learning_model/frameworks/r/mlr3/examples/automatic-tuning.R
```

第一条用基础 R 检查十类有效拒绝，**不进行调参**。完整命令缺包时输出 `dependencies_unavailable`，退出码为 77。依赖齐全时，必须实际调参、在评分前冻结全部四个模型，检查留出预测有限性、同种子树模型回放和内存序列化往返。脚本输出结构化终态，不把部分输出视为成功。

## 核查结果与边界

返回对象包含已拟合 AutoTuner、所选参数、调参档案、准确行/折/分组映射、声明/实际预算和包版本。检查开发 RMSE 有限性、失败候选及实际次数，不把档案成绩当成最终测试精度。AutoTuner 会用全部传入开发表重拟合。`term_evals` 限制调参评估次数，时间终止器不限制所有最终拟合阶段；外部进程时限单独控制。

最终测试目标保留在助手外。各模型族冻结后，在共同最终测试样本上计算 RMSE、MAE 和 `1-SSE/SST` 的 R²。无标签网格预测仍需一致特征/单位、缺失与适用域检查、有界分批及经审查导出代码；本助手不等于全国网格生产流水线。

调用者仅在获准的外部资产项目结果根保存模型、档案和逐行输出，个人映射归 CONFIG_DIR，凭据归受保护机制。模型对象与档案可能保留数据，不能进入 Git。保留实际生成调用代码/配置、明确依据、执行事件、版本及产物检查。真实研究继续遵循既有计划审核要求，本 API 不制造批准或绕过审核。

已核对官方接口：[AutoTuner](https://mlr3tuning.mlr-org.com/reference/auto_tuner.html)、[固定自定义重抽样](https://mlr3.mlr-org.com/reference/mlr_resamplings_custom.html)、[随机搜索批量机制](https://mlr3tuning.mlr-org.com/reference/mlr_tuners_random_search.html)、[参数域](https://paradox.mlr-org.com/reference/Domain.html)。
