# Fixed synthetic generation request

**English** | [中文](request_ZH.md)

Apply [the workflow prompt](../prompt.md) and generate `generated_regression.py` plus the explicit public task `config/examples/ml-regression/workflow-synthetic.json` for the following bounded task:

- Use only the manifest-listed `assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv`; do not inspect original research data or personal settings.
- Predict `outcome` from `x1`, `x2` and `treatment`; the name `treatment` is a synthetic predictor here, not a causal-effect request. Use the released `dataset` labels and all 400/100/100 train/validation/test rows, with `id` as the key.
- Compare the mean baseline, a depth-5 tree and a 48-tree forest with fixed seed 20261028, one thread and a 180-second execution cap. Select by validation RMSE and freeze before final test evaluation. Request bounded permutation/PDP/ICE diagnostics.
- Generate only thin orchestration around `ToolRunnerService.run('ml_regression_workflow', ...)`, using explicit `result_scope='workflow'`. Default to preflight; execution requires `--execute`. No project ID, arbitrary command, automatic installation or network access.
- Independently check saved prediction keys/truths and metric formulas, model reload, source integrity and the fixture-specific baseline criterion. Keep a new result batch, per-run gen_script code/prompt/config materials, environment and hashes under the workflow's ignored results tree.
- Preserve failures, report sanitized status/counts and promote only reviewed generic example source. Do not claim scientific acceptance, automatic model generality or deterministic regeneration from the prompt.

Expected deliverables: an inspectable program, schema-valid task, negative engineering checks and actual synthetic execution evidence. The agent authors/reviews code in the task session; no extra code-generation service is implied.


Follow the [common execution/process-record contract](../../../harness/usage/workflow-handoff.md). New runs use a compact YYYYMMDDHHmm timestamp plus a public task name; the internal run ID only correlates receipts. Preserve gen_script/, events.jsonl, paired retrospective documents and overall workflow.json. No new source_snapshot/ is created; verified redundant synthetic batches are cleaned only with explicit authorization. Generation basis is an explicit design summary, not an uncaptured historical generation transcript.
