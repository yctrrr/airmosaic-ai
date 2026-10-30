---
name: energy-balance-methods
description: Prepare energy-balance workbooks, explicit conversion coefficients and closure checks through a manual tabular workflow; no executable adapter is bundled.
---

# Prepare energy balance tables

**English** | [中文](SKILL_ZH.md)

Prepare a source-preserving energy table and coefficient audit for a specified region, period and energy boundary. This repository has no energy-balance CLI or processing script.

## Configure the handoff

Use Excel or a table-processing environment selected for the task. Keep immutable source workbooks in a versioned external data folder; create working files and outputs under a fresh project result folder. Record source edition, data years, sheet names, units, sector/fuel classification and requested denominator in a non-secret task sheet.

## Work in the table editor

1. Open each target sheet and retain its original headers, notes and physical units. Copy only the authorized tables into working sheets; preserve source file/sheet/cell references.
2. Create a long table keyed by region, year, balance item, sector and fuel. Store source value and unit separately from converted value and unit.
3. Create a coefficient sheet keyed by applicable year/fuel/region, with coefficient unit, source, proxy year and applicability. Review composite fuels before assigning factors.
4. Join only reviewed coefficients. For example, physical tonnes multiplied by `tce/tonne` yield tonnes of coal equivalent; check scale factors for tables in ten-thousand units. Keep unmatched coefficients and undefined denominators explicit.
5. Compare sector totals with the corresponding source total under the same boundary. Avoid adding household totals to their urban/rural components. Export raw-unit detail, converted detail, shares, coefficients and discrepancy tables.

## Verify

Recalculate a few source-to-output cells independently, check key uniqueness and coefficient coverage, and explain nonclosure before acceptance. Preserve signed source values; classify negative balance entries rather than automatically clipping them. Do not reuse an external project's historical conversion defaults without reviewing their sources and years.

Scientific definitions, uncertainty and interpretation: [energy-balance methods](../../../../methods/01_socioeconomic_natural_change/energy_balance.md).
