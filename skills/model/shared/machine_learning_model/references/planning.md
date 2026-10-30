# Plan records and review checks

**English** | [中文](planning_ZH.md)

Use the [human planning method](../../../../../methods/shared/model_planning.md) first. The [plan schema](../contracts/model-plan.schema.json) and [review helper](../scripts/common/review_plan.py) check the machine handoff; the R entry remains `ml_regression_workflow`, while an explicit Python task uses `ml_python_regression_workflow`. Tasks without a backend retain the historical R interpretation.

## Records

| Record | Required content |
|---|---|
| Plan | `plan_id`, creation time with offset, build/reproduce mode, data/dictionary/development-profile hashes, complete task, seven decision topics, per-variable meanings, parameter ranges, issues and default-human policy |
| Review | Exact `plan_sha256`, reviewer `human` or `agent`, decision, review time, allowed `generate`/`execute` stages, evidence reference/statement and judgment basis |
| Delegation, for agent review | `source=user`, the exact plan hash, permissions including `review` and the requested stage, recorded time and actual user authorization evidence |
| Code check | Plan/code hashes, check time, reviewer and basis; true checks for `syntax`, `scope`, `task_binding`, `dry_run` and `synthetic_tests` |

Each decision topic—target, variables, parameters, split, preprocessing, evaluation and interpretation—needs a choice, reason, evidence, alternatives and uncertainty. Variable notes must cover the actual feature set. Declared parameter ranges must contain every actual candidate value and fit the supported adapter. Ranges are descriptive; they do not launch a hidden search.

A pending or rejected review, stale hash, blocking issue or missing delegation does not permit generation. Execution additionally requires unchanged approved task/data and a technical check of the exact code. The helper does not create approvals or infer authorization from task wording.

## Record shapes

These illustrate structure and deny by default. Compute identity with `plan_hash` and use timestamps with offsets. Placeholders are not evidence. The host records the actual decision and covered stages, and records checks from real observations; copying an example cannot create authorization.

Illustrative review:

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

Illustrative user delegation: `review` alone grants neither generation nor execution. Add stages only from actual user authorization.

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

Illustrative code check: every check must actually pass before execution.

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

## Read-only gate

Use explicit paths to records and authorized CSV. Run from the repository root:

```powershell
python skills/model/shared/machine_learning_model/scripts/common/review_plan.py --plan "<plan.json>" --input-csv "<prepared.csv>"
```

Without review, expect `status=pending_human_review`, both permission flags false, and exit code 3. No experiment code or result folder is written. Supply `--review "<review.json>"` after real approval; agent review also needs `--delegation "<delegation.json>"`.

For execution, add `--phase execute --task-config "<task.json>" --code "<run.py>" --code-check "<code-check.json>"`. Use `--repo` only to select an explicit copied runtime. Never put credentials, personal identities or machine paths in the scientific plan; pass private filesystem locations through personal configuration or invocation arguments.

## Calling the checks

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

Before generating a caller, use `gate.require(plan, repo, review=review, delegation=delegation, input_csv=input_csv)`. Before actual execution, use the same call with `phase="execute"`, actual task, code path and code-check record. The [planned workflow caller](../../../../../workflows/ml_regression/examples/planned_regression.py) demonstrates both points.

## Boundaries

Review records are trusted-caller attestations, not cryptographic human authentication. The helper validates identity, structure, scope and declared checks; it cannot prove scientific reasons or that a human truly authored a supplied record. Host agents must derive authorization from the actual user, never manufacture approval evidence.

The low-level CLI/MCP runner retains its existing interface and does not automatically enforce a model plan. New-study agents use this plan-aware path; old direct calls and fixed synthetic replays are not evidence that the new scientific review happened. Neither path is an OS sandbox.

## Python execution bundle

For a Python new study, use `backend=python` and `execution.purpose=new_study`. The common plan keeps the same decision/review structure and validates its task against the Python schema. Learners without configurable parameters have an empty parameter-range object; examples are not scientific defaults.

The [plan-aware caller](../../../../../workflows/ml_regression/examples/planned_regression.py) selects the declared backend. After genuine plan approval it saves the caller/task and public implementation hashes, runs static preview and leaves `synthetic_tests=false`. After actual code checks, its execution step creates a bundle with `plan`, `review`, `delegation` (null for human review), `code_check`, `code_file` and `implementation_sha256`. The runner's `review_bundle` parameter names that explicit local JSON.

`python_implementation_hashes(repo)` in `runtime/services/model_plan_gate.py` computes only the fixed public source inventory. Record it during actual generation/review; do not refresh stale hashes to bypass review. Preview checks selected control records without parsing input rows. Execution checks the full attestation, input/task/caller hashes and current implementation. It cannot authenticate the human or prove the claimed tests took place.
