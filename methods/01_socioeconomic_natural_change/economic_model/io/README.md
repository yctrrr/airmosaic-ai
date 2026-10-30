# Input-output analysis: production networks and environmental extensions

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

The standard demand-driven input-output (IO) model traces a stated final demand through fixed interindustry coefficients. Define monetary units, price year, sectors, regions, trade treatment and final-demand scope before calculation. It is an accounting scenario rather than an observed causal effect.

## Input-output: the production network

Let `Z[i,j]` be the input from sector `i` used by sector `j`, and `x[j]` be sector `j`'s output. The direct requirement coefficient is `A[i,j] = Z[i,j] / x[j]`. In the standard demand-driven, fixed-coefficient model, `x = A x + y`, so `x = (I − A)^−1 y`, where `y` is final demand and `(I − A)^−1` is the **Leontief inverse**. It counts direct and upstream output needed for a stated final-demand change. A multi-regional IO (MRIO) table adds region-by-sector blocks, including trade links; it does not by itself make demand or coefficients respond to prices. See [Eurostat's IO methodology](https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/methodology).

An environmental extension can attach a direct physical intensity `f` to output, giving a final-demand footprint `fᵀ(I − A)^−1 y` after units and import boundaries are reconciled. A separate IO price or cost-push model can propagate an imposed input-price change through fixed coefficients. These extensions have useful accounting roles, but a standard fixed-coefficient quantity or price IO model does not jointly solve substitution, income, final demand and market prices as behavioral responses. Dynamic IO and other hybrid variants may add some of those mechanisms explicitly; evaluate their actual equations rather than the IO label alone. [Eurostat's IO training overview](https://cros.ec.europa.eu/book-page/supplyuse-and-input-output-tables-and-analysis) includes both the Leontief and cost-push price models.

## Operational route and interpretation

Check sector balances and `(I − A)` conditioning before solving. Compare solved output with the supplied benchmark, then attach a documented direct physical intensity to calculate the footprint of each final-demand category. The [IO skill](../../../../skills/model/01_socioeconomic_natural_change/input-output-analysis/SKILL.md) provides a bounded synthetic CSV calculator; larger MRIO systems can use [pymrio](https://pymrio.readthedocs.io/en/stable/) with separately obtained and licensed source tables. IO coefficients and demand remain fixed in this calculation; see [CGE](../cge/README.md) for explicit price and substitution responses. Physical stock and flow accounting is covered by [MFA](../material_flow_analysis.md).

The publicly released [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents) informed the system-boundary and physical-balance checks. Its broader industrial-ecology workflow is not imported into this fixed-coefficient calculator.
