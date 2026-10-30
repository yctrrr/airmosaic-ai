---
name: skill-authoring
description: Create or revise an AirMosaic operational skill and statically check its metadata, local references and Python resources before review.
compatibility: Python 3.10+ standard library; AirMosaic repository checkout
metadata:
  version: "1.0.0"
---

# Skill authoring

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->

Use the authoritative [authoring rules](../../../../harness/skill-authoring.md) when creating or revising an operational skill. For evidence-driven maintenance routing, use [autoskill](../autoskill/SKILL.md) and the [improvement contract](../../../../harness/skill-improvement.md). Scientific definitions belong in methods; combinations belong in workflows. This entry adds no scientific method and does not infer one from task logs.

Read related entries and the selected task scope, preserve existing identifiers and unrelated work, then write the English entry and its Chinese translation. Use the smallest useful scripts and references. Read [validator operations](references/operations.md) for the exact supported metadata profile and checks.

From the repository root:

```sh
python skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py --repo-root . --skill skills/agent_operations/shared/skill_authoring
python -m pytest harness/checks/test_skill_authoring.py -q
```

Expected: a JSON object with `valid: true`, no diagnostic codes and `execution_verified: false`. Fix reported static defects and review the diff, operational boundaries, bilingual consistency and meaningful synthetic checks. Static success does not verify dependency installation, host discovery, tool readiness or scientific acceptance. Stop before expanding data access, execution or publication beyond the current authorization; accepted actions remain authorized within their original scope.

This is a manual authoring workflow plus an implemented direct static-check helper. It has no registered tool ID and is unsupported by `run-tool`. Repository presence and display metadata do not install it in a host. The repository folder `skill_authoring` and canonical name `skill-authoring` deliberately differ; host packaging may copy into a name-compatible folder under separately authorized installation. Do not rename existing repository folders as a side effect.
