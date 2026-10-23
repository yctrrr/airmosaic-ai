---
name: gcam-data-extraction
description: Extract GCAM scenario output data using parameterized XQuery. Supports market rows, sector costs, technology components, provincial aggregation, and plotting. Use unit price extraction as the first worked example; apply the same pattern to industrial output, technology I/O, emissions, or energy demand.
---

# GCAM Data Extraction

> Invocation status: named wrappers in Agent Contract sections are proposed, not registered APIs. Verify actual scripts and template requirements in the [tool catalog](../../../../../harness/tool-catalog.md).

## Local paths and authentication

Follow the [shared storage contract](../../../../../harness/storage-and-credentials.md): data and results use `AIRMOSAIC_LOCAL_WORKSPACE`, personal non-secret configuration uses `AIRMOSAIC_CONFIG_DIR`, and browser authentication state uses `AIRMOSAIC_AUTH_DIR`. Read only task-needed configuration; never inspect, print or copy credential values or browser state. Set module output arguments explicitly for each run. These conventions do not imply automatic config loading or runtime isolation.

## Purpose

This layer provides parameterized scripts for extracting data from GCAM BaseX output databases. All scripts accept scenario names, region lists, sector names, and year lists as arguments. No pre-built sector registry is required.

The unit price workflow serves as the first worked example. The same patterns apply to other extraction tasks.

## Prerequisites

```powershell
$env:GCAM_RELEASE_DIR = "<path to gcam-china-v8-Windows-Release-Package>"
$env:UNIT_PRICE_OUT_DIR = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/example/gcam"
```

BaseX database must exist at:
```text
$env:GCAM_RELEASE_DIR/output/<scenario>/database_basexdb/
```

## Extraction Tools

### `xquery_market_sector.py`

Extracts market rows (Marketplace/market) and sector cost rows for specified scenarios, regions, sectors, and years. Outputs a combined CSV with price, quantity, unit columns.

Parameters: `--scenarios`, `--regions`, `--sectors`, `--years`, `--out-dir`

### `xquery_technology_components.py`

Extracts technology-level component rows including input coefficients, demand, prices, secondary outputs, and CO2 emissions. Decomposes sector cost into energy, non-energy, capital, and carbon components.

Parameters: `--scenarios`, `--regions`, `--sectors`, `--years`, `--out-dir`. The current script does not implement `--method`.

### `xquery_province_aggregator.py`

Aggregates province-level rows to weighted national values. Computes weighted prices and total quantities.

Parameters: `--input-csv`, `--out-dir`

### `plot_sector_change.R`

Plots sector price or quantity changes between two years, with boxplots, weighted means, and change arrows.

Parameters: `--sectors`, `--scenarios`, `--input-csv`. Set `UNIT_PRICE_OUT_DIR` for output; `--out-dir` is not implemented. The current comparison years are fixed at 2021 and 2035.

## Workflow Example: Unit Price

Use the repository's classified model-analysis guide for repository-root PowerShell commands. The sequence is: inspect actual scenario/region names, extract market and technology rows, validate units and provincial coverage, aggregate provincial rows, then plot. China-only rows cannot be used for provincial aggregation.

## Agent Contract

External agents should call wrappers:
- `extract_gcam_market_sector_data`
- `extract_gcam_technology_components`
- `aggregate_gcam_province_data`
- `plot_gcam_sector_change`

The agent must not receive direct BaseX execution or unrestricted filesystem access.

## References

- `references/xquery-patterns-price-quantity.md`: XQuery for price and quantity extraction
- `references/xquery-patterns-technology-inputs.md`: XQuery for technology components
- `references/unit-price-workflow-as-example.md`: step-by-step unit price example
- `references/output-unit-compatibility.md`: price/quantity unit compatibility
- `references/price-unit-interpretation.md`: detailed price unit interpretation and sector-specific quirks
- `references/technology-component-logic.md`: how sector costs decompose into technology components
