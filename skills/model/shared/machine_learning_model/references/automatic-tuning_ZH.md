# 自动调参：直接 R 与 Python 助手

[English](automatic-tuning.md) | **中文**

获准方案选择仅在开发数据内自动优化参数时使用本路径。科学依据归[方法](../../../../../methods/shared/machine_learning_model/tuning_ZH.md)。直接 [R 模块](../scripts/r/models/auto_tuning.R)使用 `mlr3tuning::auto_tuner()`，在调用者提供的固定分组折上进行有界随机搜索。它与已注册的 `ml_regression_workflow`、`ml_python_regression_workflow` 分开，不向原任务 JSON 添加调参字段。

下文的 [Python 助手](../scripts/python/models/grouped_tuning.py)提供独立的内存 sklearn 路径。两个直接助手均不增加 `run-tool` 适配器或 MCP 工具 ID，既有任务 JSON 契约与 ID 保持不变。

## R 范围与环境

助手接收完整、有限的数值开发表、目标、显式特征、折/分组向量、学习器参数及预算。支持 `regr.rpart` 与 `regr.ranger`，不提供文件读取、测试数据参数、缺失拟合、空间折生成、网格推理或导出。加载模块只定义函数。直接 R 函数不继承执行器路径/凭据检查，也不强制科学审批。

依赖为 `mlr3`、`mlr3tuning`、`paradox`、`future`、`rpart`；森林另需 `mlr3learners`、`ranger`。可在启动 `Rscript --vanilla` 前，通过 `R_LIBS_USER` 选择已存在的依赖库。助手不安装包、不加载个人启动文件。核对包版本时不输出私人库路径。使用顺序 future 计划和单线程学习器。

2026-10-30 核对时，默认本地 R 环境缺少调参包。基础 R 的契约与拒绝检查通过，完整调参/留出示例因缺依赖跳过。这不代表模型训练成功或真实数据路径已验收；研究前应在选定依赖环境运行完整示例。

## R 显式配置

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

## 调用经审查 R 函数

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

## 核查 R 结果与边界

返回对象包含已拟合 AutoTuner、所选参数、调参档案、准确行/折/分组映射、声明/实际预算和包版本。检查开发 RMSE 有限性、失败候选及实际次数，不把档案成绩当成最终测试精度。AutoTuner 会用全部传入开发表重拟合。`term_evals` 限制调参评估次数，时间终止器不限制所有最终拟合阶段；外部进程时限单独控制。

最终测试目标保留在助手外。各模型族冻结后，在共同最终测试样本上计算 RMSE、MAE 和 `1-SSE/SST` 的 R²。无标签网格预测仍需一致特征/单位、缺失与适用域检查、有界分批及经审查导出代码；本助手不等于全国网格生产流水线。

调用者仅在获准的外部资产项目结果根保存模型、档案和逐行输出，个人映射归 CONFIG_DIR，凭据归受保护机制。模型对象与档案可能保留数据，不能进入 Git。保留实际生成调用代码/配置、明确依据、执行事件、版本及产物检查。真实研究继续遵循既有计划审核要求，本 API 不制造批准或绕过审核。

## Python 分组调参

使用 Python 3.11+，单独准备 `numpy`、`pandas`、`scipy`、`scikit-learn>=1.4,<2`；助手不安装依赖。`fit_grouped_regression()` 接收两个内存 DataFrame 和显式参数，不读取配置、获取数据、写出结果、生成折或强制研究审核。它与 R AutoTuner 不同：Python 接收可缺失的数值特征和独立测试表，搜索有限候选值列表，返回 sklearn Pipeline；R 要求完整数值开发输入，搜索数值上下界，由调用者另行完成最终测试评价。上文 R 缺依赖的跳过状态不代表 Python 的执行状态。

拟合前，在审核方案中明确模型族、特征、分组定义、留出及搜索范围。开发与测试的组 ID 必须有效且完全不相交。`fold_id` 按开发表行顺序对应，以连续整数 1..k 标记 2–5 个非空折，每组全部落在同一折。数值特征可有 NaN，但每折训练部分的每个特征都须存在观测；目标必须有限，绝不填补。中位数填补器在每折训练内部拟合，线性回归的缩放器也在折内拟合。最终重拟合在全部开发行上重新学习预处理状态。

| 参数 | Python 契约 |
|---|---|
| `development`、`test` | 非空数值特征 DataFrame，含目标与组列；两表无共享组 |
| `features`、`target`、`group_column`、`fold_id` | 显式特征列表、互异的目标/组列名、开发数据逐行折向量 |
| `learner` | `linear_regression`、`decision_tree` 或 `random_forest`；不可注入任意估计器 |
| `search_space`、`fixed_parameters` | 两个独立字典，使用无前缀 sklearn 参数名，参数名不可重叠 |
| `n_iter`、`seed`、`max_fits` | 显式候选上限 1–16、整数种子 0..2³²−1、拟合预算 1–81 |

