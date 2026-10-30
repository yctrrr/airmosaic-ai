# R路径：配置并运行回归

[English](operations.md) | **中文**

本说明提供[技能](../SKILL_ZH.md)的环境设置、可运行代码及接口。命令从仓库根目录执行。

## 1. 准备环境

使用 Python 3.10+ 并安装项目。首次部署可在选定的项目环境中执行 `python -m pip install -e .`；执行器还需要能找到 Rscript。

将以下两个占位符替换为既有位置。环境助手设置三个同级根目录 `assets`、`config`、`auth`，运行前在 Git 外创建它们，再单独选择 R 依赖库：

```powershell
$amLocalRoot = "<existing-local-root-outside-git>"
. ./config/examples/environment.ps1 -LocalRoot $amLocalRoot
$env:AIRMOSAIC_R_LIBRARY = "<existing-r-package-library-outside-git>"
```

R 需要 `mlr3`、`mlr3learners`、`ranger`、`rpart`、`jsonlite`。以下 Python 代码按执行时相同的显式包库选择方式检查依赖：

```python
import os
import subprocess

env = os.environ.copy()
for name in ("R_LIBS", "R_LIBS_USER", "R_LIBS_SITE"):
    env[name] = os.environ["AIRMOSAIC_R_LIBRARY"]
packages = "c('mlr3','mlr3learners','ranger','rpart','jsonlite')"
code = f"stopifnot(all(vapply({packages}, requireNamespace, logical(1), quietly=TRUE)))"
subprocess.run(["Rscript", "--vanilla", "-e", code], env=env, check=True)
```

经授权首次安装时，将检查代码中的 `code` 赋值替换为下面这一行，运行后再执行依赖检查：

```python
code = f"install.packages({packages}, lib=Sys.getenv('AIRMOSAIC_R_LIBRARY'), repos='https://cloud.r-project.org')"
```

包安装需要联网。执行器使用选定包库，不自动安装，也不加载个人 R 启动文件。

新研究生成实验任务或调用代码前，先完成[计划及审核检查](planning_ZH.md)。下面的固定示例用于明确要求的技术重放，不作为默认研究方案。

## 2. 运行自带示例

[合成参数](../../../../../config/examples/run-tool/synthetic-regression.json)选择登记的合成 CSV 和完整[预测任务](../../../../../config/examples/ml-regression/workflow-synthetic.json)，无需工作流程序：

```sh
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/synthetic-regression.json --timeout 180
```

预检通过时 `can_execute=true` 且 `blockers` 为空。R 依赖在实际执行前仍为 `unverified`，预检不解析数据行。实际成功状态为 `status=succeeded`，结果目录中生成 `artifacts.json`。

## 3. 配置自己的数据

使用一份整理后 CSV，包含唯一非空样本键、数值目标、声明特征和既有训练/验证/测试标签。在 `categorical_features` 声明类别列。重复站点观测需要站点时期样本键，并另行设计分组或时间验证。

以下代码读取个人配置中的计划和真实审核记录，通过生成检查后才创建任务与执行器 JSON，不覆盖已有文件。先按[计划契约](planning_ZH.md)准备计划和审核记录，代理审核另需真实委托；将输入位置替换为计划对应数据。模板仅用于理解结构，实际设置取自获准计划：

```python
import importlib.util
import json
import os
from pathlib import Path

repo = Path.cwd()
personal = Path(os.environ["AIRMOSAIC_CONFIG_DIR"]) / "ml-regression"
personal.mkdir(parents=True, exist_ok=True)
helper = repo / "skills/model/shared/machine_learning_model/scripts/common/review_plan.py"
spec = importlib.util.spec_from_file_location("plan_gate", helper)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
plan = gate.read_json(personal / "plan.json")
review_path = personal / "review.json"
delegation_path = personal / "delegation.json"
review = gate.read_json(review_path) if review_path.exists() else None
delegation = gate.read_json(delegation_path) if delegation_path.exists() else None
input_csv = Path(os.environ["AIRMOSAIC_ASSETS_DIR"]) / "data/03_atmospheric_transport/ExampleDataset/v1/prepared.csv"
gate.require(plan, repo, review=review, delegation=delegation, input_csv=input_csv)
task = plan["task"]
task_path = personal / "task.json"
params_path = personal / "parameters.json"
parameters = {"input_csv": str(input_csv), "task_config": str(task_path)}
for path, value in ((task_path, task), (params_path, parameters)):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
```

在 `task.json` 中成组修改以下字段：

| 决策 | 字段 |
|---|---|
| 结果与时间 | `target`、`target_unit`、`target_definition` |
| 表结构与变量角色 | `features`、`excluded_features`、`categorical_features`、`id_column` |
| 既有划分标签 | `split.column`、`split.train`、`split.val`、`split.test` |
| 清理与筛选 | `missing.policy`、`missing.sentinels`、`feature_selection` |
| 模型比较 | `models`、`selection_metric` |
| 样本与解释预算 | `row_limits`、`seed`/`seeds`、`explanation` |

