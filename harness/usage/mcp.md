# Local MCP connection and use

<!-- README-I18N:START -->

**English** | [中文](mcp_ZH.md)

<!-- README-I18N:END -->

The local stdio server uses the existing catalog and execution services. It exposes 16 enabled tool IDs, six as public metadata queries and ten through the runner. The full catalog still has 25 entries, including non-executable references. No second tool registry, HTTP service, automatic login, workflow engine or scientific validator is introduced.

## 1. Install and check the connection

From the repository root, using the selected project interpreter:

```sh
python -m pip install -e '.[dev,mcp]'
python -m airmosaic.mcp_server --help
python harness/checks/mcp_smoke.py
```

The optional extra pins the official Python SDK to `mcp==2.3.0`. The smoke client starts a real stdio subprocess, lists tools/resources and queries public dataset metadata. It does not require personal roots or access data, credentials, network services or authenticated browsers. Expected counts for this version are 16 tools, 49 resources and nine datasets.

The MCP server is started by a compatible client using the command below. It waits for protocol messages; it does not accept natural-language text directly in a terminal.

```sh
python -I -B -X utf8 -m airmosaic.mcp_server
```

The installed console entry is `airmosaic-mcp`. Keep stdout exclusively for the protocol. The application reports fixed startup error categories on stderr and suppresses raw SDK diagnostic logs. It does not connect itself to a client or modify client settings.

## 2. Configure a compatible client

Use [mcp-client.example.json](../../config/examples/mcp-client.example.json) as a generic starting point, adapting field names to the client's supported configuration. Replace placeholders in a personal copy with the chosen interpreter and three existing, separate roots outside Git. Hosts differ in environment-variable expansion; the example does not expand itself. Do not put tokens, cookies or passwords in the JSON, and do not copy the personal file back to Git.

Public metadata queries work without roots. Preview and execution through the runner require all three roots, even when no login is needed. Pass only approved non-secret settings to the MCP process. Existing-session tools use an explicitly attested local browser port; the server neither logs in nor reads browser-state files. Current server grants do not verify login or scientific scope; the client/user must still select a bounded authorized task.

## 3. Discover and read

MCP `tools/list` returns the 16 supported interfaces with schemas derived from the existing manifests. Query operations use their existing flat parameter object:

```json
{"category":"data_acquisition"}
```

Pass that object to `airmosaic_list_tools`. Its result includes all matching catalog entries and their actual implementation/availability states. Other metadata operations are `airmosaic_describe_tool`, `airmosaic_check_tool`, `airmosaic_list_datasets`, `airmosaic_describe_dataset` and `airmosaic_search_datasets`. Format defaults are supplied by the interface; output is structured JSON.

MCP resources include `airmosaic://catalog/tools`, `airmosaic://catalog/datasets` and `airmosaic://catalog/skills`. The skill index links the English and Chinese resources for 23 canonical skills. These are reading resources, not executable tools or automatically installed skills. Skill discovery follows public method mappings and tool-associated entries; unreferenced new skills require an explicit public mapping. Resource reads accept only exact indexed URIs, with bounded public document size. There is no arbitrary file, original-data, configuration, authentication or run-log resource reader.

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
python -m airmosaic.mcp_server --execute-tool gcam_aggregate_provinces
```

An authorized call can then request execution:

```json
{"parameters":{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/01_socioeconomic_natural_change/ExampleDataset/v1/rows.csv"},"dry_run":false,"project_id":"example_project","stage":"01_socioeconomic_natural_change"}
```

Use only task-authorized inputs; the path is illustrative. Output is allocated under the existing fresh task subtree. The original aggregation implementation is used unchanged. This does not compile or simulate a model.

Network grants are separate, limited to selected execution tools:

```sh
python -m airmosaic.mcp_server --execute-tool worldpop_download --network-tool worldpop_download
```

This command authorizes future requests; starting the server does not download anything. Actual requests still require task scope, valid parameters, dependencies and checks. Without a network grant the runner returns a blocker.

For an existing browser session, operator attestation must also bind its selected local CDP port:

```sh
python -m airmosaic.mcp_server --execute-tool ihme_gbd_fetch_results --network-tool ihme_gbd_fetch_results --browser-tool ihme_gbd_fetch_results --browser-port 9222
```

The port is an example, not a detected session. The user verifies the intended session and current query dimensions first. The port cannot be changed through MCP call parameters; authentication remains unverified in receipts. Do not expose a browser debug port publicly or copy session material.

`--max-timeout` defaults to 300 seconds and accepts 1–3600; per-call timeout cannot exceed the startup limit. An optional fresh `run_id` uses the existing 32-character lowercase hexadecimal contract. The runner rejects reused IDs; it does not replay or automatically retry tasks.

## 6. Cancellation, privacy and evidence

Calls are serialized. Cancellation or normal connection shutdown signals the worker, reuses owned-process-tree cleanup and records a cancelled execution when a task has started. Cleanup waiting is bounded, and a slot remains occupied until its worker finishes. Cancellation cannot undo a completed external request. Check local receipts and partial artifacts before considering another request; do not configure blind retries of non-idempotent operations.

The runner's parameter/path checks, minimal child environment and sanitized receipts remain in force. Metadata responses are public repository information. Calculation responses contain runner receipts and allowed summaries, not raw stdout/stderr, personal input names or scientific files. The server does not read secrets or supply a general credential broker. These are trusted-code operating checks, not an OS sandbox or firewall; remote/untrusted code requires separate isolation.

Validation uses synthetic inputs: official SDK in-process and real stdio clients, protocol error redaction, startup grants, path rejection, public resources, existing aggregation arithmetic and cancellation cleanup. Actual third-party client configuration, authenticated downloads, remote deployment and scientific acceptance are separate checks. SDK protocol/runtime references: [official SDK](https://github.com/modelcontextprotocol/python-sdk), [low-level server](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/).

Calculation calls supply top-level `project_id` and `stage` following the [asset contract](../assets.md); these fields do not belong in `parameters`. Metadata queries need no project context.
