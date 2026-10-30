# 计划、审核、生成与执行

[English](planning.md) | **中文**

新研究先采用[规划方法](../../methods/shared/model_planning_ZH.md)和[技能记录契约](../../skills/model/shared/machine_learning_model/references/planning_ZH.md)。历史配置仅作参考，不作为默认方案。

1. 检查获授权字典、数据身份、划分数量和开发信息，保护留出目标值。
2. 生成实验代码前保存人类可读及机器计划，解释每个变量、参数范围、划分和预处理选择。
3. 默认等待人工审核；真实用户委托后，代理可在范围内审定指定计划，同时记录委托和判断。
4. 获准后创建全新的实验调用代码与任务。计算复用技能，复制模板要如实标注，不能声称新生成了算法。
5. 检查准确代码、任务与数据绑定、语法、范围、合成测试和预检，执行前保存技术依据。
6. 在批准范围内执行，核对产物和解释，再开展科学复核，保留原运行。

## 生成前可审查的案例计划

[AQ-Bench 坐标比较方案](examples/aq_bench_coordinate_comparison/README_ZH.md)将文献和数据依据逐项对应到变量、参数、预处理及拟定空间协议，附配对任务草案、生成提示词和代码审查映射。准备与嵌套空间评估仍未实现，没有生成新的模型或实验调用代码；复用前先核对状态。

## 可执行交接

[计划调用程序](examples/planned_regression.py)实现上述顺序。先设置通常的分离存储根和显式 R 库，将占位符替换为个人调用值：

```powershell
python workflows/ml_regression/examples/planned_regression.py --repo "." --plan "<plan.json>" --input-csv "<prepared.csv>" --project-id study --out-dir "<fresh-project-result>"
python workflows/ml_regression/examples/planned_regression.py --repo "." --plan "<plan.json>" --review "<review.json>" --input-csv "<prepared.csv>" --project-id study --out-dir "<fresh-project-result>" --generate
```

第一条仅检查计划，没有审核时返回待审且不生成实验代码。代理判断时，第二条再加 `--delegation "<delegation.json>"`，没有自行批准的标志。

获准生成后，保存绑定计划的 `gen_script/run.py`、任务和审核记录、生成时间及源码哈希，并进行执行器预检。`code-check.pending.json` 故意保留 `synthetic_tests=false`；实际完成测试及代码审查后，另建 `code-check.json`，写明依据和时间，不能只改标志而不检查。

```powershell
python "<fresh-project-result>/gen_script/run.py" --repo "." --input-csv "<prepared.csv>" --project-id study --out-dir "<fresh-project-result>" --execute
```

检查缺失或失败时不执行。材料或获准方案变化后，按情况重新生成或审核；不覆盖既有结果。注册执行器继续执行原有路径、依赖和记录检查。数值产物通过 `artifacts.json` 索引，工作流实际边界记录在 `events.jsonl`。

本程序在批准后复制经审查的编排代码，不提供大模型接口或任意代码生成服务。代理自行编写的其他调用代码也应使用同一技能检查；用户证据是可信宿主声明，不是经过认证的身份凭证。

同一调用程序支持显式 Python `backend` 且 `execution.purpose=new_study` 的任务。它保存固定实现哈希并生成待检预览材料，不由此放行执行。实际检查后，执行步骤生成 `review-bundle.json`，重新预检并调用 Python 工具。未声明后端的 R 任务保持原路径，参见[共同计划契约](../../skills/model/shared/machine_learning_model/references/planning_ZH.md)。
