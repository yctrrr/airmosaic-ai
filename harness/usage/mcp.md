# Local MCP connection and use

<!-- README-I18N:START -->

**English** | [中文](mcp_ZH.md)

<!-- README-I18N:END -->

The local stdio server uses the existing catalog and execution services. It exposes enabled tool IDs from the validated tool catalog, including public metadata queries and reviewed runner adapters. Disabled references remain visible as catalog metadata. No second tool registry, HTTP service, automatic login, general workflow engine or scientific validator is introduced.

## 1. Install and check the connection

From the repository root, using the selected project interpreter:

```sh
python -m pip install -e '.[dev,mcp]'
python -m runtime.mcp_server --help
python harness/checks/mcp_smoke.py
```

The optional extra pins the official Python SDK to `mcp==2.3.0`. The smoke client starts a real stdio subprocess, lists tools/resources and queries public dataset metadata. It does not require personal roots or access data, credentials, network services or authenticated browsers. Counts follow the current authoritative catalogs; adding a method or skill resource does not add an execution tool.

The MCP server is started by a compatible client using the command below. It waits for protocol messages; it does not accept natural-language text directly in a terminal.

```sh
python -I -B -X utf8 -m runtime.mcp_server
```

The installed console entry is `airmosaic-mcp`. Keep stdout exclusively for the protocol. The application reports fixed startup error categories on stderr and suppresses raw SDK diagnostic logs. It does not connect itself to a client or modify client settings.

## 2. Configure a compatible client

Use [mcp-client.example.json](../../config/examples/mcp-client.example.json) as a generic starting point, adapting field names to the client's supported configuration. Replace placeholders in a personal copy with the chosen interpreter and three existing, separate roots outside Git. Hosts differ in environment-variable expansion; the example does not expand itself. Do not put tokens, cookies or passwords in the JSON, and do not copy the personal file back to Git.

Public metadata queries work without roots. Preview and execution through the runner require all three roots, even when no login is needed. Pass only approved non-secret settings to the MCP process. Existing-session tools use an explicitly attested local browser port; the server neither logs in nor reads browser-state files. Current server grants do not verify login or scientific scope; the client/user must still select a bounded authorized task.

## 3. Discover and read

MCP `tools/list` returns the enabled interfaces with schemas derived from the existing manifests. Query operations use their existing flat parameter object:

```json
{"category":"data_acquisition"}
```

Pass that object to `airmosaic_list_tools`. Its result includes all matching catalog entries and their actual implementation/availability states. Other metadata operations are `airmosaic_describe_tool`, `airmosaic_check_tool`, `airmosaic_list_datasets`, `airmosaic_describe_dataset` and `airmosaic_search_datasets`. Format defaults are supplied by the interface; output is structured JSON.

MCP resources include `airmosaic://catalog/tools`, `airmosaic://catalog/datasets`, `airmosaic://catalog/skills`, `airmosaic://catalog/methods` and the unified `airmosaic://catalog/capabilities`. Read the unified resource for method-to-skill mappings, actual tool IDs, implementation/registration declarations, versions, document SHA256 fingerprints and exact document resource URIs. Method and skill documents remain reading resources; they do not install a host skill or register execution.

An explicitly indexed Chinese method sibling is also available at `airmosaic://methods/<method_id>/zh`; the canonical document uses `/en`. Other supporting documents use the exact resource addresses returned by discovery.

For skills, `supporting_documents` exposes the Markdown guides explicitly linked from either language's entry and located inside that skill directory. It is a bounded one-hop index, not recursive filesystem discovery; unlinked files, scripts, credential directories and external paths are not exposed as document resources.

This is one derived snapshot, built at server startup from `methods/index.yaml`, `catalog/skills.yaml`, canonical skill frontmatter and existing tool manifests. Restart after metadata edits; CLI invocations build a fresh snapshot. Unreferenced new skills need a method mapping or a public reference in `catalog/skills.yaml`. No recursive filesystem discovery or script import occurs. `documented_scripts` lists finite script references found in the skill document and exact matching enabled tool IDs; file presence and a tool elsewhere in the skill do not establish that every branch is executable.

`declarations` reports structured fields as `declared` or `not_declared`; `document_sections` and exact resource URIs let a reader inspect prose that has no structured field. `evidence_claim` preserves existing method evidence as a declaration. None of these establish `source_checked`, `synthetic_verified`, `real_integration` or `scientific_review`. Execution readiness is `not_checked`, and scientific acceptance is `not_assessed`; use the existing tool check/runner for an individual tool's current prerequisites and authorization.

Maintenance queries use the same service:

```sh
python -m runtime.cli list-capabilities --kind method
python -m runtime.cli list-capabilities --kind skill
python -m runtime.cli describe-capability skill machine-learning-model
python -m runtime.cli validate-capabilities
```

Validation means metadata consistency only. It rejects duplicate method/skill IDs or YAML keys, unknown mapped tools, missing documents, unsafe relative paths, links/reparse locations, nested repositories and oversized documents. Resource reads accept only exact indexed URIs and recheck the path and size. There is no arbitrary file, original-data, configuration, authentication or run-log reader.

## 4. Preview a runner-backed operation

Runner-backed tools use a transport envelope around the existing flat parameters:

```json
{"parameters":{"project":"wpgp","year":2020},"dry_run":true,"project_id":"example_project","stage":"01_socioeconomic_natural_change"}
```

