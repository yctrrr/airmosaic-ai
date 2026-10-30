# Tool capabilities and execution

**English** | [中文](tool-catalog_ZH.md)

Use `catalog/tools/*.yaml` and `list-tools`/`describe-tool` for actual IDs, parameters and support. The reviewed catalog has 26 entries, 17 with reviewed run-tool adapters (8 core CLI, 6 Python and 3 R entries). Registration does not establish local dependencies, login or scientific validity. See [queries](usage/tool-registry.md), [execution](usage/run-tool.md) and [validation records](verification.md).

## Core entries

Use the installed project environment from the repository root. Direct CLI queries retain their public detail; runner summaries are sanitized.

| Tool ID | CLI command | Runner | Scope |
|---|---|---|---|
| `airmosaic_list_datasets` | list-datasets | yes | Acquisition declarations |
| `airmosaic_describe_dataset` | describe-dataset | yes | Metadata and existing aliases |
| `airmosaic_search_datasets` | search-datasets | yes | Local metadata search |
| `airmosaic_check_availability` | check-availability | yes | Presence only; direct CLI can expose local paths |
| `airmosaic_draft_causal_plan` | draft-causal-plan | yes | Local planning template, no model call or causal conclusion |
| `airmosaic_list_tools` | list-tools | yes | Categories, filters and static state |
| `airmosaic_describe_tool` | describe-tool | yes | Manifest, parameters and entrypoint |
| `airmosaic_check_tool` | check-tool | yes | Static prerequisites, not login validation |
| `airmosaic_run_tool` | run-tool | no | Runner display entry; recursion is disabled |

The SDK exposes DataCatalogService, DataAccessService, CausalDesignService, ToolRegistryService and ToolRunnerService; see [core usage](usage/core.md). Local stdio MCP is implemented ([setup](usage/mcp.md)); REST, automatic skill installation and general cross-tool orchestration remain unimplemented.

## Acquisition and processing

See [classified usage](usage/data-acquisition.md).

| Tool ID | Runner | Scope |
|---|---|---|
| `worldpop_download` | yes | Network metadata discovery; file transfer enabled explicitly |
| `csmar_process_company_info` | yes | Existing basic-company ZIP, pandas/openpyxl |
| `ihme_gbd_fetch_results` | yes | Existing authorized local browser, network/session flags and reviewed dimensions |
| `csmar_browser_download` | reference | User's institutional access and an available browser/manual flow |
| `yearbook_regional_sector_template` | template | Adapt region/industry headers, encoding, years and output |
| `yearbook_product_output_template` | template | Adapt products, units and missingness; no separate national-sector implementation |

Nine dataset declarations are present in this version. They describe metadata, not successful acquisition:

| Dataset ID | Existing responsible skill_id | Declared scope |
|---|---|---|
| `worldpop_population_grid` | worldpop | Population raster |
| `worldpop_zonal_statistics` | worldpop | Zonal-statistics declaration, no standalone local processor |
| `csmar_listed_company_basic` | csmar | Listed-company basic information |
| `csmar_financial_statements` | csmar | Table-specific acquisition requires review |
| `industrial_yearbook_national_sector` | ind_yearbook | National-sector indicators need implementation/adaptation |
| `industrial_yearbook_regional_sector` | ind_yearbook | Regional-sector indicators |
| `industrial_yearbook_product_output` | ind_yearbook | Regional product output |
| `ihme_gbd_mortality_rates` | ihme-gbd-results | Mortality rates |
| `ihme_gbd_population` | ihme-gbd-results | Population; review request dimensions |

## Computation and templates

Detailed inputs/dependencies are in [model analysis](usage/model-analysis.md), [machine learning](usage/machine-learning.md) and the corresponding skills.

| Tool ID | Runner | Scope |
|---|---|---|
| `gcam_extract_market_sector` | yes | Existing market/sector database rows; pandas and Java/BaseX |
| `gcam_extract_technology_components` | yes | Component rows and summaries; no method parameter |
| `gcam_aggregate_provinces` | yes | Existing market CSV; review coverage, units and weights |
| `gcam_inspect_output_structure` | yes | Fixed R queries and declared database layout |
| `gcam_plot_sector_change` | yes | Required market CSV, fixed 2021/2035 years and injected task output |
| `gcam_configuration_reference` | reference | Reviewed configuration work, no simulation launcher |
| `pm25_hia_calculate_template` | template | Health inputs/method need adaptation |
| `pm25_hia_visualize_template` | template | Map inputs, grid, dependencies and outputs need adaptation |
| `ml_regression_workflow` | yes | Numeric prediction, predictive explanations and declared-DAG PLR |
| `mlr3_workflow_reference` | reference | Framework modeling, tuning and prediction guidance |
| `timexer_workflow_reference` | reference | External forecasting configuration and inference adaptation |

The [four-stage guide](four-step-workflow.md) distinguishes method-only and computational work. Build troubleshooting is guidance rather than a compilation adapter.

## Registration and handoff

Executable JSON examples contain declared parameters; the tool ID is supplied to run-tool. Lists use the adapter's documented comma-separated strings, and output parameters can usually be omitted for task allocation. Reference/browser plans with `reference_tool_id` and `execution_supported=false` are not executable runner parameters.

New tools need a manifest, reviewed policy/adapter, parameter handling, classified guidance and a skill under the [registration contract](tool-registration.md). A static ready state differs from a task's can_execute result; process success differs from scientific acceptance.

Methods explain research design, skills implement operations, workflows compose data/skills and projects retain concrete study evidence. General automatic orchestration is not implemented.
