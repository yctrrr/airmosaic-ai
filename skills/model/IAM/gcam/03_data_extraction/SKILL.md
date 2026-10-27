---
name: gcam-data-extraction
description: Extract existing GCAM market/sector and technology-component rows, then aggregate province rows with registered run-tool adapters. Plot existing sector rows for 2021/2035 with the registered R adapter; additional query types need domain adaptation.
---

# GCAM Data Extraction

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


> Invocation status: `gcam_extract_market_sector`, `gcam_extract_technology_components` and `gcam_aggregate_provinces` are enabled in `run-tool`. `gcam_plot_sector_change` is also enabled through its R adapter.

## Local paths and authentication

Follow the [shared storage contract](../../../../../harness/storage-and-credentials.md) and [execution guide](../../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_ASSETS_DIR` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `results/<project_id>/<run_id>/<stage>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

Extract rows from existing GCAM BaseX databases with two Python tools and aggregate an existing CSV with a third. Only the extractors take scenario/region/sector/year filters; aggregation takes `input_csv`. Additional emissions/energy query families, unit-price selection rules and scientific interpretation require explicit domain adaptation, not an assumed generic action interface.

## Prerequisites

Explicitly configure `GCAM_RELEASE_DIR` outside Git and the data/config/auth roots. Extraction needs pandas, local Java, a compatible `libs/jars/BaseX-*.jar`, and `${GCAM_RELEASE_DIR}/output/<scenario>/database_basexdb/`. Model resources are logically read inputs; the runner is not an OS read-only sandbox. Aggregation needs pandas and an existing CSV in workspace `data/` or `results/`.

For extraction, supply `scenarios` and `sectors` as comma-separated strings. Explicitly scope `regions` and `years` too: raw defaults can include China, many provinces and multiple years. The runner allocates `out_dir`; all script/runner parameter names come from the manifest, not an invented JSON action.

## Registered tool IDs and outputs

| Tool ID | Caller parameters | Files below results/<project_id>/<run_id>/<stage>/<tool_id>/ |
|---|---|---|
| `gcam_extract_market_sector` | `scenarios`, `sectors`; scope with `regions`, `years` | `market_sector_rows.csv`, `market_sector_summary.csv` |
| `gcam_extract_technology_components` | Same extraction filters | `technology_component_rows.csv`, `technology_component_summary.csv` |
| `gcam_aggregate_provinces` | `input_csv` | `province_aggregate.csv` |
| `gcam_plot_sector_change` | `input_csv`; optional `sectors`, `scenarios` | `sector_change_2021_2035.png`, `sector_change_weighted_mean.csv` |

Lists are comma-separated strings, not arrays. Years are four-digit values; scenario names must be safe identifiers. `out_dir` is optional to callers because the runner supplies it. The technology tool has no `method` parameter. Aggregation excludes China/Global rows and reports `weighted_price`, `quantity_sum`, `province_count` grouped by scenario/source/sector/year; it does not automatically validate unit compatibility or complete national coverage.

`gcam_plot_sector_change` requires an explicit input_csv under workspace data/results, without commas in its path. The runner maps out_dir to the child UNIT_PRICE_OUT_DIR; caller settings are ignored. Rscript --vanilla loads dplyr, ggplot2, readr and tidyr from the selected R installation standard library. dry-run leaves package loading unverified; execution checks namespaces and both expected artifacts. Years remain fixed at 2021/2035. See the [model guide](../../../../../harness/usage/model-analysis.md) for defaults and manual adaptations.

## Parameter examples and task handoff

The public [market example](../../../../../config/examples/run-tool/gcam-market.json) and [technology example](../../../../../config/examples/run-tool/gcam-technology.json) contain:

```json
{"scenarios":"example_scenario","regions":"AH,BJ","sectors":"cement","years":"2021,2035"}
```

`example_scenario` must be replaced with an existing scenario. AH/BJ illustrate a two-province subset, not a national sample. Use a reviewed task JSON under CONFIG_DIR for real scope; select and verify complete province coverage before reporting national aggregates.

```powershell
python -m airmosaic.cli describe-tool gcam_extract_market_sector
python -m airmosaic.cli run-tool gcam_extract_market_sector --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-market.json --dry-run
python -m airmosaic.cli run-tool gcam_extract_technology_components --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-technology.json --dry-run
```

Once preflight and authorization are satisfied, execute the chosen tool by removing `--dry-run`. Each invocation creates its own run ID. Check the market task's status and CSV contents before giving it to aggregation. [The aggregation example](../../../../../config/examples/run-tool/aggregate.json) requires replacing `<source_run_id>` with that successful market task's actual run ID:

```json
{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/results/<source_project_id>/<source_run_id>/01_socioeconomic_natural_change/gcam_extract_market_sector/market_sector_rows.csv"}
```

Save the resolved non-secret JSON as `gcam-aggregate.json` in CONFIG_DIR, then use:

```powershell
$aggregateParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-aggregate.json"
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $aggregateParams --dry-run
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $aggregateParams
```

Only `${AIRMOSAIC_ASSETS_DIR}` is expanded in JSON path values. `<source_run_id>` is explanatory text to replace manually, not another variable. Do not pass receipt JSON, a tool envelope or a technology-component CSV as aggregation parameters. No automatic tool chaining, cache publication or scientific acceptance occurs.

## Plot a reviewed market output

The [plot example](../../../../../config/examples/run-tool/gcam-plot.json) also requires replacing source_run_id and example_scenario. Preserve the source CSV and check the two years, sectors, province coverage and units. Save the reviewed flat JSON under CONFIG_DIR:

```powershell
$plotParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-plot.json"
python -m airmosaic.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $plotParams --dry-run
python -m airmosaic.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $plotParams
```

The original sector_cost filter, China/Global exclusion, nonnegative weights and zero-weight mean fallback remain unchanged. Different comparison years, plot styles or calculation methods require manual adaptation and separate validation. Do not pass province_aggregate.csv or technology-component rows as plot inputs.

## Agent execution boundary

Use the four enabled registered IDs through `run-tool`; a rejected tool/path is not a reason to run raw Python or Java directly. Check `can_execute`/`blockers` for dry-run, then process status and actual artifacts for execution. Unit compatibility, positive/zero weights, province coverage, method-specific interpretations and additional query logic need separate checks. Do not equate an extracted price with validated revenue or an accepted national unit cost.

## References

- `references/xquery-patterns-price-quantity.md`: XQuery for price and quantity extraction
- `references/xquery-patterns-technology-inputs.md`: XQuery for technology components
- `references/unit-price-workflow-as-example.md`: step-by-step unit price example
- `references/output-unit-compatibility.md`: price/quantity unit compatibility
- `references/price-unit-interpretation.md`: detailed price unit interpretation and sector-specific quirks
- `references/technology-component-logic.md`: how sector costs decompose into technology components

Follow the [asset layout and review contract](../../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
