---
name: gcam-configuration
description: Explain GCAM configuration chains or review authorized task-copy edits. Configuration is a manual reference, without a mutation or simulation adapter.
---

# Review GCAM configuration

**English** | [中文](SKILL_ZH.md)

`gcam_configuration_reference` is catalogued and disabled in `run-tool`. Inspect its status with:

```sh
python -m runtime.cli describe-tool gcam_configuration_reference
```

Use an explicitly selected external `GCAM_RELEASE_DIR`. For explanation, inspect only requested XML and its references. For an authorized edit, copy required configuration/dependencies into a fresh task directory, change the copy, parse XML, verify component ordering and reference resolution, and return a scoped diff. Compilation and simulation require their own task scope. The JSON files in `examples/` describe manual plans; they are not runner payloads.

Read the relevant reference: [configuration structure](references/configuration-files-overview.md), [SSP/RCP setup](references/ssp-rcp-scenario-setup.md), [input chain](references/input-data-chain-tracing.md), [edit patterns](references/common-config-manipulation.md), [CCS](references/ccs-configuration-in-depth.md), [sector names](references/sector-naming-conventions.md). For compilation/linking problems use [build troubleshooting](../references/build-troubleshooting.md). Scenario interpretation belongs in the [method](../../../../../methods/04_integrated_impacts/gcam.md).
