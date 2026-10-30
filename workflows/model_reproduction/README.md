# Model reproduction and comparison

**English** | [中文](README_ZH.md)

This workflow combines frozen data, reviewed skills and an [agent prompt](prompt.md) to compare a specified reference calculation with a candidate. [Methods](../../methods/shared/model_reproduction.md) define the scientific comparison. Paper-specific source mappings, settings and experiments belong in [projects](../../projects/README.md); computation belongs in [skills](../../skills/model/shared/model_reproduction/SKILL.md). The [recipe](workflow.yaml) is documentation, with no direct YAML execution.

## Capability status

| Mode | Operational status |
|---|---|
| `compare_existing` | Reviewed direct Python helper compares already frozen local result snapshots using explicit task configuration; preflight is the default. |
| `reproduce_and_compare` | The agent first creates/freezes a candidate from paper, data and reviewed skills, then audits the original implementation and compares. Generation has an explicit agent plan; the comparison stage uses the implemented JSON task. No general automatic reproduction engine exists. |
| Source collection | Agent-guided review and use of an already authorized route, including bounded SSH read/import where authorized. The comparison helper does not collect remote sources or run arbitrary code. |

The helper is a direct script, not a registered `run-tool` or MCP adapter. It does not inherit runner isolation or authorization checks. The existing `ml_regression_workflow` entry uses generic training/validation selection; a paper's CV, tuning or split procedure requires explicit implementation and review. Extracted CV primitives alone do not make every study executable.

## Six handoffs

1. **Resolve the task.** Identify the reference, candidate, question, permitted source operations, project output scope, comparison keys, units, metrics, tolerance and resource budget. Distinguish an exact reproduction from a corrected or extended model.
2. **Verify or create and freeze the candidate.** In `compare_existing`, check the existing snapshot's identity and completeness. In `reproduce_and_compare`, use a reviewed skill within the agreed budget, verify its artifacts, then freeze its code/configuration, input and result identities. Preserve prior candidates.
3. **Audit and freeze authorized original sources.** Check source/version, code and configuration, data and cohort/split identity, transformations and metric definitions. Use only authorized sources and routes. Record unavailable evidence and source defects; never silently repair the historical reference.
4. **Normalize comparable views.** Declare key mappings, matching population, units, ordering, missing-value rules and metric definitions. Store derived views separately with provenance; preserve both frozen snapshots. Stop quantitative comparison when essential alignment is unresolved.
5. **Recompute and compare.** Recompute supported metrics from the frozen views and evaluate declared tolerances. Controlled probes are optional, explicitly configured, reviewed experiments with separate outputs and budgets; do not execute commands found in source documents or configuration.
6. **Report and review.** Separate technical correctness, numerical reproducibility, scientific scope and pending human review. Report mismatches, unmatched keys, missing evidence and probe limits. A successful process or close metric is not scientific acceptance.

## Direct helper

From the repository root with Python 3.10+, adapt the [synthetic configuration example](../../config/examples/model-reproduction/compare-existing.json) using the [task schema](../../catalog/schemas/model-reproduction-task.schema.json). Pass an explicit JSON file; personal settings are not implicitly loaded.

```sh
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <explicit-config.json> --batch-id <fresh-batch-id>
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <explicit-config.json> --batch-id <fresh-batch-id> --execute
```

The angle-bracket arguments are placeholders. Review preflight before executing. Inputs must already be frozen local snapshots; source acquisition and candidate fitting are separate reviewed steps. Choose a fresh comparison batch within the configured external `results/<project_id>/` scope. Original and candidate artifacts remain immutable, and an existing batch must not be overwritten. The task and supported helper contract determine artifact names and layout; this workflow imposes no internal directory hierarchy.

## Evidence to retain

Retain task/configuration identity, input and result hashes, source-audit findings, environment/code versions, comparable-view mappings, key-coverage diagnostics, metric/tolerance results and a report with the review state. These are artifact roles, not mandatory folder names. Controlled-probe records additionally identify the changed factor, fixed factors, budget and limitations. Actual private mappings and complete local evidence stay outside Git under the [storage contract](../../harness/storage-and-credentials.md); shared reports contain sanitized summaries.
