# Configure and run GCAM output tools

**English** | [中文](operations_ZH.md)

This page operates on existing outputs. For release preparation, compilation, input generation or a manually adapted simulation, first use [build and run](build-and-run.md). Those operations have no registered execution adapter.

## Environment and parameters

Run from the repository root with the installed project Python (3.10+). Set existing external `AIRMOSAIC_ASSETS_DIR`, `AIRMOSAIC_CONFIG_DIR`, `AIRMOSAIC_AUTH_DIR` using [environment examples](../../../../../config/examples/README.md). Set `GCAM_RELEASE_DIR` to an existing release outside Git and those three roots. No release is downloaded or built by these tools.

| Operation | Dependencies / fixed input |
|---|---|
| Structure | Rscript, Java, data.table, rgcam; `output/database_basexdb`, `database_R/Prov_code_china.csv` below release |
| Market / technology extraction | pandas, Java, compatible `libs/jars/BaseX-*.jar`; `output/<scenario>/database_basexdb/` |
| Aggregation | pandas; existing market-sector CSV under assets data/results |
| Plot | Rscript, dplyr, ggplot2, readr, tidyr; existing market-sector CSV, path without commas |

R runs with `--vanilla` and the selected installation's standard library; personal library/startup settings are not passed. Dry-run does not load R packages. Check Java/BaseX/rgcam compatibility for the selected release.

Structure parameters are `max_memory` (default `1g`) and runner-supplied `output_dir`. Caller `GCAM_BASEX_MAX_MEMORY` is ignored. Extractors use flat JSON such as `{"scenarios":"example_scenario","regions":"AH,BJ","sectors":"cement","years":"2021,2035"}`. Replace scenario names with actual selected database names in a personal parameter file; AH/BJ is a subset. No `release_dir`, `action` or technology `method` parameter exists.

## Calls and handoff

The public examples show syntax, not verified local data availability. Choose the stage explicitly; the examples below describe socioeconomic output use. For integrated-impact use select `04_integrated_impacts` consistently in calls and source paths.

```powershell
python -m runtime.cli run-tool gcam_inspect_output_structure --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-inspect.json --dry-run
python -m runtime.cli run-tool gcam_extract_market_sector --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-market.json --dry-run
python -m runtime.cli run-tool gcam_extract_technology_components --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/gcam-technology.json --dry-run
```

Inspect `can_execute` and `blockers`; after successful preflight and authorized scope, remove `--dry-run` to execute (structure inspection may need `--timeout 600`). The runner allocates `results/<project_id>/<run_id>/<stage>/<tool_id>/`; omit output parameters unless selecting a supported task override.

Check extraction before downstream calls. Copy [aggregate](../../../../../config/examples/run-tool/aggregate.json) or [plot](../../../../../config/examples/run-tool/gcam-plot.json) parameters into CONFIG_DIR, replace `<source_project_id>`, `<source_run_id>` and scenario values. `input_csv` must name the actual successful `market_sector_rows.csv`, not a receipt, aggregate or technology CSV. Only `${AIRMOSAIC_ASSETS_DIR}` expands in JSON paths; angle-bracket labels require manual replacement.

```powershell
$gcamParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-aggregate.json"
python -m runtime.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamParams --dry-run
python -m runtime.cli run-tool gcam_aggregate_provinces --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamParams
$gcamPlotParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gcam-plot.json"
python -m runtime.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamPlotParams --dry-run
python -m runtime.cli run-tool gcam_plot_sector_change --project-id example_project --stage 01_socioeconomic_natural_change --params-file $gcamPlotParams
```

Each invocation creates its own run ID. Plot output is injected as `UNIT_PRICE_OUT_DIR`; caller values are ignored. Rejected parameters or paths do not authorize raw-script bypass.

## Inspect actual results

| Tool | Expected files |
|---|---|
| Structure | `inspect_scenarios.csv`, `inspect_province_top_level.csv`, `inspect_industrial_sector_tree.csv`, `inspect_industrial_cost_nodes.csv` |
| Market | `market_sector_rows.csv`, `market_sector_summary.csv` |
| Technology | `technology_component_rows.csv`, `technology_component_summary.csv` |
| Aggregate | `province_aggregate.csv` |
| Plot | `sector_change_2021_2035.png`, `sector_change_weighted_mean.csv` |

Confirm receipt status and nonempty expected artifacts, then read CSV schemas, selected scenarios/years/sectors, duplicates, missing values, province coverage and units. Structure queries can fail individually; the runner rejects missing artifacts. Scientific review still requires checking contents.

Aggregation reports `weighted_price`, `quantity_sum`, `province_count` by scenario/source/sector/year, excluding China/Global. Plotting retains sector_cost selection, China/Global exclusion, nonnegative weights and a zero-weight mean fallback; years are fixed at 2021/2035. Independently review denominators and zero weights. Inspect the PNG for missing groups and axis units. Output presence does not prove compatible price/quantity units, national completeness or validated revenue. See [method](../../../../../methods/04_integrated_impacts/gcam.md).
