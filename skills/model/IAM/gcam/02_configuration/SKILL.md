---
name: gcam-configuration
description: Read GCAM configuration and input-chain references to explain scenario components, SSP/RCP settings and CCS inputs. Authorized configuration edits require task copies and manual validation; no automated configuration tool exists.
---

# GCAM Configuration Reference

> Invocation status: `gcam_configuration_reference` is a catalogued reference, disabled in `run-tool`. Inspection and authorized edits are manual agent work on task copies; no configuration mutation API or simulation launcher exists.

## Local paths and authentication

Follow the [shared storage contract](../../../../../harness/storage-and-credentials.md) and [execution guide](../../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `output/<run_id>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

This layer provides reference documentation for GCAM configuration. It is not designed for automated model execution, but for helping agents understand:

- How configuration XML files define scenario components
- How SSP-RCP scenario combinations are set up
- How input CSV data flows through R processing scripts into model XML
- Common configuration manipulation operations and their risks
- CCS configuration specifics and common pitfalls
- Sector naming conventions and internal name mappings

## Prerequisites

Use an explicitly configured `GCAM_RELEASE_DIR` for authorized read-only source inspection. The model release stays outside Git and the data/config/auth roots; do not put its private absolute mapping into shared examples. No configuration file is automatically loaded from the personal settings root.

## Quick Tasks

- Understand configuration structure: read `references/configuration-files-overview.md`
- Understand SSP-RCP scenario setup: read `references/ssp-rcp-scenario-setup.md`
- Trace input data to output: read `references/input-data-chain-tracing.md`
- Modify a configuration safely: read `references/common-config-manipulation.md`
- Diagnose CCS configuration issues: read `references/ccs-configuration-in-depth.md`
- Look up sector names and mappings: read `references/sector-naming-conventions.md`

## Manual configuration boundary

`gcam_configuration_reference` is the real catalog ID. `describe-tool gcam_configuration_reference` shows its reference status; `run-tool` rejects execution. The JSON files in `examples/` are marked manual plans, not `--params-file` payloads or registered actions.

For explanation, inspect only the requested XML, component order and referenced files. For an authorized change, copy the required configuration/dependencies to a fresh local task directory, edit the copy, check XML parsing, order and reference resolution, then review a scoped diff. Do not modify shared model originals or launch a new simulation without task-specific authorization. Read-only configuration review, modification and model execution are separate operations.
