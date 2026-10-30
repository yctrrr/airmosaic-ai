---
name: health-impact-analysis
description: Adapt and review PM2.5 mortality calculation and map templates against aligned exposure, population, baseline rates and RR curves. No executable health adapter.
---

# Prepare PM2.5 health-impact analysis

**English** | [中文](SKILL_ZH.md)

`pm25_hia_calculate_template` and `pm25_hia_visualize_template` are catalogued R templates, disabled in `run-tool`. They need task-copy adaptation and scientific review before execution; no one-command health service exists.

1. Define endpoints, age/sex populations, exposure period, baseline year and risk-function version using the [health method](../../../../methods/04_integrated_impacts/health_impacts.md).
2. Use [input schemas](references/data_requirements.md) and [template operations](references/operations.md) to map authorized prepared inputs, explicit environment settings and new external project outputs.
3. Adapt reader functions, population denominators, mortality-year selection, age harmonization and RR lookup behavior in a task copy. Sourcing a template executes its body; do not source it for discovery.
4. Before real computation, validate simple cases and complete joins. Check units, common population support and scenario pairing; then review grid totals, summaries and maps independently.

[Operations](references/operations.md) provides actual template locations and conditional R invocation. The existing workflow example contains relative source paths that require adaptation. Template presence or successful exit does not validate epidemiology or authorize data acquisition. Historical references retain their existing language.

Choose and integrity-check an external ER version using [source records and the coefficient contract](references/exposure_response.md). Actual GEMM source cells and historical/current WHO log-linear coefficients are available separately; they are not interchangeable or directly accepted by the old RR lookup template. This PM2.5 skill cannot consume AQ-Bench O3 predictions.
