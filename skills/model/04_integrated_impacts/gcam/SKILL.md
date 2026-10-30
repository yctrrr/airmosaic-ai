---
name: gcam
description: Inspect and analyze existing GCAM outputs through reviewed tools, or consult manual configuration, build and run guidance. No simulation launcher.
compatibility: "Python >=3.10; Java; Rscript; optional C++ toolchain"
metadata:
  version: "1.0.0"
  reviewed: "2026-10-30"
---

# GCAM preparation and output analysis

**English** | [中文](SKILL_ZH.md)

Choose the task before reading detailed references:

| Task | Entry |
|---|---|
| Prepare a release, compile source, generate input XML or run a model manually | [Build and run](references/build-and-run.md) |
| Inspect the fixed database structure and units | [Output structure](01_output_structure/SKILL.md) |
| Explain or adapt configuration in a task copy | [Configuration](02_configuration/SKILL.md) |
| Extract, aggregate or plot existing results | [Extraction](03_data_extraction/SKILL.md) |
| Diagnose compilation/linking/runtime errors | [Build troubleshooting](references/build-troubleshooting.md) |

Only output inspection, extraction, aggregation and plotting have reviewed `run-tool` adapters. Configuration, compilation and simulation remain manual tasks. The build/run guide requires a selected model version, compatible dependencies, a reviewed task copy and separate process/solver checks; it does not add an execution adapter. Read [GCAM methods](../../../../methods/04_integrated_impacts/gcam.md) for scenario design, build/run choices, units and interpretation.

From the repository root, inspect the selected interface with `python -m runtime.cli describe-tool <tool_id>`. Configure existing external storage roots and `GCAM_RELEASE_DIR` explicitly; no personal configuration is automatically loaded. The [operations reference](references/operations.md) covers prerequisites, parameter files, calls and output checks. Keep releases and databases outside Git; see [data boundaries](data_boundary.md).

For differences between GCAM-China and GCAM-Core read [model variants](references/gcam-china-vs-official.md); for a requested source-chain question read [input architecture](references/input-data-architecture.md). Historical references retain their existing language. Do not interpret a completed extraction as a validated simulation or accepted cost estimate.
