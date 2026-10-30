# Agent boundaries and general authoring rules

<!-- README-I18N:START -->

**English** | [中文](agent-boundaries_ZH.md)

<!-- README-I18N:END -->


Applies to reading, editing, execution, documentation and sharing. Authorization must identify objects, inputs, writes and external actions; these rules grant no additional authority.

## 1. Start and finish

1. Read root `AGENTS.md` and relevant `SKILL.md`; inspect branch, uncommitted work and real entries.
2. Bound files, data/regions/years, outputs, network behavior and resources.
3. Follow classified usage. Report documentation/code differences and fix invocation guidance within scope.
4. Change only necessary content, preserving originals, results and others' edits. Check target and authorization before overwriting.
5. Validate, inspect the final diff/artifacts, remove private information and report completed/unverified work.

## 2. Information boundaries

| Material | Local use | Shared artifacts |
|---|---|---|
| Usernames, credentials, keys, tokens and cookies | Secret manager and authorized internal tool use | Never publish, including encoded, truncated or hashed substitutes |
| Home directories, drives and private server paths | Explicit local variables/configuration | Logical roots, IDs and repository-relative paths |
| Email, identities, accounts and internal endpoints | Only when needed and authorized | Roles/placeholders, except specifically authorized disclosure |
| Signed/private links and authentication headers | Authorized local calls only | Public entry and parameter categories |
| Browser profiles and sessions | Member-owned local environment | Do not copy to Git, other members or shared attachments |
| Original data, releases and business outputs | Authorized workspace/read-only roots | Metadata, methods, synthetic cases, approved summaries and explicitly publication-authorized licensed public dataset snapshots |

Public source URLs, paper identifiers and repository addresses may be cited. Report suspected credentials only by file, line and category, never values.

Logs/screenshots can expose prompts, stacks, filenames, tables, account areas and URL queries. Replacing only a home directory is not sufficient sanitization.

If a secret entered history, stop propagation and notify the maintainer for provider-side revocation/rotation. Removing the current text does not erase historical exposure. History rewriting, remote deletion and rotation need specific authorization.

Follow the [storage contract](storage-and-credentials.md). Read only needed non-secret configuration; never traverse configuration/authentication to find login details, export cookies, print full environments or package sessions. Authentication and downloads have separate scope; filesystem access does not authorize secret inspection.

A user-prepared client secret file may be internally reused only by its explicitly authorized trusted client/task. The agent must not open, parse, print, copy or hash its contents, or publish its path/fingerprint. Documentation/tests use temporary substitutes, not real secret reads or authenticated-client initialization just to confirm preparation. User-reported preparation is not verified authentication.

## 3. Authorization and effects

| Action | Rule |
|---|---|
| Relevant code/public documentation and checks without external effects | Continue within scope without repeated confirmation |
| Requested edits and new local artifacts | Preserve originals/others' work, use task outputs and record changes |
| Installation, acquisition, paid calls or costly computation | Check existing authorization, target and resource limits |
| Login/account changes | Use the member's session and source flow; do not collect passwords or copy sessions |
| Deletion/overwrite, shared-resource changes or job cancellation | Require target-specific authority and check recoverability |
| Push, merge, publish, upload or send messages | Verify current-task authorization after preparing reviewable sanitized content |

Existing authorization covers necessary follow-up steps. Tool discovery is not permission for bulk acquisition or all analyses.

## 4. General documentation and script rules

Write general guidance in terms of task responsibilities, capability state and boundaries, without enumerating models, frameworks or technology categories. Concrete names, dependencies and invocations belong in skills and classified guides.

Routine method/engineering maintenance uses descriptions, interfaces and synthetic inputs; original-data access requires a bounded task. Methods-only stages contain no concrete data, values, code, project scripts or source fingerprints.

- Locate code/schemas/templates relative to the repository, not an author's machine or editor.
- Pass inputs explicitly; keep non-secret mappings in CONFIG_DIR, browser state in AUTH_DIR and credentials in protected storage. Missing settings cause clear errors, not fallback to personal directories.
- Examples specify interpreter, working directory, parameters, outputs and effects using the actual execution environment's syntax.
- Use argument arrays; never splice user text into shell code or evaluate documentation/model output as commands.
- Tools accept only necessary arguments. Prefer [run-tool](usage/run-tool.md) for supported adapters, with declared parameter/path checks and fresh task/environment boundaries. This trusted-code preflight is not OS isolation or protection for arbitrary direct scripts.
- Inputs default to read-only and outputs to fresh tasks. Do not silently overwrite, change years or fill zeros to recover execution.
- Shared logs use allowed fields: operation IDs, states, counts, units and public error summaries. Complete local diagnostics still exclude credentials, cookies and authentication headers.
- Never print whole environments, browser storage, authentication requests or configuration for debugging. Name missing settings without exposing values.
- Declare module-level dependencies. Core installation does not implicitly fetch releases or perform live acquisition, login or analysis.

## 5. Result claims

Document existence does not verify years, quality or permission. Catalog metadata is not acquisition; file presence is not content, checksum or scientific acceptance. Scripts are not installed tools and JSON examples are not implemented APIs.

Process success does not prove completeness. Report skipped, failed/missing and passed checks separately. Distinguish scenario differences, associations, modeled results and identified causal effects. Synthetic validation is not a successful real-data pipeline.

## 6. Before sharing

1. Inspect changed/new files for caches, accounts, real data and releases.
2. Scan machine paths, identities, keys, authentication headers and signed links; report locations/categories only.
3. Replace machine-specific values with general parameters while retaining correct operations and clear placeholders.
4. Check actual entries, parameters and outputs; mark unimplemented or unrun behavior.
5. Review final diffs/attachments before the authorized sharing action.

Pattern scans supplement review; they do not prove all secrets absent. Do not propagate a discovered secret into tests, error examples or repair notes.

## Data and project results

Experimental results belong to their [project](../projects/README.md), which retains code, settings, evaluation and review records. Only a human scientific decision can admit selected outputs to `assets/`; internal asset organization is deferred. Current runners retain their existing external output contracts until project-directory support is implemented. Generic demonstration exceptions remain adapter-specific. Do not move historical outputs, bypass checks or infer approval from file presence. Configuration, authentication and credentials remain separate. See the [result and review contract](assets.md).


Agent objectives/actions/observations, stop conditions and generation/event/retrospective records follow the [common execution and process-record contract](usage/workflow-handoff.md). Each adapter must declare actual capture coverage; retrospective summaries do not replace observed events.
