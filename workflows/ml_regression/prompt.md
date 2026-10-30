# Plan, review and generate a regression experiment

**English** | [中文](prompt_ZH.md)

Use this prompt with a host agent. It does not call an LLM API or execute YAML. Follow [the planning handoff](planning.md), [scientific planning method](../../methods/shared/model_planning.md) and [skill record contract](../../skills/model/shared/machine_learning_model/references/planning.md).

```text
Use AirMosaic regression skills for this bounded task.
Mode: <build from requirements | explicitly requested reproduction>.
Question: <physical target, units, unobserved spatial/time domain, labelled reference and use>.
Inputs: <authorized fixed data version and dictionary>.
Review mode: human by default; delegate only if the actual user explicitly authorizes it.
Budget and destination: <allowed models, time/threads and a fresh result scope>.

1. Read methods and the skill. Inspect authorized metadata and development predictors;
   do not use final-test outcomes for feature or parameter design. Identify unsupported operations.
2. Save a human-readable modelling plan and machine plan before experiment-code generation.
   Explain target; every included/excluded variable and physical/proxy meaning; product
   lineage and availability; parameter ranges and actual candidates; independent split
   units and counts; preprocessing; selection/test metrics; interpretation and uncertainty.
   For every decision give the choice, reason, evidence, alternatives and unresolved items.
   Distinguish scientific evidence, software parameter definitions and engineering budgets.
   Derive sample use from data and the study, not fixed demonstration counts.
   Historical configurations are references; do not use them as default new-study plans.
3. Present the plan for human judgment and stop experiment-code generation while pending.
   With explicit user delegation, record the real authorization, scope and exact plan hash;
   perform and save an agent review. Never manufacture a human approval or infer a grant
   from an auto flag. Blocking scientific issues stop the affected operation.
4. Run the skill's generation guard with the approved plan, data and review evidence.
   Only then generate/reuse a small caller and materialize the task; calculations stay in
   skill modules. Record generation mode honestly. For a causal request, retain an
   evidence-based DAG/contrast and uncertainties; do not infer adjustment from importance.
5. Review exact code and configuration, run syntax/scope and synthetic tests, check
   dependencies and dry-run. Preserve technical evidence and code/plan hashes.
   Before execution use the execution guard: task/data must match the plan and the
   exact generated code must match its checks. Plan changes invalidate the old review.
6. Run only within scope, without installing software, reading credentials or expanding
   data access. Use fresh results, preserve failures, verify sample keys/truths, recompute
   RMSE/MAE/1-SSE/SST independently, reload the model and inspect explanation provenance.
   Do not revise settings in response to final-test scores.
7. Preserve plan/review/delegation, prompt, source/config/data identities, environment,
   actual events and a separately labelled retrospective. Scientific project outputs use
   external assets/results/<project_id>; supported synthetic workflow checks keep their
   declared ignored scope. Never overwrite previous results or automatically promote data.
   Report computation, review status, scientific limitations and required adaptations.
```

The [planned caller](examples/planned_regression.py) enforces the two handoffs for supported task settings. It copies a reviewed caller after approval and requires code/test evidence before execution. The [older synthetic program](examples/generated_regression.py) remains a fixed technical replay; it does not demonstrate a new study's plan review.

Follow the [common process-record contract](../../harness/usage/workflow-handoff.md). Result names use YYYYMMDDHHmm plus a public task name. Save generated code and explicit design basis under the run's `gen_script/`, actual events separately, and an explicitly post-run retrospective. Do not invent a generation transcript or hidden reasoning record.
