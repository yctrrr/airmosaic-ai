"""Explicit adapter allowlist. Adding a manifest alone never enables new code."""

ADAPTERS = {
    **{f"airmosaic_{name}": "core_cli" for name in (
        "list_datasets", "describe_dataset", "search_datasets", "check_availability",
        "draft_causal_plan", "list_tools", "describe_tool", "check_tool")},
    "worldpop_download": "worldpop", "csmar_process_company_info": "csmar",
    "ihme_gbd_fetch_results": "gbd", "gcam_extract_market_sector": "gcam_extract",
    "gcam_extract_technology_components": "gcam_extract", "gcam_aggregate_provinces": "gcam_aggregate",
    "gcam_inspect_output_structure": "gcam_inspect", "gcam_plot_sector_change": "gcam_plot",
}
PATH_PARAMETERS = {
    "core_cli": {}, "worldpop": {"root": "output_directory"},
    "csmar": {"zip": "input_file", "out_dir": "output_directory"},
    "gbd": {"out": "output_file"}, "gcam_extract": {"out_dir": "output_directory"},
    "gcam_aggregate": {"input_csv": "input_file", "out_dir": "output_directory"},
    "gcam_inspect": {"output_dir": "output_directory"},
    "gcam_plot": {"input_csv": "input_file", "out_dir": "output_directory"},
}
