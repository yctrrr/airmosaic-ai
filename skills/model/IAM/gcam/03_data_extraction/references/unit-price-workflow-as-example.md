# Existing-Result Extraction and Aggregation

This reference describes registered tools, not an automatic unit-price selection or scientific-validation pipeline. Run from the repository root using the [extraction skill](../SKILL.md) and [model guide](../../../../../../harness/usage/model-analysis.md).

## Implemented artifacts

Each tool creates its own `output/<run_id>/<tool_id>/`:

| Tool ID | Actual files |
|---|---|
| `gcam_extract_market_sector` | `market_sector_rows.csv`, `market_sector_summary.csv` |
| `gcam_extract_technology_components` | `technology_component_rows.csv`, `technology_component_summary.csv` |
| `gcam_aggregate_provinces` | `province_aggregate.csv` |
| `gcam_plot_sector_change` (standalone R, runner disabled) | `sector_change_2021_2035.png`, `sector_change_weighted_mean.csv` |

The extractors take comma-separated scenario/region/sector/year strings; aggregation takes the existing market-sector CSV as input_csv. See the skill for parameter JSON and run-tool commands. Pass the successful market task ID explicitly; there is no automatic chaining.

## Checks before aggregation

Market rows distinguish marketplace from sector_cost. Preserve source, year, unit and scenario columns. Confirm provincial coverage; China-only rows do not support province aggregation. AH/BJ examples are subsets, not national coverage.

The aggregator excludes China/Global, groups by scenario/source/sector/year, and writes weighted_price, quantity_sum, province_count. Nonnegative quantities weight available prices; it falls back to an ordinary mean when valid weights sum to zero. Units and coverage are not automatically validated. Inspect original rows and these assumptions before interpreting results.

## Technical components and interpretation

The technology tool extracts available costs, output, coefficients, demand, component prices and CO2 fields, then forms its existing summary. These are not a validated sector-cost decomposition or universal price proxy. Review sample coverage and denominators before comparing technology-weighted and sector-weighted values.

No current tool creates selected_unit_price, selected_quantity, selected_aggregation_scope or an automatic explainability-quality grade. Selection among marketplace, sector-cost, provincial and China representations requires a separately reviewed method and implementation. Do not silently apply fixed residual thresholds or assume a conceptual hierarchy has been accepted.

## Standalone plotting and scientific acceptance

Plotting is a separately prepared R step with fixed years, explicit input and UNIT_PRICE_OUT_DIR, without a runner receipt. Check packages and coverage first.

Document unit compatibility, model version, missing rows, zero-weight behavior and coverage locally. For a justified conversion or override, preserve original units and method evidence; successful extraction alone does not authorize a revenue or national-price claim.
