---
name: gcam-output-structure
description: Inspect the fixed GCAM BaseX output layout and query artifacts through run-tool before scoped extraction.
---

# Inspect GCAM output structure

**English** | [中文](SKILL_ZH.md)

Use `gcam_inspect_output_structure` for its fixed R inspection sequence. It accepts `max_memory` (default `1g`) and runner-supplied `output_dir`; it has no action/scenario/region/sector selector. The database is `${GCAM_RELEASE_DIR}/output/database_basexdb`, with `database_R/Prov_code_china.csv`. This differs from the per-scenario Python extractor layout.

Follow [setup, invocation and artifact checks](../references/operations.md). Check all four CSVs and their actual query contents; individual query failures can be caught inside the script, so process completion alone is insufficient.

Read only the needed detail: [XML paths](references/xpath-structure-guide.md), [custom query templates](references/xquery-csv-templates.md), [units](references/output-price-quantity-units.md), or [province mapping](references/province-region-mapping.md). Custom queries require separately reviewed task-copy adaptation; these references are not extra runner arguments. Interpret results using the [GCAM method](../../../../../methods/04_integrated_impacts/gcam.md).
