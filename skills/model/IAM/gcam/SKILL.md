---
name: gcam
description: Navigate GCAM existing-output inspection, configuration references, and registered result-extraction and aggregation tools. Use for analyzing existing scenario databases; this skill does not launch GCAM simulations.
---

# GCAM Model Analysis

> Invocation status: Use `gcam_extract_market_sector`, `gcam_extract_technology_components` and `gcam_aggregate_provinces` through `run-tool`. `gcam_inspect_output_structure` and `gcam_plot_sector_change` also use `run-tool`; configuration is a reference workflow. No GCAM simulation launcher is registered.

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md) and [execution guide](../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `output/<run_id>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Layer Navigation

GCAM 是跨阶段共享能力，见[四步导航](../../../../harness/four-step-workflow.md)。源码编译、链接依赖与运行错误的区分见[构建排错](references/build-troubleshooting.md)。该说明不启动编译或模拟，不扩大现有输出分析工具的权限。

Choose the right layer based on the task:

| Task | Layer |
|------|-------|
| List scenarios, regions, sectors, subsectors, technologies | [01_output_structure](01_output_structure/SKILL.md) |
| Check price/quantity unit compatibility | [01_output_structure](01_output_structure/SKILL.md) |
| Map province codes to province names | [01_output_structure](01_output_structure/SKILL.md) |
| Understand configuration XML and scenario components | [02_configuration](02_configuration/SKILL.md) |
| Trace how input CSV becomes BaseX output | [02_configuration](02_configuration/SKILL.md) |
| Add or remove a scenario component safely | [02_configuration](02_configuration/SKILL.md) |
| Diagnose CCS configuration issues | [02_configuration](02_configuration/SKILL.md) |
| Look up sector naming conventions | [02_configuration](02_configuration/SKILL.md) |
| Extract market/sector price and quantity rows | [03_data_extraction](03_data_extraction/SKILL.md) |
| Decompose sector cost into technology components | [03_data_extraction](03_data_extraction/SKILL.md) |
| Aggregate province rows to national weighted values | [03_data_extraction](03_data_extraction/SKILL.md) |
| Plot sector price/quantity change over time | [03_data_extraction](03_data_extraction/SKILL.md) |
| Interpret price units and sector-specific quirks | [03_data_extraction](03_data_extraction/SKILL.md) |

## Execution routing and prerequisites

| Tool ID | Invocation | Scope |
|---|---|---|
| `gcam_extract_market_sector` | `run-tool` | Existing market/sector rows |
| `gcam_extract_technology_components` | `run-tool` | Existing technology-component rows |
| `gcam_aggregate_provinces` | `run-tool` | Existing market/sector CSV |
| `gcam_inspect_output_structure` | `run-tool` (R) | Fixed inspection queries and database layout |
| `gcam_plot_sector_change` | `run-tool` (R) | Fixed comparison years and explicit output mapping |
| `gcam_configuration_reference` | Reference only, runner disabled | Manual inspection/authorized task-copy edits |

Use `describe-tool <tool_id>` to inspect each record, then follow the linked sub-skill and [model guide](../../../../harness/usage/model-analysis.md). Enabled adapters use the configured project Python; extraction needs pandas, local Java, a compatible BaseX JAR and selected scenario databases. `GCAM_RELEASE_DIR` must be explicitly configured outside Git and the data/config/auth roots; it is not bundled or auto-discovered. Aggregation only needs pandas and its input CSV.

The runner supplies output paths and injects `UNIT_PRICE_OUT_DIR` for plotting; caller values of that variable are ignored. R runs with --vanilla and isolated package checks; dry-run leaves package loading unverified. An authorized configuration change requires a task copy and separate checks; it never authorizes simulation execution. No automatic workflow stitching, GCAM simulation launcher or scientific acceptance service is implemented.

## Data Boundary

This skill stores reusable methods only. Do not copy GCAM model releases, BaseX databases, scenario outputs, or raw data into the skill directory. See `data_boundary.md`.

The skill does not store credentials, tokens, cookies, browser profiles, personal paths, or private download links.

## Cross-Cutting References

- `references/gcam-china-vs-official.md`: differences between GCAM-China and official GCAM-Core
- `references/input-data-architecture.md`: full pipeline from raw CSV to BaseX output
- `references/privacy-redaction-rules.md`: checklist for keeping derived methods clean
- `data_boundary.md`: what belongs in and out of the skill
