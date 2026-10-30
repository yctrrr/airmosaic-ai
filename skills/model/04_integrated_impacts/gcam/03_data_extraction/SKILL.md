---
name: gcam-data-extraction
description: Extract market or technology rows from existing GCAM databases, aggregate province market rows, and plot the fixed comparison through reviewed run-tool adapters.
---

# Extract and compare GCAM results

**English** | [中文](SKILL_ZH.md)

Use the implemented IDs `gcam_extract_market_sector`, `gcam_extract_technology_components`, `gcam_aggregate_provinces` and `gcam_plot_sector_change`. Follow [operations](../references/operations.md) for exact dependencies, flat JSON parameters, dry-run/execution calls and artifacts.

Declare scenario, region, sector and year scope explicitly. Lists are comma-separated strings; the technology extractor has no `method` parameter. Review units and row coverage before passing a successful market CSV to aggregation or plotting. These are separate invocations with separate run IDs.

Aggregation excludes China/Global; its weighted prices do not establish complete national coverage. Plotting compares fixed years 2021/2035 and retains sector-cost filtering and weight fallback. Different years or query logic require reviewed manual adaptation.

Read detailed interpretation only when needed: [price/quantity queries](references/xquery-patterns-price-quantity.md), [technology queries](references/xquery-patterns-technology-inputs.md), [unit compatibility](references/output-unit-compatibility.md), [price interpretation](references/price-unit-interpretation.md), [technology components](references/technology-component-logic.md), [worked unit-price reference](references/unit-price-workflow-as-example.md). The [method](../../../../../methods/04_integrated_impacts/gcam.md) explains what the extracted measures mean.