树/森林参数为 `max_depth`（整数 1–64）与 `min_samples_leaf`（整数 1–10000）；森林另支持 `n_estimators`（整数 1–512）和 `max_features`（大于0且不超过1的数值，遵循 sklearn 所传整数/比例的语义）。树必须显式声明深度，森林还必须显式声明树数，可固定或搜索。每个搜索列表包含 1–16 个互异合法值，组合不超过 65536。树/森林要求非空搜索。线性回归接收空参数字典，不搜索、仅拟合一次，返回空 CV 表和 `best_cv_rmse=None`，不产生可供模型族比较的线性 CV 分数。

树/森林通过 `RandomizedSearchCV` 在显式折上最大化负 RMSE，固定种子、`n_jobs=1`，拟合错误直接抛出。预算包括 `min(n_iter, 组合数) × 折数 + 1` 次拟合，包含开发集最终重拟合。`best_cv_rmse` 是各折 RMSE 的等权均值，不是合并行的总体 RMSE。基于开发证据冻结选择后再评价测试集。此 API 每次针对一个预先声明的模型族，在选择完成后仅预测并评价一次测试集，不提供模型族选择阶段。比较多个模型族时，须在上游安排仅开发数据的 CV 选择，冻结最终族与搜索方案，再调用最终助手；不得按测试分数选择最终模型族或调整搜索范围。

### 完整小型合成调用

在选定 Python 环境、仓库根目录运行以下代码。全部输入在内存生成；样本数与参数仅是工程示例，不是研究默认值。多个模型族可复用一份整理表；助手保留最终估计器与 CV 摘要，不保留所有折模型。

```python
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

path = Path("skills/model/shared/machine_learning_model/scripts/python/models/grouped_tuning.py")
spec = importlib.util.spec_from_file_location("grouped_tuning_example", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

rng = np.random.default_rng(29)
x = rng.normal(size=(32, 2))
table = pd.DataFrame({"x1": x[:, 0], "x2": x[:, 1],
                      "target": 2 * x[:, 0] - x[:, 1],
                      "group": np.repeat(np.arange(8), 4)})
development = table.iloc[:24].copy()
test = table.iloc[24:].copy()
development.loc[[0, 5, 12], "x1"] = np.nan
test.loc[24, "x2"] = np.nan
features = ["x1", "x2"]
groups = development["group"].to_numpy()
fold_id = np.repeat([1, 2, 3, 1, 2, 3], 4)
assert not set(groups) & set(test["group"])
assert pd.DataFrame({"g": groups, "f": fold_id}).groupby("g").f.nunique().max() == 1

# 传入最终测试表前，已固定模型族与搜索范围。
result = module.fit_grouped_regression(
    development, test, features=features, target="target", group_column="group",
    fold_id=fold_id, learner="decision_tree",
    search_space={"max_depth": [2, 3], "min_samples_leaf": [1, 2]},
    fixed_parameters={}, n_iter=3, seed=41, max_fits=10)
selection = result["selection"]
cv = result["cv_results"]
metrics = result["test_metrics"]
predictions = result["predictions"]
assert selection["fits_required"] == 10 and selection["n_candidates"] == 3
assert selection["test_used_for_selection"] is False
assert len(cv) == 3 and np.isfinite(cv["mean_test_score"]).all()
assert np.isclose(selection["best_cv_rmse"], -cv["mean_test_score"].max())
residual = predictions["observed"] - predictions["predicted"]
assert np.isclose(metrics["rmse"], np.sqrt(np.mean(residual ** 2)))
assert np.isclose(metrics["mae"], np.mean(np.abs(residual)))
sst = np.sum((predictions["observed"] - predictions["observed"].mean()) ** 2)
assert np.isclose(metrics["r2"], 1 - np.sum(residual ** 2) / sst)
print(selection["parameters"], metrics)
```

`selection` 记录实际估计器参数、声明的搜索/固定参数、种子、逐行折、分数和预算。核查 `cv_results` 的候选参数及逐折分数；计时列无需精确复现。`test_metrics` 含 RMSE、MAE、`1-SSE/SST` 的 R²，以及 `development_mean_reference` 内的开发目标均值参考。测试目标方差为零时，返回 `r2=None` 和 `r2_note="undefined_zero_test_target_variance"`。均值参考归公共评估，不新增模型族。`predictions` 保留测试索引及观测/预测/参考列。后续无标签预测须先核查适用域、单位和缺失，再以同序数值特征调用 `result["estimator"].predict(feature_frame[features].to_numpy(dtype=float, na_value=np.nan))`。

Python 合成检查覆盖三个模型、组/折拒绝、训练折插补、预算/参数、预测/选择确定性与测试目标扰动。依赖环境中运行 `python -m pytest harness/checks/test_grouped_tuning.py -q`。这些是工程检查，不代表真实站点训练、空间泛化证据或科学验收。模型对象可能保留数据；若调用者另行持久化，须遵守上文外部项目存储边界。

已核对 R 官方接口：[AutoTuner](https://mlr3tuning.mlr-org.com/reference/auto_tuner.html)、[固定自定义重抽样](https://mlr3.mlr-org.com/reference/mlr_resamplings_custom.html)、[随机搜索批量机制](https://mlr3tuning.mlr-org.com/reference/mlr_tuners_random_search.html)、[参数域](https://paradox.mlr-org.com/reference/Domain.html)。
