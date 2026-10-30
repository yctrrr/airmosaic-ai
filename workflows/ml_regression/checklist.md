# Decisions and checks before reusing the workflow

**English** | [中文](checklist_ZH.md)

| Step | Decide and retain | Stop or adapt when |
|---|---|---|
| Plan/review | A pre-generation plan with choices, reasons, evidence, alternatives, uncertainty and exact review scope | Experiment code is generated while review is pending; historical settings or an auto flag stand in for user judgment |
| Question | Unobserved spatial/time prediction domain, physical target, observed/proxy labels, units and support | Prediction domain and labelled reference are conflated; reference agreement is claimed as physical truth |
| Data | Immutable version/hash, dictionary, sample keys, inclusion rules and missingness | Duplicate keys, incompatible units, unexplained exclusions or changed input |
| Product lineage | Variable/product/version, assimilated/fused/calibration or synthetic-generation observations, evaluation overlap and evidence/unknowns | Upstream use of held-out outcomes is ignored; downstream splitting is claimed to remove it; independence is claimed without evidence |
| Availability | Retrospective/forecast purpose, valid time, issue/release time and prediction origin | Later-available information is used for a claimed operational forecast |
| Validation | Independent unit, training/selection/final-test membership and fixed folds | Repeated stations/groups cross boundaries; random splits are used to claim spatial/future generalization |
| Sample size | Study-specific split counts/ratios, usable independent units and separate computation caps | Demonstration counts are copied without review; unexplained subsampling changes the study cohort |
| Preprocessing | Training-fitted imputation/encoding/selection, with fold-specific fitting where required | Learned information crosses training boundaries; unavailable categories are silently changed |
| Models | Candidate definitions, budget, baseline, seeds and selection metric | Unsupported learners or tuning procedures are silently substituted |
| Evaluation | Frozen choices, matched cohorts, RMSE/MAE and explicit R² formula | Selection scores are presented as final estimates; test outcomes guide another candidate |
| Explanation | Exact fitted model, background, units, bounds and approximation method | A separately refitted model is explained as the final model; importance is called causal effect |
| Causal question | Physical variable meanings, contrast, mechanism evidence, alternative DAGs, identification assumptions and sensitivity | Proxy and physical quantity are conflated; assumed arrows or configuration flags are treated as proof |
| Execution permission | Same approved plan/data/task, exact checked code, real delegation if agent-reviewed, tests and preflight | Stale approval, changed code, missing checks or an agent-issued user grant |
| Reuse | Prompt, source/config/data identities, environment, predictions, checks and review status | Exit code alone is treated as validation; private material enters a reusable example |

The current adapter fits candidates on training data, selects using validation data and evaluates the frozen choice on test data. It provides neither automatic nested tuning nor a spatial/temporal split builder. The shared reproduction functions support explicitly supplied folds and bounded forest searches; a reviewed caller must define its scientific cohort, preprocessing and held-out evaluation. An unsupported design remains an adaptation item.

Predictive interpretation and causal estimation are separate branches. Retain the DAG discussion in the [scientific method](../../methods/shared/machine_learning_model/README.md). A graph check cannot establish that its assumptions hold in the real world.

The runner does not audit product lineage or supply a separate unlabelled regional inference/export entry. Review source documentation and map those operations to an explicit adaptation when needed. Unknown dependence limits the independence claim; retain it in the assessment.

## External design basis

The following are design inputs, not claims that AirMosaic implements these systems or complies with a complete reporting standard. Checked on 2026-10-28.

- [Paper2Agent](https://arxiv.org/abs/2509.06917) motivates extracting reusable operations and iterating against executable tests. Its [prompt guidance](https://github.com/jmiao24/Paper2Agent/blob/main/skills/paper2agent/paper2mcp/references/extensions.md) distinguishes workflow instructions from execution. Applied here: prompts reference real skills; results require an actual run.
- [MLAgentBench](https://arxiv.org/abs/2310.03302) evaluates agents through experiments, code execution and inspected outputs. Applied here: retain generated code and execution evidence rather than grading the plan alone.
- [REFORMS](https://arxiv.org/abs/2308.07832) provides reporting guidance for ML-based science. Applied here: record data/model/evaluation decisions and evidence; the synthetic example is not a scientific validation.
- The [mlr3 book, nested resampling](https://mlr3book.mlr-org.com/chapters/chapter4/hyperparameter_optimization.html#sec-nested-resampling) separates tuning from performance estimation. Applied here: keep final evaluation independent and describe selected CV scores accurately; nested resampling remains an explicit implementation choice.


Follow the [common process-record contract](../../harness/usage/workflow-handoff.md): preserve design basis in this run's gen_script/ before computation, record actual calls in events.jsonl, and explicitly label retrospectives written afterward. Retain task name, precise time/offset and code/dependency identity. Report a complete delivery only after checking overall terminal state and hashes. The current example captures controller boundaries, not full LLM or R traces.
