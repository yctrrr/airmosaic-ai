---
name: ind-yearbook
description: Adapt industrial-yearbook regional-sector and product-output R templates to authorized Excel inputs; templates require review and are disabled in run-tool.
---

# Industrial yearbook tables

**English** | [中文](SKILL_ZH.md)

Use existing Excel tables to prepare province–industry economic indicators or province–product output. National-sector processing requires a separate implementation.

## Prepare a task copy

Use R with `data.table`, `readxl`, and `stringr`, plus a spreadsheet viewer for source checks. Record edition years, actual data years, authorized files/sheets, units and industry-code version. Put immutable originals in an external versioned data folder; create the task specification and mapping in `AIRMOSAIC_CONFIG_DIR`, with working copies and results in a fresh project result folder.

The two R templates are adaptation material: `yearbook_regional_sector_template` and `yearbook_product_output_template` cannot execute through `run-tool`. Inspect their current metadata without starting processing:

```sh
python -m runtime.cli describe-tool yearbook_regional_sector_template
python -m runtime.cli describe-tool yearbook_product_output_template
```

## Adapt and run only the reviewed task script

1. Inspect representative authorized sheets in a spreadsheet viewer. Regional tables are expected beneath `中国工业统计年鉴{edition}（Excel）/3分地区数据/`; product tables beneath `工业产量/` or `分地区工业主要产品产量/` in each edition folder.
2. Copy the required [regional](templates/process_regional_sector.R) or [product](templates/process_product_output.R) template into the task workspace and review it before sourcing. The current files contain incomplete/invalid expressions and simplified handling; they are not ready-to-run recipes. Validate syntax and repair the task copy separately before testing on synthetic sheets.
3. Set explicit input files, edition range, source-sheet selection, mappings and a fresh output folder in the reviewed task copy. [config.yaml](templates/config.yaml) is a declaration only: templates neither load it nor expand its placeholders. Existing examples are structural illustrations.
4. Review every write: regional per-year processing writes inside edition folders despite its final `output_dir`; product processing writes within edition folders and `root`, with no independent output-directory argument. Use task working copies or adapt all writes before any use; setting one final destination does not protect originals.
5. Check extracted headers and units, `地区` panel boundaries, continuation sheets, numeric-conversion failures, edition/data-year mapping, excluded tables and industry-code matches. The templates assume data year = edition year − 1; verify that assumption against actual tables.
6. Export the cleaned table, source/edition inventory, mappings, conversion issues, missing coverage and all fill rules. Independently check several source cells and year/region/industry/product totals. Missing values are not automatically zeros; optional interpolation, extrapolation or supplementation needs a separately justified task implementation.

Detailed layout and historical design: [processing techniques](references/processing-guide.md), [pipeline blueprint](references/pipeline_blueprint.md), [industry matching](references/industry_code_matching.md), [encoding repair](references/encoding_repair.md). Historical references retain their existing language. Scientific choices and interpretation: [yearbook methods](../../../../methods/01_socioeconomic_natural_change/statistical_yearbooks.md).
