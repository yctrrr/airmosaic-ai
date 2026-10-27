# Model building from research requirements

<!-- README-I18N:START -->

**English** | [中文](requirements_driven_model_building_ZH.md)

<!-- README-I18N:END -->

**Status: workflow design.** The user supplies data and research requirements. The agent combines data contracts with available method skills to propose and build an appropriate model. Existing project code supplies reproduction cases, rather than fixing every new task to the same model. This document does not register a training tool or create a workflow engine.

## Capability library, task and reference case

| Component | Responsibility |
|---|---|
| `methods/` | Explain applicability, scientific assumptions, validation and interpretation limits |
| `skills/` | Explain concrete data preparation, software operations, model construction and artifact checks |
| Data descriptions | State sample units, fields, units, temporal/spatial support, feature availability and permitted use; actual files remain outside Git |
| `catalog/` | Declare actual tool capabilities and implementation status |
| MCP and core | Expose existing declarations and controlled operations; future orchestration must reuse these services |
| Reproduction cases | Pin a reference implementation, input contract, execution recipe and expected checks for independent comparison |

Two task modes use the same capability library. **Build** follows a new research requirement and records why a method was selected. **Reproduce** follows a specific frozen reference case and compares the agreed outputs. A new algorithm is not required to reproduce another algorithm's predictions; its scientific evaluation is specified separately.

## What the user provides

The initial interaction should request an authorized input reference, the target or research objective, and a plain-language modeling requirement. The agent organizes the remaining specification from available metadata and skills, asking only for missing decisions that materially affect the task. Users do not need to know backend learner keys, server names or shell commands.

The following is a **design example**, not an implemented configuration loader or run-tool parameter file. A personal copy belongs in CONFIG_DIR. Null values and empty lists are unresolved requirements, not permission to use every input or model.

```yaml
spec_version: 1
document_type: model_build_request
execution_enabled: false
user_request: null
mode: null  # build or reproduce
data:
  dataset_id: null
  input_ref: null
  format: null
  sample_unit: null
  target: null
  feature_columns: []
  entity_column: null
  time_column: null
  units: {}
  feature_available_at: {}
model_requirements:
  required_methods: []
  constraints: []
  explanation_questions: []
validation:
  deployment_scenario: null
  split_design: null
  primary_metric: null
  acceptance_conditions: []
reference_case_id: null
resources:
  max_trials: null
  max_walltime_minutes: null
  max_threads: null
```

Actual paths and private source mappings stay in the personal configuration. An input reference resolves only within the current authorization; it does not authorize a whole-directory scan. Data loading stays in the controlled computation environment. Send only the necessary schema and approved summaries to the reasoning agent, without automatically transmitting data rows to an external service.

## End-to-end steps

| Step | Agent work | Required output or stopping condition |
|---|---|---|
| 1. Interpret requirements | Identify prediction, comparison, explanation or another explicit objective; record the target, deployment scenario and constraints | A bounded task specification; resolve ambiguous target/time semantics before modeling |
| 2. Match data and skills | Match input metadata and units to available methods and operational skills; inspect actual implementation status | Data contract and a capability/gap list; missing features, unavailable dependencies and unsupported methods remain explicit |
| 3. Design validation | Choose split units and time boundaries for the intended deployment; reserve the final evaluation set; specify baselines, metric direction and resource budget | Frozen split and evaluation plan, without fitting transformations on the held-out data |
| 4. Construct the model | Generate task-specific code or adapt a suitable implementation; make paths, columns, algorithms and budgets explicit | Reviewable source/configuration and synthetic contract checks; generated code is not automatically trusted or registered |
| 5. Execute a bounded task | Use a reviewed operation within the authorized input/output and compute boundary | Dependency, preflight and process receipts plus fresh artifacts; a failed stage blocks dependent work |
| 6. Evaluate and explain | Freeze development choices, evaluate the agreed holdout once as designed, and answer the stated interpretation questions | Metrics, baselines, failure/coverage checks and explanation limits; predictive attribution alone is not causal identification |
| 7. Compare and deliver | Run a reference case only when relevant and authorized; inspect model/input compatibility and reproduction checks | Model card, source/configuration versions, input contract, split record, metrics and artifact index; detailed rows/models stay local |

Repeated entities, spatial structure, time trends and lagged features affect the split design. Fitted imputation, scaling, encoding and feature selection belong inside the appropriate training/resampling scope. Preserve the trained transformations, field order, types and levels for prediction. Do not select a preferred model by repeatedly inspecting the final test set.

## How reference code validates the capability

Each reference case needs a stable case ID and source version, authorized input description, original method/configuration, runtime/dependency information, output contract, comparison metric and tolerance, and known limitations. Keep private code roots, data and expected detailed outputs in a local mapping. A file's presence or an old success message is not a current reproduction result.

Use three distinct checks: synthetic engineering checks for interfaces and failure behavior; reproduction of the specified original calculation under its agreed inputs; and scientific evaluation of a newly requested model. For stochastic calculations, document seeds, split identity and acceptable numerical/statistical variation rather than demanding identical files. Review the reference implementation itself before treating its outputs as an acceptance target.

## Integration boundary

The first source-audited example is the [air-quality ozone regression case](references/air_quality_o3_reference.md). It supplies concrete reproduction/adaptation evidence; its original feature set, split and budget do not constrain every new request.

Human workflow narratives live here. Reusable software instructions belong in the relevant model skills, such as the [current model-use category](../../skills/model/machine_learning/README.md). Private reproduction inputs and model artifacts use the data workspace, with non-secret source mappings in CONFIG_DIR and authentication kept separate.

Current model references are not training adapters. MCP can discover registered capabilities and read skill entries, but cannot execute arbitrary newly generated code. Future validated stage bindings belong under `workflows/` after a reviewed engine/adapter exists. Keep unimplemented operations visible as gaps rather than inventing callable tool IDs.

## Suggested implementation order

1. Complete a data dictionary and stable sample keys for the reference case; freeze its source, cohort, split and comparison contract.
2. Extract preparation, fit/tune, evaluation and explanation into independently callable operations. Preserve the legacy source and version any alignment or validation corrections separately. Check failure behavior and branch alignment with synthetic inputs first.
3. Add the task-specification loader, capability matching, bounded operation adapters and artifact checks. Only reviewed implemented adapters become catalog/MCP execution tools; stage orchestration needs its own implementation.
4. Verify the first bounded reproduction within a separate authorized compute task, then add other user-requested models and cases. Check model choice and evaluation against each task's requirements rather than enforcing the original random forest everywhere.

## Data and project results

Follow the [asset contract](../../harness/assets.md). Shared data outside Git uses `assets/data/<stage>/<dataset-name>/<version>/` with actual dataset names. Projects reference fixed versions in configuration without cross-stage duplication. New results use `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`, with records and temporary files inside that run. New calls provide project and stage together. Compute/check, obtain human review, then register selected data in a fresh version; never overwrite originals or existing versions. Personal settings, authentication and credentials remain separate. Existing files are not migrated; automatic approval and registration services are not implemented.
