# AirMosaic AI — Agent Operating Guide

AirMosaic contains reusable atmospheric-environment skills, data declarations, scripts and local Python services. Start from the repository root. Read the relevant skill before using or changing its workflow.

## Required operating boundaries

- Documentation/method maintenance and routine checks use only relevant documentation, interface definitions and synthetic inputs. Do not read or copy original data without a separately scoped data task. Step 02 is methods-only: no concrete data, parameter values, implementation code, project script names or source fingerprints. Keep that boundary in methods, skills and workflow references.

- Work within the user's requested files, datasets, years, regions and operations. Continue necessary, authorized reversible work without repeated confirmation; ask only when essential information or authorization is missing.
- Preserve originals, existing results and other contributors' changes. Check the branch and working tree before editing. Do not launch additional model runs, bulk downloads, publication or external messages merely because a workflow mentions them.
- Never put private usernames, passwords, keys, tokens, cookies, browser profiles, private hostnames, signed links or machine-specific paths in shared code, documentation, examples, Issues, PRs or logs.
- Use repository-relative code paths and locally configured environment variables for data/model roots. Do not print whole environments, credential files or authenticated browser state. Report suspected secrets by location and category without repeating their values.
- Keep data/results under `AIRMOSAIC_LOCAL_WORKSPACE`, personal non-secret settings under `AIRMOSAIC_CONFIG_DIR`, and browser authentication state under `AIRMOSAIC_AUTH_DIR`. All roots must be separate and outside Git checkouts. Store passwords/tokens in a credential manager; do not create plaintext secret files. Read only task-needed configuration and use authorized tools without exporting authentication state.
- Keep model releases outside the repository. Use `output/<run_id>/<tool>/` for new results and share only a reviewed, sanitized summary. Preserve legacy output locations unless migration is authorized.
- Distinguish source inspection, local smoke checks, real-data integration and scientific validation. Do not report skipped tests or planned capabilities as implemented capabilities.
- Follow [agent boundaries](harness/agent-boundaries.md) for scope, privacy, general-purpose scripts and sharing. These rules are operating instructions; they are not evidence that runtime enforcement exists.

## Documentation map

Start with the [four-step guide](harness/four-step-workflow.md) and [skill navigation](skills/README.md). methods/index.yaml maps every method to actual skills and stages; it is not an execution registry.

| Task | Guide |
|---|---|
| Understand collaboration and execution | [Harness overview](harness/README.md) |
| Find commands, scripts and templates | [Tool catalog](harness/tool-catalog.md), [registry queries](harness/usage/tool-registry.md) |
| Run reviewed CLI/Python/R adapters | [run-tool](harness/usage/run-tool.md) |
| Configure separate data/settings/authentication roots | [Storage and credentials](harness/storage-and-credentials.md) |
| Install core services; inspect datasets/cache | [Core tools](harness/usage/core.md) |
| Acquire or process source data | [Data acquisition](harness/usage/data-acquisition.md) |
| Inspect GCAM outputs or adapt health templates | [Model analysis](harness/usage/model-analysis.md) |
| Use mlr3 / TimeXer guidance and track reference projects | [Machine learning](harness/usage/machine-learning.md) |
| Reuse categorized local methods without treating source files as registered tools | [Methods library](methods/README.md) |
| Register a capability or configure host discovery | [Registration and display](harness/tool-registration.md) |

Read only guides and references relevant to the task. Detailed harness guides are currently in Chinese; the root README has English and Chinese versions.

## Environment and existing entry points

Use Python 3.10+ in a project virtual environment and install with `python -m pip install -e '.[dev]'`. Configure `AIRMOSAIC_LOCAL_WORKSPACE` locally to a directory outside the repository. `.env` is not automatically loaded. Cache checks require this variable or an explicit SDK workspace argument. The [environment example](config/examples/README.md) configures session path variables explicitly; CONFIG_DIR/AUTH_DIR are caller conventions, not core loaders.

Core commands, with the same interpreter used for installation:

