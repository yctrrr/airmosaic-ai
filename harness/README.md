# AirMosaic AI collaboration and execution harness

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Choose an actual capability, check inputs, permissions and data contracts, then deliver verified results with sanitized records. General rules do not prescribe a named model, framework or technology category. Concrete capabilities belong in [skill navigation](../skills/README.md) and [classified usage](tool-catalog.md).

## 1. Start here

Use the [four-step workflow](four-step-workflow.md) and [methods](../methods/README.md). Methods-only stages do not provide implementation; reference entries do not imply executability. Documentation work does not read original data.

| Need | Guide |
|---|---|
| Install, inspect catalogs and local files | [Core tools](usage/core.md) |
| Separate data, configuration and authentication | [Storage](storage-and-credentials.md) |
| Acquire/prepare data | [Classified acquisition](usage/data-acquisition.md) |
| Check provenance, uncertainty and normalization | [Data quality](../methods/shared/data_quality.md) |
| Analyze existing results or adapt templates | [Classified analysis](usage/model-analysis.md) |
| Find reusable specialist workflows | [Skills](../skills/README.md), [methods](../methods/README.md) |
| Modify the project safely | [Agent boundaries](agent-boundaries.md), [AGENTS.md](../AGENTS.md) |
| Add a capability | [Authoring](skill-authoring.md), [registration](tool-registration.md) |
| Inspect readiness or execute an adapter | [Queries](usage/tool-registry.md), [run-tool](usage/run-tool.md) |
| Review evidence and unperformed checks | [Verification](verification.md) |

Keep personal task records outside Git. Shared rules describe collaboration; skills describe concrete domain workflows.

## 2. Responsibilities of each layer

| Layer | Responsibility |
|---|---|
| Skill | Task suitability, steps, inputs/outputs and limits |
| Tool | One explicit action using an implemented entry or a clearly labeled template |
| Dataset catalog | Source, owning skill and cache metadata, not acquisition |
| Workflow | Handoffs and assumptions; design is not orchestration |
| Runtime harness | Preflight, reviewed calls, states and receipts; supported adapters only |
| Evaluation | Interface checks, artifact checks and separate scientific validation |

Task authorization → discover capability → check inputs/dependencies/write scope → execute implemented entry → validate artifacts/method → retain local evidence → share sanitized results.

## 3. Team roles

Users define scope and intended use. Domain contributors explain methods, units, assumptions and acceptance criteria. Platform maintainers keep interfaces, metadata and environments compatible. Reviewers check a minimal reproducible case, scientific scope and the actual diff.

Roles may overlap, but a scientific calculation change should receive independent domain review. Roles, repository permissions and task authorization are separate. Use individual accounts, checkouts, environments and task directories; shared input roots remain read-only and caches/outputs must not be concurrently overwritten.

## 4. Task execution

1. Define objects, years, regions, outputs, operations and resource limits.
2. Read the relevant skill and check a real entry point.
3. Check environment, access, input presence and versions.
4. Validate schema, units, time/space alignment, provenance and coverage.
5. Confirm authorized reads, writes, network effects and overwrite behavior.
6. Execute the reviewed command and record completion, waiting or failure.
7. Check artifacts and scientific scope separately from process success.
8. Deliver results, evidence and limits without private identities, credentials or machine paths.

Continue authorized reversible work without repeated confirmation. Missing authorization or necessary information requires clarification; documentation does not authorize installation, downloads or costly work.

A task brief should specify the repository entry, bounded question, allowed inputs and operations, expected evidence, missing-data behavior and sanitized reporting. Do not silently replace missing inputs with zeros, change years/resolution or expand scope.

## 5. Paths and data

Keep reusable code, documentation, schemas and general examples in Git. Use `AIRMOSAIC_LOCAL_WORKSPACE` for `data_cache/`, fresh `output/<run_id>/<tool_id>/`, `runs/<run_id>/` and `temp/<run_id>/`. Personal settings and authentication use separate roots outside Git.

Explicitly override legacy output defaults for new tasks without moving old files. External releases remain separately configured read-only inputs; configuration edits use task copies. Use logical roots and IDs in shared documents. Variable strings are not automatically expanded unless the caller implements it.

## 6. Tool use

Read-only discovery and readiness checks do not execute actions or validate scientific content. Inspect real manifests and use the [runner](usage/run-tool.md) for supported adapters. Review `can_execute`/`blockers` in dry-run, then actual state and artifacts.

Implemented preflight, minimal environments and sanitized receipts apply only to reviewed adapters, not direct scripts. The runner is not an OS sandbox. Authentication, dependency loading, live integration and scientific acceptance are distinct. Unimplemented orchestration or external service interfaces remain proposals.

## 7. Validation and handoff

Record source/configuration versions, scope, parameters, inputs, outputs and validation status locally. Preserve complete diagnostics only in authorized locations without secrets. Share logical IDs, relative paths, counts, units and sanitized errors. Distinguish source review, synthetic checks, real integration and scientific validation. An existing file or successful process is not enough.

Handoffs specify unique keys, units, time/space support, missingness, mappings, uncertainty and acceptance evidence. Do not automatically chain modules or publish a cache merely because an upstream task succeeded.

## 8. Contribution and release

Define a bounded change, inspect existing work, use a task branch/check-out when appropriate, maintain both documentation languages, and follow [authoring](skill-authoring.md) and [registration](tool-registration.md). Run relevant checks and privacy review before an authorized commit, push or release.

Separate approved prerequisites and unrelated work. Do not force-push, rewrite history, start later roadmap tasks or change repository permissions merely because a role or plan mentions them. Future distribution/interfaces require implementation and task-specific validation before being described as operational.
