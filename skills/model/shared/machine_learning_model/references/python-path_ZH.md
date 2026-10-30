# Python 回归路径

[English](python-path.md) | **中文**

本页说明已注册的 sklearn 回归适配器。直接运行 CPU 合成 Transformer 软件案例时，使用独立[软件指南](transformer-software_ZH.md)，其配置不能传给 `ml_python_regression_workflow`。

通过注册工具 `ml_python_regression_workflow` 使用 `scripts/python/run_regression.py`。配置模式为 `catalog/schemas/python-ml-regression-task.schema.json`，完整合成示例为 `config/examples/machine-learning-model/python/synthetic-regression.json`。当前实现预测回归；Python 因果 PLR 仍是计划能力。科学准备与审查见[主技能](../SKILL.md)。

输入必须是准备好的单个 CSV，包含调用者提供的唯一非空 ID、明确目标和特征，以及明确且互异的 train/val/test 标签。未知标签或任意分组中的重复 ID 都会被拒绝。不会推断随机划分。原始文件不修改；`prepared.csv` 保留纳入行的原始列和单元格字符串，预测表保留 ID 与源行号。这只核验所提供表的约束，不认证上游来源或科学适用性。

显式选择缺失策略 `error`、`drop` 或 `impute`，并列明数值哨兵。`impute` 下缺失目标仍被排除；特征使用训练集的中位数或最高频类别填补。`preprocessing.json` 记录各分组和列的缺失数量、排除数量及带 ID 的排除行。缩放、填补和独热编码均在每条模型流水线内仅拟合训练行。未见类别映射为全零编码；训练特征全缺失、类别数过高会失败。ID、目标、划分列不得进入特征。当前仅支持手动列选取。

必须包含明确的 `baseline_mean` 候选，可再选择 `linear_regression`、`decision_tree`、`random_forest`。禁止任意估计器、表达式、回调和外部序列化模型。树深与森林树数必须显式填写。上限为 8 个候选、每森林 512 棵树、所有候选累计 1024 棵树、每分组 100000 行及 500 万个稠密预处理单元；调用者可设更小行上限，超限失败而非抽样。森林单线程。候选是固定参数试验，尚无 CV 调参引擎。所有候选仅拟合训练集，以验证 RMSE 最小者选择，并列取首个；最终模型不重新拟合验证集，冻结后才产生测试预测。测试指标不参与选择。成功必须通过刚保存模型的重载与独立 RMSE/MAE 检查。R/Python 森林不保证数值等价。

`explanation.methods` 分别选择描述性 `permutation`、`pdp`、`ice`、`shap`。解释使用有界验证行，依赖网格和 SHAP 背景来自训练集。置换输出验证 MSE 增量，PDP/ICE 支持数值特征。SHAP 需要可选 `shap` 依赖，并显式声明 `shap_algorithm=permutation`、`shap_background=training_first_rows`、`shap_output=raw_prediction` 及计算预算。当前仅支持有限值的原始数值特征，基值与贡献和必须在容差内重构预测。缺失所选依赖或能力明确失败，不伪造成功解释；这些贡献均不是因果效应。

产物清单使用共享角色：目标约定、准备数据、预处理、特征选取、候选、保存模型、带 ID 预测、指标、来源、重现核验、状态和所选解释表。`output_files` 可改安全相对文件名；`artifacts.json` 固定，Python 模型扩展名仍为 `.joblib`。拒绝覆盖已有产物。运行时唯一反序列化对象是本次刚保存的可信模型。Runner 负责目录、环境和审查约束；直接脚本不继承其存储边界。

新研究设置 `execution.purpose=new_study` 并通过 `--review-bundle` 提供审查包。共享门控绑定准确输入、规范化配置、方案审查、经审查的生成调用代码及当前固定实现。工程示例使用 `engineering_replay`；Runner 将其限制为仓库清单中通过哈希核验的合成数据。单独在直接脚本中声明工程用途不认证合成来源或科学有效性。

选择可信 Python 环境并准备 `numpy`、`scikit-learn`、`joblib`、`jsonschema` 后运行（仅选择 SHAP 时需要该依赖）：

```sh
python skills/model/shared/machine_learning_model/scripts/python/run_regression.py --input-csv assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv --task-config config/examples/machine-learning-model/python/synthetic-regression.json --out-dir <fresh-authorized-result-directory>
```

此例仅为工程回放。模型拟合和重载不构成真实数据验证或科学验收。每次运行保存实际版本，不自动安装依赖。

API 参考：[sklearn OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html), [SHAP PermutationExplainer](https://shap.readthedocs.io/en/stable/generated/shap.PermutationExplainer.html).

## CLI 与 MCP 入口

选择包含项目核心及所需依赖的环境。已测包为 scikit-learn 1.9.1、NumPy 2.5.4、SciPy 1.18.1 和 joblib 1.6.0；可选 SHAP 路径在独立 Python 3.14 环境中使用 SHAP 0.54.1 实跑。这是已检查的环境快照，不要求所有环境统一升级。

```sh
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/synthetic-python-regression.json --dry-run
python -m runtime.cli run-tool ml_python_regression_workflow --params-file config/examples/run-tool/synthetic-python-regression.json --timeout 180
```

需要三个分离根目录，本次检查未改动项目主环境。新研究采用[共同计划/审核材料流程](planning_ZH.md)，没有自行批准开关。MCP 使用相同工具、参数和默认预检，实际执行还需要启动授权 `--execute-tool ml_python_regression_workflow`。
