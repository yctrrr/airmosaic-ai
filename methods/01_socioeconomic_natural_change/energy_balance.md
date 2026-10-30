# Energy balances and coal-equivalent conversion

**English** | [中文](energy_balance_ZH.md)

## Research question

Estimate energy use or sectoral shares under a declared accounting boundary. Final consumption, transformation inputs/outputs, losses and non-energy use answer different questions; choose the relevant balance items before adding fuels or sectors.

## Sources and units

Keep CEADs provincial workbooks, official energy balance tables and conversion appendices as distinct source versions. Preserve region, year, sector, fuel, physical unit, source value and balance item. Coal equivalent is an energy-normalized quantity, not physical fuel mass. Conversion coefficients need a dimensional unit, reference year, source and applicability.

## Conversion and aggregation

Convert physical quantities only after harmonizing scale and fuel definitions. For example, tonnes × tonnes-coal-equivalent per tonne yields tonnes of coal equivalent. Composite fuels require a justified composition/weighting rule. Compute a sector share from a numerator and denominator with the same year, region, fuels and balance boundary; a zero denominator yields an undefined share. Avoid counting both household totals and urban/rural components.

A historical source workflow described in this library covered 47 final-consumption sectors and 20 fuels. For 1997–2018 it used one national coefficient per fuel across regions/years, mainly based on the 2019 national final-consumption ratio, with stated exceptions for cleaned coal and other energy; 2019–2022 used year-specific evidence. This is a project-specific approximation, not a universal conversion rule or a verified coefficient set for new years. Reassess the source appendix before reusing it.

## Error and quality

Check uniqueness, coefficient coverage, dimensional consistency and source-to-output calculations. Compare sector sums with the appropriate source total and retain discrepancies rather than overwriting the source to force closure. Preserve signed balance values: a negative entry may have accounting meaning. Version changes, proxy coefficients and composite fuels contribute uncertainty; compare alternative defensible coefficients when conclusions depend on them.

## Interpretation

Report energy and sector shares together with the chosen boundary and coefficient basis. Coal-equivalent totals do not directly measure emissions, economic output or efficiency. An internally closed balance can still use an unsuitable coefficient or sector mapping. Operational tables and file checks are described in the [energy-balance skill](../../skills/data_acquisition/01_socioeconomic_natural_change/energy-balance/SKILL.md).
