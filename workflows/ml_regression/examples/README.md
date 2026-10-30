# Checked generation and execution example

**English** | [中文](README_ZH.md)

The [request](request.md) instantiates the workflow [prompt](../prompt.md). The reviewed [controller](generated_regression.py) uses the registered regression skill and [public synthetic task](../../../config/examples/ml-regression/workflow-synthetic.json). It replays agent-authored code; no LLM generation API is called during execution.

For a literature-grounded real-data plan before code generation, see the [AQ-Bench paired coordinate design](aq_bench_coordinate_comparison/README.md) and [decision-to-code review map](aq_bench_coordinate_comparison/code-review.md). That case is a pending design with task drafts, not an executed spatial validation; the synthetic replay below retains its own scope.

From the repository root, explicitly prepare the separate storage roots and R library using the [skill](../../../skills/model/shared/machine_learning_model/SKILL.md), then run:

```sh
python workflows/ml_regression/examples/generated_regression.py --task-name synthetic_regression
python workflows/ml_regression/examples/generated_regression.py --task-name synthetic_regression --utc-offset +08:00 --execute
```

Preflight does not fit or create result folders. Execution reserves `workflows/ml_regression/results/<YYYYMMDDHHmm>_<task-name>/` exclusively. The name uses minute precision; the explicit offset defaults to +08:00. Internal `--run-id` remains optional receipt correlation, not the visible directory name. Task names must be public lowercase slugs. Conflicting names and existing internal receipts are rejected.

Each result contains:

- `gen_script/run.py`, `task.json`, prompt/request copies, paired `generation*.md` and structured `generation.json`;
- `gen_script/dependencies.json` and `dependencies.patch`, identifying reused public code and preserving changes/additions against a Git base, rather than copying a full source tree;
- timestamped `events.jsonl`, separate runner receipts, model/prediction/explanation artifacts and independent `verification.json`;
- paired `retrospective*.md`, overall terminal `workflow.json` and `delivery-sha256.json`.

No new `source_snapshot/` or input-data copy is produced. The ignored result tree retains all local files; historical runs are not automatically renamed or removed; explicitly authorized redundant synthetic batches may be cleaned after review. The [current checked receipt](verification.json) summarizes the retained batch; an authorized cleanup manifest records removed redundant synthetic batches.

The generation basis is explicit design information saved before computation, not a recreated historical thought trace. Events capture actual controller boundaries; preflight is buffered until a directory is reserved. Full host-agent conversations, generated-code edit history and inner R operations are not automatically captured. Retrospectives are labelled as written afterward. Follow the [common record contract](../../../harness/usage/workflow-handoff.md).

To replay an executed program, use its saved relative path, replacing the example directory below:

```sh
python workflows/ml_regression/results/<timestamp>_<task>/gen_script/run.py --task-name synthetic_replay --execute
```

Replay uses the saved task and generation materials, checks current dependency hashes and creates a fresh result directory. Changed dependencies require review and reconstruction/adaptation; patches are never applied automatically. They preserve LF-normalized public text, with separate byte and normalized hashes, including empty additions and missing terminal newlines.

Inspect overall `workflow.json` and the delivery hashes as well as the separate process receipt. A successful R process alone does not establish complete workflow delivery. The fixed smoke criteria include exact validation/test keys and truths, independently recomputed selected and training-mean baseline metrics, reload equality and test RMSE below the synthetic baseline. Negative engineering checks cover paths, private/external inputs, records, dependency reconstruction and failed verification/sealing. These checks do not approve scientific claims or establish performance on new real data.
