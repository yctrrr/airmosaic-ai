# 计划记录与审核检查

[English](planning.md) | **中文**

先采用[面向人类的规划方法](../../../../../methods/shared/model_planning_ZH.md)。[计划结构](../contracts/model-plan.schema.json)和[审核助手](../scripts/common/review_plan.py)检查机器交接；R 入口保持 `ml_regression_workflow`，显式 Python 任务使用 `ml_python_regression_workflow`。未指定后端的既有任务仍按 R 处理。

## 记录内容

| 记录 | 必要内容 |
|---|---|
| 计划 | `plan_id`、带时差的创建时间、新建或复现模式、数据与字典及开发概况哈希、完整任务、七类决策、逐变量含义、参数范围、未解决项及默认人工策略 |
| 审核 | 准确的 `plan_sha256`，审核者 `human` 或 `agent`，决定、时间、允许的 `generate` 与 `execute` 阶段、证据引用与陈述、判断依据 |
| 代理审核所需委托 | `source=user`、准确计划哈希，包含 `review` 和对应阶段的权限，记录时间及真实用户授权依据 |
| 代码检查 | 计划与代码哈希、检查时间、审核者和依据；`syntax`、`scope`、`task_binding`、`dry_run`、`synthetic_tests` 均实际通过 |

目标、变量、参数、划分、预处理、评估和解释七类决策，都要说明选择、理由、证据、备选与不确定性。逐变量说明应覆盖实际特征集合；参数范围应包含实际候选值并符合执行器支持范围。范围只是声明，不会隐式启动搜索。

待审、拒绝、旧哈希、阻塞问题或缺少委托时，不允许生成代码。执行还要求任务和数据保持与获准内容一致，并检查准确代码。助手不生成批准，也不从任务措辞推断授权。

## 记录格式示例

以下仅展示结构，默认不放行。哈希用 `plan_hash` 计算，时间必须带时差；占位符不能作为真实证据。宿主依据真实答复填写决定及涵盖阶段，代码检查按实际结果填写，不得复制样例来制造授权。

审核记录示意：

```json
{
  "schema_version": 1,
  "plan_sha256": "<computed-plan-hash>",
  "reviewer": "human",
  "decision": "changes_requested",
  "reviewed_at": "<ISO-time-with-offset>",
  "stages": ["generate"],
  "evidence": {
    "reference": "<actual-user-message-reference>",
    "statement": "<actual-user-decision>"
  },
  "basis": "<scientific-review-reasons-and-limitations>"
}
```

用户委托记录示意：仅列 `review` 不允许生成或执行；须有实际授权才增加对应权限。

```json
{
  "schema_version": 1,
  "plan_sha256": "<computed-plan-hash>",
  "source": "user",
  "permissions": ["review"],
  "recorded_at": "<ISO-time-with-offset>",
  "evidence": {
    "reference": "<actual-user-message-reference>",
    "statement": "<actual-user-delegation>"
  }
}
```

代码检查示意：全部实际通过后才可能执行。

```json
{
  "schema_version": 1,
  "plan_sha256": "<computed-plan-hash>",
  "code_sha256": "<checked-code-hash>",
  "checked_at": "<ISO-time-with-offset>",
  "reviewer": "agent",
  "checks": {
    "syntax": false,
    "scope": false,
    "task_binding": false,
    "dry_run": false,
    "synthetic_tests": false
  },
  "basis": "<actual-check-results-and-evidence-reference>"
}
```

## 只读检查

显式提供记录和获授权 CSV 的位置，在仓库根目录运行：

```powershell
python skills/model/shared/machine_learning_model/scripts/common/review_plan.py --plan "<plan.json>" --input-csv "<prepared.csv>"
```

未提供审核时，应返回 `status=pending_human_review`、两项权限均为假，退出码为3，不生成实验代码或结果目录。实际获准后提供 `--review "<review.json>"`；代理审核还需要 `--delegation "<delegation.json>"`。

执行检查另加 `--phase execute --task-config "<task.json>" --code "<run.py>" --code-check "<code-check.json>"`；只有选择显式运行时副本才使用 `--repo`。科学计划不写凭据、私人身份或机器路径；私人文件位置通过个人配置或调用参数传入。

## 在程序中检查

```python
import importlib.util
from pathlib import Path

repo = Path.cwd()
helper = repo / "skills/model/shared/machine_learning_model/scripts/common/review_plan.py"
spec = importlib.util.spec_from_file_location("plan_gate", helper)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
plan = gate.read_json(Path("plan.json"))
print(gate.plan_hash(plan))
```

生成调用代码前，使用 `gate.require(plan, repo, review=review, delegation=delegation, input_csv=input_csv)`。实际执行前，再提供 `phase="execute"`、实际任务、代码位置与代码检查记录。[工作流调用示例](../../../../../workflows/ml_regression/examples/planned_regression.py)展示两个节点。

## 边界

审核记录属于可信调用方的声明，不是对人类身份的加密认证。助手检查身份摘要、结构、范围及声明的检查，不能证明科学理由真实，也不能证明记录确由人类编写。宿主代理必须从实际用户获得授权，不能自行制造批准证据。

底层 CLI/MCP 执行器接口保持不变，不自动强制科学计划。新研究代理使用本审核路径；旧直接调用及固定合成重放不能证明完成了新的科学审核。两条路径都不构成操作系统沙箱。

## Python 执行材料

Python 新研究使用 `backend=python` 和 `execution.purpose=new_study`。共同计划沿用同一决策/审核结构，任务按 Python 结构校验。没有可配置参数的学习器使用空的参数范围对象；示例不是科学默认设置。

[计划调用程序](../../../../../workflows/ml_regression/examples/planned_regression.py)按声明后端选择工具。真实计划审核后保存调用代码、任务与公开实现哈希，进行静态预检，并保留 `synthetic_tests=false`。实际代码检查完成后，执行步骤生成包含 `plan`、`review`、`delegation`（人工审核时为空）、`code_check`、`code_file` 和 `implementation_sha256` 的材料。runner 的 `review_bundle` 参数指向这份显式本地 JSON。

`runtime/services/model_plan_gate.py` 中的 `python_implementation_hashes(repo)` 只计算固定公开源码清单。在实际生成/审查时记录，不能靠刷新旧哈希跳过审核。预检核对选定控制记录，不解析输入行；执行时核对完整陈述以及数据、任务、调用代码和当前实现。它不能认证真实人工身份或证明所声称的测试确实发生。