Use this object with `worldpop_download`. `dry_run` defaults to true. Output paths and browser ports are managed by the server/runner and are omitted from the MCP parameter schema. Input paths retain the runner's existing checks. `params_file`, arbitrary commands and per-call permission flags are not accepted.

Responses contain `tool_id`, `mode` and `result`; errors use fixed categories. A preview can have `isError=false` while `result.can_execute=false`: inspect `blockers`. Preview does not create directories/receipts, execute a process, verify a login or perform a download. Process success keeps `scientific_validation=not_run` unless a separate future validator establishes otherwise.

## 5. Authorize actual execution at startup

The operator grants individual runner-backed tools when starting the server; the model cannot add those grants through tool arguments. Read-only metadata queries need no execution grant.

```sh
python -m runtime.mcp_server --execute-tool gcam_aggregate_provinces
```

An authorized call can then request execution:

```json
{"parameters":{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/01_socioeconomic_natural_change/ExampleDataset/v1/rows.csv"},"dry_run":false,"project_id":"example_project","stage":"01_socioeconomic_natural_change"}
```

Use only task-authorized inputs; the path is illustrative. Output is allocated under the existing fresh task subtree. The original aggregation implementation is used unchanged. This does not compile or simulate a model.

Network grants are separate, limited to selected execution tools:

```sh
python -m runtime.mcp_server --execute-tool worldpop_download --network-tool worldpop_download
```

This command authorizes future requests; starting the server does not download anything. Actual requests still require task scope, valid parameters, dependencies and checks. Without a network grant the runner returns a blocker.

For an existing browser session, operator attestation must also bind its selected local CDP port:

```sh
python -m runtime.mcp_server --execute-tool ihme_gbd_fetch_results --network-tool ihme_gbd_fetch_results --browser-tool ihme_gbd_fetch_results --browser-port 9222
```

The port is an example, not a detected session. The user verifies the intended session and current query dimensions first. The port cannot be changed through MCP call parameters; authentication remains unverified in receipts. Do not expose a browser debug port publicly or copy session material.

`--max-timeout` defaults to 300 seconds and accepts 1–3600; per-call timeout cannot exceed the startup limit. An optional fresh `run_id` uses the existing 32-character lowercase hexadecimal contract. The runner rejects reused IDs; it does not replay or automatically retry tasks.

## 6. Cancellation, privacy and evidence

Calls are serialized. Cancellation or normal connection shutdown signals the worker, reuses owned-process-tree cleanup and records a cancelled execution when a task has started. Cleanup waiting is bounded, and a slot remains occupied until its worker finishes. Cancellation cannot undo a completed external request. Check local receipts and partial artifacts before considering another request; do not configure blind retries of non-idempotent operations.

The runner's parameter/path checks, minimal child environment and sanitized receipts remain in force. Metadata responses are public repository information. Calculation responses contain runner receipts and allowed summaries, not raw stdout/stderr, personal input names or scientific files. The server does not read secrets or supply a general credential broker. These are trusted-code operating checks, not an OS sandbox or firewall; remote/untrusted code requires separate isolation.

Validation uses synthetic inputs: official SDK in-process and real stdio clients, protocol error redaction, startup grants, path rejection, public resources, existing aggregation arithmetic and cancellation cleanup. Actual third-party client configuration, authenticated downloads, remote deployment and scientific acceptance are separate checks. SDK protocol/runtime references: [official SDK](https://github.com/modelcontextprotocol/python-sdk), [low-level server](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/).

Calculation context fields belong at the top level, outside `parameters`. Legacy adapters require `project_id` and `stage`. Regression interfaces expose optional project/stage context and `result_scope: auto|skill|workflow|project`; each selected adapter still validates its supported scope and input restrictions. The reviewed workflow scope is for declared synthetic checks, not arbitrary project data. Auto selects project scope when a project ID is supplied and otherwise skill scope. Metadata queries need no context.

## Configured workflow entry

`ml_regression_workflow` exposes the reusable regression skill through the existing runner; see the [skill](../../skills/model/shared/machine_learning_model/SKILL.md). For a separate package library, set `AIRMOSAIC_R_LIBRARY` explicitly in the client's personal `env`. Tool arguments cannot change the dependency library; keep its actual location out of public examples. Add `--execute-tool ml_regression_workflow` at server startup for execution. No network grant is required. An example preview request:

```json
{"parameters":{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/AQbench_dataset.csv","task_config":"config/examples/ml-regression/aq-bench-prediction.json"},"project_id":"aq_bench_demo","stage":"03_atmospheric_transport","dry_run":true}
```

After preview, use the same parameters with `dry_run: false`. Omit project/stage for a generic run in the skill’s ignored local results; provide a project ID for external project results. MCP manages output directories and does not expose `out_dir` overrides. For custom project directories and `output_files`, use the CLI and reviewed task settings. Neither route imposes a stage/tool hierarchy for this adapter.

## Maintenance resources and language-specific execution

`catalog/skills.yaml` adds finite public operational references to the read-only skill resource index. Canonical metadata stays in each SKILL entry; these references do not register tools or install host skills. Maintenance drafts outside the repository are not discovered. The tool catalog and reviewed adapter allowlist remain the sole execution sources.

The machine-learning skill exposes R `ml_regression_workflow` and Python `ml_python_regression_workflow` with separate task/dependency contracts. Both use the shared result-scope rules and require their own startup execution grant. Python new-study execution additionally requires the explicit plan bundle; engineering replay accepts only manifest-listed repository synthetic input.
