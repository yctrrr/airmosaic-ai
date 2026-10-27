# Skill, dataset and tool registration

<!-- README-I18N:START -->

**English** | [中文](tool-registration_ZH.md)

<!-- README-I18N:END -->


This specification describes registration boundaries and implemented behavior. Concrete capability inventories and dependencies belong in the [catalog](tool-catalog.md) and classified usage guides. General rules do not enumerate models, frameworks or technology categories.

## 1. Different objects

| Object | Authoritative source | Effect |
|---|---|---|
| Skill | `SKILL.md` frontmatter | Workflow guidance discoverable by a compatible host |
| Host display | Skill `agents/openai.yaml` | Optional presentation, not executable functions or login |
| Dataset | Acquisition `datasets.yaml` | Catalog metadata, not download or content verification |
| Tool | `catalog/tools/*.yaml` | Validated metadata and declared execution support |
| Method mapping | `methods/index.yaml` | Documentation links between stages, skills and real tool IDs |

Workflow/request files do not replace implementations. Method `skills` must point to actual canonical entries; `tool_ids` must exist. Reference skills need not have a tool ID.

## 2. Stable identifiers

New skill names use lowercase letters, digits and hyphens; tool IDs use lowercase letters, digits and underscores. Titles are human-readable. Do not embed personal accounts, machines, absolute paths or credentials.

Historical frontmatter names, dataset skill IDs, directory names and aliases can differ. Inspect actual metadata through the relevant service and skill rather than guessing. Preserve existing public IDs or provide an explicit migration. An alias does not establish the scope or completeness of its resolved dataset.

## 3. Add a skill

Follow the bilingual [authoring checklist](skill-authoring.md):

1. Define one bounded task and select the existing category/stage or shared home.
2. Write `SKILL.md` and `SKILL_ZH.md`, including stable name/description, inputs/outputs, prerequisites, procedure, failures and validation.
3. Put reusable data/method knowledge in `methods/`, cross-stage principles in `methods/shared/`, and link the authoritative body. Put interface procedures in `references/`, reviewed code in `scripts/`, adaptable code in `templates/`, and public/synthetic examples in `examples/`.
4. Add optional host metadata only when needed.
5. Add a dataset declaration only for a real catalog need. Do not invent datasets or tools for display.
6. Update both category-navigation languages and applicable method mappings, without duplicating workflows.
7. Validate discovery, implemented invocation and failure behavior to the stated evidence level; check privacy before authorized sharing.

Only the canonical entry is discovered as a skill; a translation is not another registered capability. For independent distribution, include required resources or versioned public links: repository-relative links do not automatically travel with a copied folder.

## 4. Declare datasets

Use `skill_id`, `layer` and repository-relative `skill_path` in the owning acquisition declaration. Records need the service's `dataset_id`, `name`, `domain`, `description`, plus clear access mode, provenance, coverage and logical cache root.

Use `${AIRMOSAIC_LOCAL_WORKSPACE}`, never private mappings, actual cache manifests or credentials. Check listings, details, filters, uniqueness and references. Current loading does not enforce every dataset schema/duplicate-ID constraint automatically; do not claim otherwise.

The separate `catalog/datasets/` directory is also a detail-query fallback. Adding only a fallback record does not guarantee listing. Define the authoritative declaration for an ID and prevent drift.

## 5. Register executable metadata

One tool per file under `catalog/tools/`, using [tool.schema.json](../catalog/schemas/tool.schema.json). The [list-query declaration](../catalog/tools/airmosaic_list_tools.yaml) is a real example.

| Fields | Requirements |
|---|---|
| `schema_version`, `tool_id` | Supported version, currently 1; stable unique ID |
| `title`, `description`, `category`, `skill_id`, `owner_role` | Public purpose, category, actual skill and maintaining role |
| `implementation_status`, `registration_status` | Truthful implemented, template/reference and registration states |
| `entrypoint` | Existing relative path and supported kind; command module/subcommand where required |
| `input_schema`, `argument_bindings` | Matching declared fields and flags or positional bindings; no arbitrary shell |
| `default_arguments` | Optional reviewed defaults; structured queries use their declared output format |
| `output_schema` | Expected structured response or artifacts, not a claim that every raw script is a service |
| `requirements` | Dependencies, executables, non-secret settings, fixed resources and manual checks |
| `authentication`, `effects` | Logical authentication mode plus read/write/network effects, without secrets/profile paths |
| `documentation` | Existing classified usage document |
| `execution` | Required enablement, supported adapter and path roles matching reviewed policy |

The loader rejects unknown fields, duplicate keys/IDs, missing bindings, unsupported versions, unsafe paths and external schema references. A manifest alone cannot enable arbitrary execution: reviewed runner allowlists, resource/path/input/result checks and meaningful synthetic tests are also required. Templates and references remain disabled.

Task JSON contains parameters only, not a tool envelope. run-tool receives the tool ID separately and may allocate output fields before schema validation. Caller schema snapshots are documentation, not registration authority; keep them and examples consistent with the manifest. Manual plans must state unsupported execution rather than invent actions.

For a new tool, define the minimal real action, inspect its parser, declare effects/authentication, validate the catalog, inspect details/readiness, test normal and rejected inputs, update usage, then review privacy. Resource checks use fixed relative locations beneath explicitly configured roots. State readiness per environment; do not commit a member's current login or dependency state.

## 6. Host discovery and interfaces

Keep `skills/` as source. Read entries by path or install/link selected directories into a host-supported discovery location, checking conflicts without overwriting personal skills. This repository has no automatic installer; do not assume an arbitrary source folder is auto-discovered.

Verify names and invocation in the actual host. Optional interface metadata may specify display name, short description and default prompt; it does not create functions, authenticate accounts or launch services. Include resources when packaging and track versions.

Additional service adapters remain unimplemented. A future interface must implement actual listing/calling, input/result checks, error reporting and authorization before exposing a callable tool. Metadata and behavioral hints do not enforce permissions. Never expose reference documents or unadapted templates as executable functions.

## 7. Display and readiness

Use categories and actual manifest data to display purpose, entry type, implementation, current environment state and next steps. Clearly label templates, references and proposals.

Implementation, evidence and current readiness are separate dimensions. Use the loader's actual response values; do not invent status enums or equate registration with readiness. Source review, synthetic smoke checks, integration and scientific validation need separate dated evidence.

Details include invocation, schema, units, dependencies, authentication requirements, read/write/network scope, failure behavior and verification. Public displays use logical paths; full local paths stay in authorized local views. Current CLI/JSON/Markdown navigation does not imply that a visual tool panel, installer or external service adapter exists.
