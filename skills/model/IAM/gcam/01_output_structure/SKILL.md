---
name: gcam-output-structure
description: Inspect GCAM output structure through run-tool with a fixed R script and XQuery references. Use before extraction to check available nodes and units; custom scenario or sector queries require adaptation.
---

# GCAM Output Structure Exploration

> Invocation status: `gcam_inspect_output_structure` is an implemented R script enabled in `run-tool`. It has a fixed inspection sequence, not an action/scenario/region query API.

## Local paths and authentication

Follow the [shared storage contract](../../../../../harness/storage-and-credentials.md) and [execution guide](../../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_LOCAL_WORKSPACE` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `output/<run_id>/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

Before extracting prices, quantities, or technology data from GCAM BaseX output databases, use this layer to understand what is available. This layer provides generic tools to list scenarios, regions, sectors, subsectors, technologies, and their internal node structures without requiring a pre-built sector registry.

## How It Works

GCAM writes model output as XML, stored in a BaseX database. The top-level structure is:

```text
collection()
  -> scenario
    -> world
      -> region
        @type = "region"
        @name = "AH" / "BJ" / ... / "China"
        -> supplysector / pass-through-sector
          -> subsector
            -> technology
              -> output-primary / output / physical-output
              -> input / demand-physical
```

The most common XPath entry point for region-level queries:

```xquery
collection()/scenario/world/*[@type="region"]
```

For China aggregate (not provincial):

```xquery
collection()/scenario/world/*[@type="region" and @name="China"]
```

## Prerequisites and actual database layout

`gcam_inspect_output_structure` needs R, its declared packages, Java/BaseX and explicit `GCAM_RELEASE_DIR`. The current R script reads `${GCAM_RELEASE_DIR}/output/database_basexdb` and `${GCAM_RELEASE_DIR}/database_R/Prov_code_china.csv`. This is different from the Python extractors' per-scenario layout; adapt a task copy if the authorized release uses another structure.

Runner parameters are `max_memory` (default `1g`, e.g. `512m`) and optional task-scoped `output_dir`. The model root comes only from checked `GCAM_RELEASE_DIR`; release_dir is not a runner parameter. Caller GCAM_BASEX_MAX_MEMORY is ignored. There is no `action`, `scenario`, `region` or `sector` API argument. The raw script flags remain an implementation detail.

## Quick tasks

- Inspect scenarios and the predefined node/sector queries: use the registered tool after its layout and task scope are reviewed. It does not accept a query selector.
- Custom sector/province queries: read `references/xquery-csv-templates.md` and adapt an authorized task copy.
- Explore the XML tree: read `references/xpath-structure-guide.md`.
- Check units: read `references/output-price-quantity-units.md`.
- Map province codes: read `references/province-region-mapping.md`.

## Unified execution boundary

Use the public [parameter example](../../../../../examples/run-tool/gcam-inspect.json) and the installed project interpreter:

```powershell
python -m airmosaic_core.cli describe-tool gcam_inspect_output_structure
python -m airmosaic_core.cli run-tool gcam_inspect_output_structure --params-file examples/run-tool/gcam-inspect.json --dry-run
python -m airmosaic_core.cli run-tool gcam_inspect_output_structure --params-file examples/run-tool/gcam-inspect.json --timeout 600
```

Rscript runs with --vanilla, task HOME/TEMP and no personal startup/profile/library settings. Install data.table and rgcam in that R installation's standard library; Java uses rgcam's classpath, whose compatibility still needs verification. check-tool/dry-run do not launch R and leave package loading unverified. Actual execution checks namespaces before sourcing the script; the receipt reports r_dependency_unavailable when loading fails.

The runner allocates output_dir and requires all four non-empty outputs: inspect_scenarios.csv, inspect_province_top_level.csv, inspect_industrial_sector_tree.csv and inspect_industrial_cost_nodes.csv. The original script continues after individual query errors, so missing artifacts cause expected_outputs_missing instead of success. Inspect contents separately; an empty query or existing file is not scientific validation.

Custom queries and a per-scenario database layout require manual adaptation. Preserve the original release and existing outputs; rejected paths/parameters do not authorize bypassing the runner. Direct raw-script calls retain their old defaults and bypass these protections.

## References

- `references/xpath-structure-guide.md`: full GCAM XML tree structure with node types and typical paths
- `references/xquery-csv-templates.md`: reusable XQuery templates for CSV output
- `references/output-price-quantity-units.md`: explanation of price-unit vs output-unit and compatibility
- `references/province-region-mapping.md`: province codes, China aggregate node, and mapping conventions
