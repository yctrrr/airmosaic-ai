---
name: autoskill
description: Review explicitly selected AirMosaic task records, show bounded lexical reuse evidence and prepare a sanitized skill proposal for agent review.
compatibility: Python 3.10+ standard library; explicit external task and storage roots
metadata:
  version: "1.0.0"
---

# Evidence-driven skill maintenance

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->

Use this for a bounded retrospective on named project-record JSON/Markdown or explicitly reviewed source text. Read the authoritative [improvement contract](../../../../harness/skill-improvement.md) and [operations/schema](references/operations.md). Select individual sanitized files in an explicit Git-external task root; the helper never discovers task histories or proposed skills. Provide a controlled public catalog containing skill names and descriptions only.

The helper produces lexical evidence and a suggested `reuse`, `revise`, `compose` or `novel` route. Review the actual evidence and scientific assumptions yourself. A description term overlap is a visible search hint, not semantic understanding. Stale or reported claims cannot establish observed reuse. For `compose`, keep combinations in workflows, operational code in skills and scientific reasoning in methods. Scientific acceptance remains unset by this process.

An optional draft requires an explicitly supplied sanitized structured proposal, authored by the current agent or supplied for review. The helper formats that proposal; it does not infer scientific methods or write instructional prose from logs. Use [skill authoring](../skill_authoring/SKILL.md) to revise the resulting draft and check it. Read the operations reference for a runnable synthetic example and exact flags.

Outputs go only to a fresh external `assets/results/skill_maintenance/<UTC-minute>_<task-id>/`. Raw prose, source paths, source record IDs and data rows are omitted from the generated summary. Do not supply raw datasets, credentials, browser state, authentication/configuration files, private harness plans, session histories or screen captures. Explicit config/auth roots are checked for separation, never enumerated. Privacy heuristics are a supplement to preparing sanitized input; they do not prove arbitrary prose is public.

This is an implemented direct standard-library helper and a review workflow, with no registered tool ID or `run-tool` support. It executes no inspected source and calls no external model, embedding service or screen recorder. It never promotes, installs, registers, commits or updates repository files. Existing task authorization persists for accepted actions in scope; later installation/publication needs its own authorization. On refusal, fix the named fixed-code condition without broad discovery or weakening boundaries. Inspect partial fresh outputs after an I/O failure before retrying with a new task ID.

The adaptation was informed by the publicly reviewed [scientific-agent-skills revision](https://github.com/K-Dense-AI/scientific-agent-skills/tree/5f2bc0341354fd5590aef76a533ada1e1e5b4e62). The bounded AirMosaic implementation and synthetic examples are original; no upstream runtime or collection workflow is imported.