### 决定划分规模与计算上限

先根据可用样本量、独立实体及预期时空评估设计训练、验证和测试成员，没有适合所有研究的固定数量或比例。划分标签在上游生成并检查。

再将 `row_limits.train`、`row_limits.val`、`row_limits.test` 设置为计算上限。当前实现在清理后对每个集合选取 `min(可用行数, 配置上限)` 行，上限不会在集合之间重新分配样本。需要保留全部可用行时，在[支持范围](#8-支持的设置)内将上限设为至少覆盖计划数量。研究超出实现范围时，需要经审查的规模适配或有依据的抽样方案；直接复制小示例可能使大样本研究被降采样。

记录来源、可用和选中数量，以及任何抽样依据。注册入口接收留出标签，自动生成划分和通用交叉验证仍需单独适配。

### 核对输入依据

采用[方法中的产品来源与因果设计规则](../../../../../methods/shared/machine_learning_model/README_ZH.md)。写定任务前保留：

| 依据 | 核对内容 |
|---|---|
| 目标与标签 | 待预测的未观测时空区域、物理目标、实测或代理训练标签及评估参照 |
| 特征定义 | 物理量或代理量、单位、层次、空间尺度及平均或滞后窗口 |
| 产品来源 | 变量、产品、版本，上游同化、融合、校准或合成生成方式，是否使用结果，是否重用评估站点或时期，依据来源或未确认状态 |
| 可获得性 | 数据对应时间、实际发布时间及预测起点能否取得 |
| 因果设计（如需要） | 处理与调整变量的物理含义、机制依据、备选 DAG、识别假设及计划的敏感性检查 |

将决策保存在数据字典和任务生成或设计依据中，用既有 `requirements` 文本简要引用，不增加任务结构未支持的字段。结构校验不核实这些依据。未知依赖须明确保留，没有支持证据不能将所得成绩描述为独立验证；不能只为通过校验而将 `causal.assumptions` 填成真。

预测入口需要带标签行进行训练与评估。独立的无标签区域预测表及场数据导出，仍需经审查的推理与导出适配。

数值文本必须能解析为有限数值。空单元格和配置的缺失标记转为缺失，不填补目标。`drop` 使用完整案例，`train_median_mode` 在训练集拟合特征填充值。未知类别默认报错，只有显式设置 `unseen_categories=train_mode` 才执行映射。

私人路径保留在个人文件中。输入路径支持 `${AIRMOSAIC_ASSETS_DIR}`；示例将配置文件位置解析为绝对路径，不支持任意环境变量占位符。

使用个人参数文件运行项目：

```powershell
$amParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "ml-regression/parameters.json"
python -m runtime.cli run-tool ml_regression_workflow --params-file $amParams --project-id air_quality_study --dry-run
python -m runtime.cli run-tool ml_regression_workflow --params-file $amParams --project-id air_quality_study --timeout 180
```

项目标识选择外部 `assets/results/air_quality_study/<run_id>/`。仅在需要该项目根下其他新目录时，向参数 JSON 添加 `out_dir`。

## 4. 从 Python 或 MCP 调用

以下可执行 Python 示例预检与 CLI 相同的合成任务：

```python
import json
from pathlib import Path
from runtime.services import ToolRunnerService

parameters = json.loads(Path("config/examples/run-tool/synthetic-regression.json").read_text(encoding="utf-8"))
record = ToolRunnerService().run(
    "ml_regression_workflow",
    parameters,
    dry_run=True,
    timeout=180,
)
print(json.dumps(record, ensure_ascii=False))
```

预检及依赖检查通过后，将 `dry_run=False` 执行计算。使用个人任务文件时，将 `parameters` 参数替换为 `params_file=str(params_path)`，并增加 `project_id="air_quality_study"`，不要同时传入两种参数来源。

MCP 发送相同的执行器参数，服务端需开放 `--execute-tool ml_regression_workflow`；客户端配置见 [MCP 说明](../../../../../harness/usage/mcp_ZH.md)。

## 5. 读取和检查结果

上面的通用预测调用实际成功后，按以下方式读取：

```python
if record["status"] == "succeeded":
    output = Path("skills/model/shared/machine_learning_model/results") / record["run_id"]
    files = json.loads((output / "artifacts.json").read_text(encoding="utf-8"))["files"]
    metrics = json.loads((output / files["metrics"]).read_text(encoding="utf-8"))
    print(json.dumps(metrics["test"], ensure_ascii=False))
```

项目调用改用选定的项目结果根。索引解析可配置文件名，`artifacts.json` 本身固定。预测角色包括 `model`、`predictions`、`metrics`、`candidates`、`preprocessing` 及选定解释；PLR 角色包括 `causal_effect`、`causal_residuals`、`causal_folds`、`causal_models` 和 `dag`。完整角色见[输出契约](../contracts/output-files.json)。

检查保留样本数和特征，从留出预测独立重算指标，确认模型重载。失败时可能只有部分文件且没有索引：查看执行记录或状态，再使用新运行，不覆盖已有产物。

## 6. 因果与复现选项

`analysis=causal_plr` 从完整[合成因果任务](../../../../../config/examples/ml-regression/synthetic-causal.json)开始。填写一个数值处理、单位及 `treatment_scale`、结果及单位、DAG 和人工调整集；`features` 必须等于 `adjustment_set`。使用 `missing.policy=drop` 且只设一个辅助模型候选，六项假设声明应在科学设计完成论证后填写。

保留的训练与验证数据合并交叉拟合，测试集不参与效应估计。折数为 2–10，样本至少为 `max(30,10*folds)` 行。分组模式至少需要 `max(5,folds)` 个组，并声明组间独立。系数表示每 `treatment_scale` 个原始处理单位对应的结果单位变化。设计决策见[领域映射](air-pollution_ZH.md)。

独立的 `scripts/r/models/reproduction.R` 函数库接收开发数据及固定折号，执行有界森林搜索；它不是注册入口的自动交叉验证选项。

## 7. 脚本接口

`scripts/r/run_regression.R` 通过执行器接收 `--input-csv`、`--task-config`、`--out-dir`。模块共享 `context` 环境，不是单独的 CLI 工具。

| 模块 | 操作与交接 |
|---|---|
| `scripts/r/common/target.R` | 记录目标、变量角色和划分契约 |
| `scripts/r/common/prepare.R` → `scripts/r/common/select.R` → 继续整理 | 读取一次数据，筛选标记为训练的行，形成队列并拟合训练集预处理 |
| `scripts/r/models/fit.R` | 拟合基线与候选，按验证损失选型，保存模型包 |
| `scripts/r/common/evaluate.R` | 评分冻结的验证/测试预测，检查模型重载 |
| `scripts/r/contribution/explain.R` | 验证集置换，训练背景 PDP/ICE，可选经验背景 Shapley 估计 |
| `scripts/r/causal/causal.R` | 替代拟合/评估/解释，执行交叉拟合 PLR 与推断 |
| `scripts/r/common/io.R` | 按角色写入、状态及指标定义 |
| `scripts/r/models/reproduction.R` | `reproduction_forest()`、`reproduction_search_forest()`；先加载 `scripts/r/common/io.R` 以使用 `metrics()` |

R 适配器的 Python 配置及产物验证位于 `runtime/services/mlr3_workflow.py`，依赖、路径及记录由公共执行器处理。直接调用 R 模块不继承这些保护。

## 8. 支持的设置

以[任务结构](../../../../../catalog/schemas/ml-regression-task.schema.json)为准，适配器支持：

| 设置 | 范围及行为 |
|---|---|
| 输入 | 最多 100,000 行和 64 个候选特征 |
| 预测队列 | 至少 10 条可用训练行、各 5 条可用验证/测试行；上限为 20,000/5,000/5,000 |
| 候选 | 声明 1–4 个，另加均值基线；按验证 RMSE 或 MAE 选型 |
| `regr.rpart` | `cp`：0–1；`maxdepth`：1–30；`minsplit`：2–10,000；`minbucket`：1–5,000 |
| `regr.ranger` | `num.trees`：1–1,000；`mtry`：1–64 且不超过保留特征数；`min.node.size`：1–10,000；`max.depth`：1–30；`sample.fraction`：0.1–1；`replace`：布尔值 |
| 解释 | 最多请求 5 个特征；背景/验证样本 5–200；重复 1–10；网格点 2–20；类别网格最多 32 个水平 |
| Shapley 估计 | 1–20 行、2–32 次排列；配置行数 × 排列数 × 候选特征数 × 背景行数 ≤ 2,000,000 |

Ranger 固定单线程，省略树数时使用 100；rpart 内部交叉验证关闭。其他省略的学习器参数沿用安装版本。适配器不自动调参、创建交叉验证划分或合并训练与验证重拟合优胜模型。

`train_filter` 默认缺失比例 0.5、不同值数量 2、绝对相关阈值 0.95。筛选使用目标过滤和抽样前的全部训练标签源行，填补使用选中训练队列；相关候选按声明顺序移除，VIF 只作诊断。`row_limits` 可能触发抽样，应查看来源、可用和选中数量。

PDP/ICE 使用训练数据第 5–95 百分位网格或类别水平。`explanation.features` 选择置换/PDP/ICE 变量，可选 Shapley 覆盖全部保留特征。这些属于预测解释，因果设计使用单独分支。
