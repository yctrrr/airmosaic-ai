# Static authoring validator

<!-- README-I18N:START -->

**English** | [中文](operations_ZH.md)

<!-- README-I18N:END -->

`scripts/validate_skill.py` uses only the standard library and reads the explicitly chosen skill folder inside `--repo-root`. It checks no more than 200 selected resources and 256 KiB per entry/Python script, rejects filesystem links/reparse points and nested repositories, checks local Markdown links stay inside the chosen repository, and parses Python syntax without importing or running it. References outside the repository, missing references and linked resources fail. HTTP links and anchors are not fetched or verified. Python syntax checking does not establish script safety; non-Python scripts need their own scoped check.

New entries use this scalar frontmatter profile in both languages:

```yaml
---
name: example-operation
description: Perform one bounded operation with reviewed inputs and checks.
compatibility: Python 3.10+; repository checkout
metadata:
  version: "1.0.0"
---
```

The supported profile has single-line string values, balanced optional quotes, and a two-space `metadata` mapping. Quote colon-space, comment-like or boolean/number-like values. It deliberately refuses complex YAML, aliases, tags, duplicate keys and multiline scalars. Use a full YAML validator separately when preserving an existing richer schema. The checker does not migrate existing metadata or demand a repository-wide version retrofit.

`name` is a stable identifier (new names: lowercase letters, digits and hyphens, at most 63 characters); `metadata.version` is a semantic version, and `compatibility` declares runtime/host prerequisites. The translation must keep name, version and compatibility identical. Descriptions are language-specific, 15–1024 characters. Each entry needs one reciprocal language selector. A folder name need not equal its metadata identifier. For an explicitly reviewed existing identifier containing underscores, pass `--published-name existing_id`; this exception preserves the identifier and does not authorize a rename.

The JSON report contains fixed diagnostic codes, resource count and `execution_verified: false`, never source snippets or private paths. Exit 0 means these checks passed; exit 2 means refusal or a static defect. Parser failures also omit unknown argument text. The checker is read-only and has no network, import, execution, registration or installation step. It is not an OS sandbox or a secret detector. Perform a separate privacy and semantic review, meaningful synthetic script tests, and authorized integration checks where required by the authoring contract.

```sh
python skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py --repo-root . --skill skills/agent_operations/shared/skill_authoring
python skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py --repo-root . --skill skills/agent_operations/shared/autoskill
python -m pytest harness/checks/test_skill_authoring.py harness/checks/test_autoskill.py -q
```
