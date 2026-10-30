# Plan, review, generate and execute

**English** | [中文](planning_ZH.md)

For a new study, begin with the [planning method](../../methods/shared/model_planning.md) and [skill record contract](../../skills/model/shared/machine_learning_model/references/planning.md). Historical configurations are references, not default plans.

1. Inspect authorized dictionary, data identity, split counts and development information; protect held-out outcomes.
2. Save human-readable and machine plans before experiment-code generation. Explain every variable, bounded parameter choice, split and preprocessing decision.
3. Default to waiting for human review. A real user delegation allows an agent review of the identified plan within scope; record both delegation and judgment.
4. After approval, create a fresh experiment caller and task. Reuse skill calculations; identify template copies as copies rather than fresh LLM-generated algorithms.
5. Check exact code, task/data bindings, syntax/scope, synthetic tests and dry-run. Save technical evidence before execution.
6. Execute within approved scope. Verify results and interpretation, then conduct scientific review; preserve prior runs.

## A study plan to inspect before generation

The [AQ-Bench coordinate comparison](examples/aq_bench_coordinate_comparison/README.md) maps literature and data-specific reasons to each variable, parameter, preprocessing step and proposed spatial protocol. It includes paired task drafts, a generation prompt and a code-review map. Its preparation and nested spatial evaluation remain unimplemented; no new models or experiment callers have been generated. Read the stated status before reusing it.

## Executable handoff

The [planned caller](examples/planned_regression.py) implements the ordering. Set the normal separate storage roots and explicit R library first. Replace all placeholders with personal invocation values:

```powershell
python workflows/ml_regression/examples/planned_regression.py --repo "." --plan "<plan.json>" --input-csv "<prepared.csv>" --project-id study --out-dir "<fresh-project-result>"
python workflows/ml_regression/examples/planned_regression.py --repo "." --plan "<plan.json>" --review "<review.json>" --input-csv "<prepared.csv>" --project-id study --out-dir "<fresh-project-result>" --generate
```

The first command only checks the plan; without review it returns pending and writes no experiment code. For delegated judgment, add `--delegation "<delegation.json>"` to the second command. There is no self-approval flag.

Generation saves a plan-bound `gen_script/run.py`, task/review records, generation time and source hashes, plus runner preflight. Its `code-check.pending.json` intentionally leaves `synthetic_tests=false`. After actual tests and code review, create a separate `code-check.json` recording the evidence and time. Do not simply change a flag without checking.

```powershell
python "<fresh-project-result>/gen_script/run.py" --repo "." --input-csv "<prepared.csv>" --project-id study --out-dir "<fresh-project-result>" --execute
```

Missing or failed checks prevent execution. Material or approved-plan changes require a fresh bundle/review as appropriate. Existing results are not overwritten. The registered runner keeps its normal path/dependency/receipt checks. Numerical outputs are indexed by `artifacts.json`; observed workflow boundaries are in `events.jsonl`.

This caller copies reviewed orchestration after approval; it does not provide an LLM API or arbitrary-code generation service. Other agent-authored callers must use the same skill checks. User evidence remains a trusted-host attestation, not authenticated identity proof.

The same caller supports an explicitly declared Python `backend` with `execution.purpose=new_study`. It records fixed implementation hashes and produces a pending-check preview bundle; this grants no execution. After actual checks, execution constructs `review-bundle.json`, reruns preflight and invokes the Python tool. R tasks without a backend keep the historical route. See the [shared plan contract](../../skills/model/shared/machine_learning_model/references/planning.md).