```sh
python -m airmosaic_core.cli --help
python -m airmosaic_core.cli list-tools --format json
python -m airmosaic_core.cli describe-tool worldpop_download
python -m airmosaic_core.cli check-tool ihme_gbd_fetch_results
python -m airmosaic_core.cli list-datasets
python -m airmosaic_core.cli describe-dataset worldpop_population_grid
python -m airmosaic_core.cli search-datasets "population grid"
python -m airmosaic_core.cli check-availability worldpop_population_grid --pattern 'raw/**/*.tif'
python -m airmosaic_core.cli draft-causal-plan --question 'Did the policy change exposure?' --treatment 'target policy' --outcome 'exposure'
```

- `list-datasets` reads acquisition `datasets.yaml` declarations. It is not a catalog of every executable tool or of downloaded files.
- `check-availability` searches for files only. It does not validate contents, years, checksums or scientific suitability. Its local output may contain absolute paths; sanitize before sharing.
- `draft-causal-plan` returns a local template. It does not invoke an LLM, generate an actual DAG or establish a causal effect.
- SDK entry points are the `DataCatalogService`, `DataAccessService`, `CausalDesignService`, `ToolRegistryService` and `ToolRunnerService` classes in `airmosaic_core.services`.

## Skill and tool discovery

Skill sources live under `skills/`. Read their `SKILL.md` files explicitly when working in this repository. Standard host discovery requires installation or a supported location; `agents/openai.yaml` supplies optional host metadata, not executable tool registration.

Acquisition skill IDs include `worldpop`, `csmar`, `ind_yearbook` and `ihme-gbd-results`. Some differ from skill frontmatter names; use the [mapping](harness/tool-registration.md) when filtering datasets or selecting skills.

`ToolRegistryService` now validates `catalog/tools/*.yaml` and supports `list-tools`, `describe-tool` and `check-tool`. These read-only queries check static prerequisites; they never execute tools, load personal config or inspect credentials. Authentication/R libraries may remain unverified. Templates and references are catalogued as non-callable.

`run-tool` supports the reviewed core CLI, six Python scripts and two GCAM R scripts with schema/path checks, dry-run and sanitized receipts. Read its [guide](harness/usage/run-tool.md) first: all three existing roots are required, output parameters default to a fresh task directory, network requires an explicit flag, and GBD requires session attestation. Never put credentials into parameters. Child processes receive a minimal environment; receipts omit raw values and logs. This is a preflight layer for trusted code, not an OS sandbox. Templates/references and nested run-tool remain unsupported. R uses native Rscript with --vanilla and isolated namespace checks; dry-run leaves R packages unverified. MCP, REST and cross-layer workflow orchestration are not implemented. Raw scripts do not gain these checks automatically.

## Execution and scientific boundaries

1. Determine scope and choose an implemented entry point.
2. Check dependencies, authentication, inputs, parameters and output destinations.
3. Verify units, years, spatial alignment, missing-value semantics and method assumptions before chaining modules.
4. Execute within existing authorization, record outcomes, and verify required artifacts and domain checks.
5. Deliver results with their validation scope and unresolved limitations; sanitize shared material.

Select methods using evidence, data suitability, baselines and domain review. Workflow thresholds and AI/empirical branches are design proposals, not automatic execution rules or proof of causal identification. Do not silently change scientific scope to make a run pass.

## Contribution checks

- Keep tool arguments, examples, skill metadata and catalog entries consistent with actual code.
- Update classified guides and the catalog when interfaces change; update both root README variants when shared entry instructions change.
- Use synthetic inputs in temporary directories for ordinary tests. Keep real-data validation receipts local and sanitize shared summaries.
- Run relevant checks; core tests use `python -m pytest -q -p no:cacheprovider`. They do not validate every connector or scientific model.
- Review diff, filenames, logs and attachments for private information before authorized sharing. Inspect only locations/categories of suspected secrets, never their values. Do not bundle auth/config directories into data archives or copy browser profiles between members.
- Commit and push when the current task explicitly authorizes them, after relevant validation and privacy review. Do not force-push, rewrite history or include unrelated repositories. A role name or a roadmap does not grant additional authority.
