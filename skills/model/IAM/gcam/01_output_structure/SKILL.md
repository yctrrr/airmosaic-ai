---
name: gcam-output-structure
description: Inspect GCAM output structure using a fixed standalone R script and XQuery references. Use before extraction to check available nodes and units; custom scenario or sector queries require adaptation.
---

# GCAM Output Structure Exploration

> Invocation status: `gcam_inspect_output_structure` is an implemented standalone R script, disabled in `run-tool`. It has a fixed inspection sequence, not an action/scenario/region query API.

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

Supported script flags are `--release-dir=...`, `--output-dir=...`, `--max-memory=...`. It also reads `GCAM_BASEX_MAX_MEMORY`; there is no `action`, `scenario`, `region` or `sector` API argument.

## Quick tasks

- Inspect scenarios and the predefined node/sector queries: use the fixed R script after its layout and output directory are reviewed. It does not accept a query selector.
- Custom sector/province queries: read `references/xquery-csv-templates.md` and adapt an authorized task copy.
- Explore the XML tree: read `references/xpath-structure-guide.md`.
- Check units: read `references/output-price-quantity-units.md`.
- Map province codes: read `references/province-region-mapping.md`.

## Standalone execution boundary

Use `describe-tool gcam_inspect_output_structure` to locate the reviewed script. It is disabled in `run-tool`. After dependencies and the fixed input layout are checked, the separately authorized R invocation from the repository root is:

```powershell
$structureRunId = [guid]::NewGuid().ToString("N")
$structureOutput = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/$structureRunId/gcam_inspect_output_structure"
Rscript skills/model/IAM/gcam/01_output_structure/scripts/inspect_gcam_xml_structure.R "--release-dir=$env:GCAM_RELEASE_DIR" "--output-dir=$structureOutput" "--max-memory=1g"
```

Always supply the output directory: the raw script otherwise writes into the model release. Standalone execution has no runner path checks, environment isolation or sanitized receipt. Inspect each output/error before declaring the inspection complete; custom queries and a per-scenario database layout require manual adaptation.

## References

- `references/xpath-structure-guide.md`: full GCAM XML tree structure with node types and typical paths
- `references/xquery-csv-templates.md`: reusable XQuery templates for CSV output
- `references/output-price-quantity-units.md`: explanation of price-unit vs output-unit and compatibility
- `references/province-region-mapping.md`: province codes, China aggregate node, and mapping conventions
