# Adding and maintaining skills

<!-- README-I18N:START -->

**English** | [中文](skill-authoring_ZH.md)

<!-- README-I18N:END -->

This is the authoring checklist for a new or revised AirMosaic skill. For executable registration and host discovery, use the [registration specification](tool-registration.md). Writing guidance does not authorize data access, downloads, model runs, installation or publication.

## 1. Choose scope and location

Choose the home directory by task responsibilities and applicable stages. Put cross-stage capabilities in shared directories and preserve established classifications. Give each skill a clear task and avoid maintaining the same workflow in multiple directories. Read related skills and methods before writing.

General authoring rules do not enumerate specific models, frameworks or technology categories or use them as directory rules. Put concrete names, dependencies and invocation examples in the relevant skills and category navigation.

Stage 02 remains conceptual methods only: no concrete data, parameter values, implementation code, project script names, source fingerprints or execution commands. A new navigation entry does not change this boundary.

## 2. Separate languages and preserve identifiers

Use `SKILL.md` for English and `SKILL_ZH.md` for Chinese. Other paired documents use the existing canonical filename and an `_ZH.md` sibling. Add exactly one reciprocal language selector near the top of each version. Keep meaning, capability status, examples, dates and boundaries aligned; translate prose rather than alternating languages within paragraphs or tables.

Keep tool IDs, commands, flags, configuration keys, data fields, paths, source identifiers and proper names unchanged. Chinese data headers that are required for matching are source literals, not prose to translate. Translate explanatory comments where useful without changing executable behavior.

Only canonical `SKILL.md` participates in normal skill discovery. Its Chinese sibling is a translation, not a second skill or a second tool. Link to a same-language reference when it exists; otherwise retain the actual reference without inventing a translation. Historical long references were not included in the entry-point migration.

## 3. Minimum skill content

The frontmatter must contain a stable `name` and a task-specific `description`. New names use lowercase letters, digits and hyphens, with no personal information. Preserve existing published IDs or document an explicit migration; do not silently rename historical identifiers.

Organize the body to make the following clear:

| Content | Required explanation |
|---|---|
| Purpose and trigger | Which task the skill serves, and when a related workflow should be used instead |
| Current capability | Implemented adapter, manual workflow, template or reference; actual tool IDs if any |
| Inputs and outputs | Formats, logical paths, units, time/space scope, schema and required mappings |
| Prerequisites | Dependencies, versions, login/access requirements and manual preparation |
| Procedure | Concrete selection, preparation, invocation, verification and handoff steps |
| Failure and stopping conditions | Dependency/access failures, uncertain task outcomes, partial artifacts and safe retry checks |
| Agent boundaries | Authorized scope, read/write/network effects, credential separation and protected originals |
| Validation and evidence | What was tested, date/version, synthetic versus live checks, and what remains unverified |

Do not copy a full manual into the entry point. Link substantial conditional procedures from references and reusable scientific explanations from methods.

## 4. Put each resource in the right place

| Resource | Purpose |
|---|---|
| `SKILL.md` / `SKILL_ZH.md` | Task routing, workflow and behavior boundaries |
| `methods/` | Authoritative scientific methods, data provenance, uncertainty, normalization and quality rules |
| Skill `references/` | Tool/API details, operational procedures and verified examples |
| `scripts/` | Reviewed deterministic implementations |
| `templates/` | Code requiring explicit adaptation, labeled as non-executable through run-tool unless implemented |
| `examples/` | Synthetic or generalized task parameters, without personal paths or secrets |
| `agents/openai.yaml` | Optional host presentation metadata, not execution registration |

For a data source, explain original producer versus download provider, product type, version, coverage, units, time semantics, missingness, quality handling and dated primary references. Keep one authoritative explanation in methods and link it from the skill. Record actual operation times with an explicit time zone for live examples; do not invent times for unperformed steps.

## 5. Keep discovery, datasets and tools distinct

| Object | Registration source | What it establishes |
|---|---|---|
| Skill | Canonical frontmatter and host-supported discovery location | Discoverable guidance, subject to actual host verification |
| Host display | `agents/openai.yaml` | Presentation fields, not login or executable functions |
| Dataset | Acquisition `datasets.yaml` when a real declaration is needed | Data-catalog metadata, not acquisition success |
| Tool | `catalog/tools/*.yaml` | Validated tool metadata and declared execution support |
| Method mapping | `methods/index.yaml` | Stage/skill/tool documentation links, not execution permission |

Reference skills may have no dataset declaration or tool ID. Do not invent either for display. Executable tools also require reviewed runner policies/adapters and meaningful synthetic tests; a manifest alone cannot enable arbitrary code. Use actual tool IDs and run-tool for implemented adapters. Preserve historical dataset/skill ID differences documented in the registration specification.

## 6. Paths, credentials and data boundaries

Use three separate existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings, and `AIRMOSAIC_AUTH_DIR` for browser state. Credentials remain in a secret manager or an explicitly authorized official client's existing credential mechanism; do not inspect, copy or expose them. Keep model releases outside Git and use fresh task outputs.

Documentation maintenance uses interfaces and synthetic inputs, not existing original data. Shared documents, examples and logs must exclude usernames, passwords, keys, cookies, private hosts, machine-specific absolute paths, signed URLs and personal task references. State what a reference workflow does not enforce; instructions are not OS isolation.

## 7. Authoring sequence

1. Define the bounded task, stage, status and allowed side effects.
2. Write both language versions and link their methods and operational references.
3. Add only needed examples, templates or scripts. Preserve originals and unrelated work.
4. Add dataset/tool/host metadata only where warranted, following the separate registration rules.
5. Update both language versions of relevant category navigation and the method mapping when applicable.
6. Run the checks below and review privacy. Perform live acquisition or model work only within an explicitly scoped task.
7. Commit/push only when the current task authorizes them, with a concrete reviewed diff.

## 8. Review before delivery

- Validate frontmatter and stable identifiers; the Chinese entry describes the same capability.
- Check reciprocal selectors, relative links, translated anchors and language-consistent navigation.
- Compare executable command blocks, tool IDs, parameters, paths, defaults and validation status across versions.
- Check referenced files and real manifest entries; templates/references remain disabled.
- When metadata changes, use read-only `list-tools`, `describe-tool`, `check-tool` and dataset queries. These are not live execution evidence.
- For changed implementations, run meaningful synthetic failure/success tests before task-authorized integration checks. Documentation-only translation does not need data/model execution.
- Scan shared changes for private information, review findings without echoing secret values, and distinguish real secrets from synthetic fixtures.
- When distributing a skill independently, include its needed resources or versioned public links; repository-relative harness/method links do not automatically travel with a copied folder.

Human-facing complete pathways live in `methods/pathways/`; future executable definitions belong in `core/workflows/`. Neither a narrative nor a definition is a discovered skill or an implemented engine. See the [layout](project-layout.md).
