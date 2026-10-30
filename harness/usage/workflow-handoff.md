# Research-stage handoff and traceability

<!-- README-I18N:START -->

**English** | [中文](workflow-handoff_ZH.md)

<!-- README-I18N:END -->

This guide defines handoff and process-record requirements; each adapter declares implemented coverage. It does not provide a general workflow executor. A fixed sample count, correlation or single test is not a universal scientific acceptance threshold. Originals and private logs remain in authorized local locations.

| Handoff | Required explanation | Acceptance condition |
|---|---|---|
| 01 → 02 | Definitions, units, classifications, coverage and source categories for activity, resources and technology | Accounting scope, units and method semantics are clear; only the declared synthetic inventory route supplies reviewed calculation examples, without implying real-data or runner authorization |
| 01 → 03/04 | Product, variable, time, grid, unit and version for background and component inputs | Distinguish observation, reanalysis and forecast; separately validate conversion/matching; passing through Stage 02 is not required |
| 02 → 03 | Allocation and mapping methods, conservation and gaps | Define task-specific input compatibility; a directory does not establish generated inputs |
| 03 → 04 | Concentration unit, grid, surface definition, averaging, valid scope and validation summary | Check recipient-specific inputs and response metrics; observation validation criteria are task-specific |
| Shared → any stage | Applicability, version, boundaries and comparison design | Reference one skill; do not introduce concrete emission implementation or treat method references as executable tools |

## Records and comparison

Separate method selection, engineering execution and scientific acceptance. Identify baseline/intervention scenarios, permitted changes and common valid scope. Traceable sources alone do not establish causal identification. List missing items and unperformed checks explicitly.

Supported tools record sanitized metadata under their own adapter contract: legacy stage/tool layouts or separate `.airmosaic/<run_id>/record.json` for flexible outputs. This is not a complete cross-stage provenance chain or scientific-validation service. Unsupported workflows do not inherit runner protections. See [scientific design](../../methods/shared/requirements_driven_model_building.md), [data/skill combinations](../../workflows/README.md), [four-stage procedures](../four-step-workflow.md) and [single-tool execution](run-tool.md).

## Agent execution cycle and process records

These are common operating requirements for workflows. Concrete adapters must state which requirements they implement; a written rule does not create an execution engine or complete trace capture.

1. Before acting, state the current objective, evidence, intended operation and authorization/resource boundary in a concise decision summary. Keep assumptions and unverified statements explicit.
2. After acting, update state from the actual tool response and referenced artifacts. Separate plans, attempts, process completion, numerical checks and scientific acceptance. Never invent observations or backdate events.
3. Adjust within the declared development design and budget. Preserve changed code/configuration versions. Freeze the final evaluation boundary; do not choose another candidate from final-test feedback.
4. Keep design/generation basis, actual execution events and post-run retrospective summaries distinct. Explicitly label a retrospective and its writing time. A decision summary is public explanatory evidence, not a claim to capture hidden internal reasoning.
5. Stop the affected branch on missing authorization, incompatible contracts, changed frozen inputs, failed required checks, exhausted budgets or destination conflicts. Preserve partial outputs, report the gap and obtain scientific review where required.

| Record | Required meaning | Timing |
|---|---|---|
| Generation basis | Specific request, code/configuration identity, supported choices, assumptions and missing generation metadata | Preserve before computation; identify summaries written after code generation |
| Execution events | Ordered timestamps, controller/action identity, actual state and bounded evidence references/counts | Capture when operations occur; identify any buffered persistence |
| Retrospective | Completed/failed scope, evidence-based conclusions, limitations and next checks | Write after observed operations; never present as a contemporaneous trace |

Use approved non-secret references, fixed status/error categories and minimal summaries. Keep private paths, identities, credentials, raw model/tool responses and unrelated files out of shared records. Full raw traces are not required by this contract.

The currently reviewed example controller records controller preflight, material preservation, skill invocation and independent verification. It stores paired generation-basis and retrospective documents, observed events and a sealed overall terminal receipt. It replays reviewed generated code without a new LLM call; model/settings for historical generation remain unavailable. Inner R operations, host-agent conversations and complete LLM generation/edit trajectories are not automatically captured. Other workflows retain their documented capabilities.

For storage and timestamp naming, see the [asset contract](../assets.md). For executable task examples, follow the selected workflow and skill. ReAct provides a useful interaction paradigm, while the project owns permissions, scientific controls and evidence contracts. References: [ReAct, section 2](https://arxiv.org/html/2210.03629v3), [MLAgentBench, sections 2.3 and 3.1](https://arxiv.org/html/2310.03302v2).
