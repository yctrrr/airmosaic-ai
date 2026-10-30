# Interpreting GCAM scenario outputs

**English** | [中文](gcam_ZH.md)

GCAM links socioeconomic assumptions, energy and land systems, technologies and climate policy in internally consistent scenarios. Compare a declared baseline and intervention using the same model version, regional definitions and reporting years. A scenario difference is conditional on model assumptions; it is not an empirically identified causal effect.

## Prepare a model experiment

Choose the model variant, version and the scientific change before choosing software operations. An unchanged, compatible release can use its supplied executable and XML. A change to C++ behavior requires a source build; a change to data-system processing may require rebuilding matching input XML. These operations address different parts of the model and do not substitute for each other.

1. Define the question, baseline/intervention, periods and outputs. Record which assumptions remain shared and which change; keep model, input and executable identities together.
2. Select a compatible release or a version-pinned build, then verify the runtime environment independently from the scientific assumptions. Build success does not establish input correctness or calibration.
3. Prepare an independent task copy with explicit configuration, input references, logs and output destinations. Configuration names and relative paths depend on the selected branch. Preserve original scenarios and avoid multiple writers to one database.
4. Run the requested experiment and examine process exit status, completion of the requested periods, solver failures and database writing. A success-looking message is not sufficient evidence of numerical success.
5. Check calibration, accounting consistency, regional/time coverage and sensitivity to relevant assumptions before interpreting scenario differences. Keep technical completion separate from scientific acceptance.

Existing XML does not have to be regenerated for every experiment. Rebuilding inputs can change calibration and data lineage, so record affected modules and generated versions when it is necessary. Native model outputs retain their task identity; reviewed derived results may be registered for reuse only after the applicable checks and human review. Commands, platform differences, locations and manual adaptation points belong to the [build/run reference](../../skills/model/04_integrated_impacts/gcam/references/build-and-run.md).

## Quantities, prices and components

Select the reported object before extraction: a market price, sector output, physical demand, or technology cost/input component. XML nodes with similar names need not share a denominator. Match price units, quantity units, currency base year and aggregation level before multiplying them. A model price is not automatically an observed transaction price or a validated enterprise control cost.

Technology component sums depend on model accounting boundaries and coefficients. Distinguish energy/material inputs, non-energy costs and output units; avoid double-counting intermediate inputs or treating every component as independent expenditure. Preserve source-node labels with derived measures.

## Regional comparisons

GCAM-China and official GCAM-Core have different regional and sector structures. Province codes must be mapped against the selected release. Exclude aggregate China/Global rows when summing provinces, and report missing provinces explicitly. National quantity is a sum only across compatible, non-overlapping units; a national price is a quantity-weighted value only when weights and denominators are compatible. Zero weights require explicit interpretation.

Use the same regions and sectors for paired scenarios. Separately report structural change, quantity change and unit-price change; a fixed-year comparison cannot establish the complete time path. Keep interpolation and omitted-year assumptions visible.

## Evidence and limits

Check scenario/year/region coverage, unique rows, units, nonfinite values and component closure. Retain baseline/intervention pairs and provenance. Output inspection validates database access and structure; extraction and plotting do not establish solver convergence, calibration quality or scientific acceptance.

The [GCAM skill](../../skills/model/04_integrated_impacts/gcam/SKILL.md) owns commands, configuration, artifacts and retained build troubleshooting. There is no simulation launcher; compilation and configuration edits remain manual. Historical specialist references provide [model-variant context](../../skills/model/04_integrated_impacts/gcam/references/gcam-china-vs-official.md) and [unit interpretation](../../skills/model/04_integrated_impacts/gcam/03_data_extraction/references/price-unit-interpretation.md).
