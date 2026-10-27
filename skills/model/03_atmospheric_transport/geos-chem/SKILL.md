---
name: geos-chem-workflow
description: Guide version-specific GEOS-Chem Classic and GCHP setup, compilation triage, runtime configuration and concentration handoff. Reference only; no compilation, download, scheduler or simulation adapter.
---

# GEOS-Chem usage and troubleshooting reference

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Stage:** 03, atmospheric transport and chemistry. **Status:** reference only, without a registered tool ID. run-tool cannot compile or simulate the model. This skill does not install dependencies, log in, download/read data or launch/modify jobs.

## Workflow

1. Specify Classic/GCHP, pinned source version, simulation type, grid and comparison scenarios; use matching official documentation.
2. Read [input preparation](../../../data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md) and define meteorology, initial/boundary conditions, species and time contracts. Emissions remain interface methods without concrete data or implementation.
3. Use the [usage guide](references/usage.md) to review toolchains, source/build/run directories and configuration. Consult [build/run troubleshooting](references/build-troubleshooting.md), retaining error categories and versions instead of arbitrarily changing scientific code.
4. A separately authorized model task should begin with a short validation, checking process state, time coverage, diagnostics, restart and scientific scope independently. Documentation maintenance does not execute these steps.
5. Hand concentrations to stage 04 with units, grid, vertical/surface definition, averaging period, common valid support and observation-validation limits.

## Paths and evidence

Keep source and releases outside Git. Explicitly configure task build/run directories in personal non-secret settings; write results to a fresh workspace task directory. `GC_SOURCE_DIR` and `GC_RUN_DIR` are documentation variables, not automatically loaded AirMosaic settings. Raw logs may expose paths and filenames; do not publish them. Unadapted workflows do not inherit run-tool isolation or sanitized receipts.

This guide distills local technical notes cross-checked against official documents. See [sources and version differences](SOURCES.md). Historical machine-specific patches are not universal fixes; forward, GCHP and version-specific adjoint capabilities are not interchangeable.

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
