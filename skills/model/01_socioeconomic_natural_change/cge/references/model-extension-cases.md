# CGE Model Extensions

**English** | [中文](model-extension-cases_ZH.md)

Use this page when **building or extending a model**. For running an external archive and recording solver evidence, use the [CHEER GAMS operations guide](cheer-gams-operations.md). The CHEER file map below comes from source inspection of downloaded demo archives, not a GAMS solve. For another release, trace the active includes, data and scenario switches from its own `run.gms`.

## Choose an example for the concept being learned

| Example | Construction steps it demonstrates | Boundary |
|---|---|---|
| [Public general-equilibrium-model-builder skill](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md) | Its Julia two-good, two-consumer pure-exchange example goes from endowments and preferences to demand, a numeraire, zero excess demand and market-clearing checks. Code is embedded in the skill text. | Only Cobb-Douglas pure exchange is implemented; production, SAM, trade and dynamics are future extensions. It is not a CHEER runner. |
| [GAMS/MPSGE two-good, two-factor tutorial](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html) | Adds production and consumers using `$SECTORS`, `$COMMODITIES`, `$CONSUMERS`, `$PROD` and `$DEMAND`, and compares algebraic MCP. | A small teaching economy; research SAM and parameters must be supplied separately. |
| [GAMS `stdcge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_stdcge.html) → [`dyncge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_dyncge.html) | The static case shows SAM, production, trade, taxes and calibration. The dynamic case adds time, depreciation, capital and labor updates. With GAMS installed, copy them outside Git using `gamslib stdcge` and `gamslib dyncge`, then run the corresponding `.gms` files. | These are **public model-library examples**, not agent skills; their equations, solution type and data differ from CHEER. See the [GAMS library command guide](https://www.gams.com/latest/docs/UG_ModelLibraries.html). |
| [Bundled synthetic CGE tutorial](../SKILL.md#run-the-synthetic-numerical-model) | A balanced SAM, calibration, zero-shock replication, productivity shock and one-way emissions satellite with actual Python inputs, code and checks. | A simple closed economy without CHEER's interregional trade, government or dynamics. |

The sequence is pure-exchange equilibrium checks, then `stdcge` for SAM and production/trade, `dyncge` for period updates, and finally the active CHEER MPSGE source. The examples do not share parameters or interchangeable code.

## Data worth reusing

| Data | Useful for | Checks before use |
|---|---|---|
| Embedded SAMs in [GAMS `stdcge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_stdcge.html) and [`dyncge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_dyncge.html) | Learning account-to-benchmark mapping, calibration and dynamic updates without external China data. | `stdcge` has two commodity sectors and `dyncge` four; neither supplies China parameters. Retrieve originals outside Git through the official model library. |
| The `CHEER-P_demo` release: `data.gdx`, `emission_r11.gdx`, trend GDX and workbooks | Tracing the 2012-base, 30-region, 11-sector interregional flows, CO₂ benchmark mapping and SSP pathways; `cal.gms` loads `int_ag`, `va_ag`, `fd_ag`, `imp_ag` and `exp_ag`. | The active run loads GDX files. Do not assume the Excel workbooks are the exact raw sources for each GDX. Obtain and run the full demo separately from the skill. |
| Skill [electricity split workbook](../assets/cheer_clean_electricity_example/v1/benchmark.xlsx) | Mapping the aggregate IO electricity account to technology activities. | Read the included workbook and [source metadata](../assets/cheer_clean_electricity_example/v1/source.json); it is a teaching excerpt rather than a complete SAM. |
| [CEADs 2012/2015/2017 provincial MRIO](https://zenodo.org/records/4569117) and [2018/2020 MRIO](https://pmc.ncbi.nlm.nih.gov/articles/PMC12890965/) | Building the transaction, final-demand and some value-added foundation for a new Chinese multiregional CGE; the newer dataset also publishes [construction code](https://github.com/LiJie20230/China_MRIO). | Map their region/sector classifications to the model, add household income, taxes/transfers, saving/investment, factor ownership and closure, and balance the SAM. The 2018/2020 paper reports nonzero sector-output accounting errors, so these tables are not an already balanced CGE benchmark. |

For a first auditable calculation, use this repository's **synthetic SAM and Python runner** to check input shape and benchmark replication. The included CHEER-Clean workbook illustrates how technology accounts are formed. Use `stdcge` to study fuller public accounts and a documented MRIO vintage to construct a new China benchmark. Do not combine datasets from different releases as though they already formed one calibrated model.

## Active CHEER demo modules

Source inspection shows `CHEER-P_demo/run.gms` actively includes `sets.gms`, `cal.gms`, `elasticities.gms`, `emission.gms`, `parshock.gms`, `partrend.gms`, `core.gms`, `dyncal_CER.gms` and `dyn_CER.gms`; its static and BAU includes are commented out. This demo labels 2012 as its base year and defines 30 region labels and 11 commodity sectors. The [newer CHEER-P website description](https://cheer.org.cn/model-structure/extension/) refers to 2017 and 31 provinces. Use data and source from the release actually being reproduced.

| Module | Demo files | What an extension must check together |
|---|---|---|
| Classification | `sets.gms` | Sector, region, energy/resource, factor and time sets; matching input symbol dimensions. |
| Benchmark and calibration | `cal.gms`, `data.gdx` | Intermediate, value-added, final-demand, import and export data; calibrated flows, output and bilateral trade; units and balances. |
| Behavioral parameters | `elasticities.gms` | Each production/consumption nest, elasticity provenance, missing assignments and zero flows. |
| Equilibrium and closure | `core.gms` | Active MPSGE production, Armington supply, consumption, investment, representative agent, prices, carbon price and constraints. |
| Environment | `emission.gms`, `emission_r11.gdx`, `core.gms` | CO₂ benchmark allocation, `check0` and whether emissions are merely reported or enter the `pco2` carbon constraint. |
| Scenarios and dynamics | `parshock.gms`, `partrend.gms`, `dyncal_CER.gms`, `dyn_CER.gms` | Active flags and pathways, labor, TFP, energy efficiency, carbon targets, investment and next-period capital. |
| Reporting | `report_dynamic.gms` | Output, prices, labor, trade, CO₂ and model status by region, sector and period, with units. |

The separate `CHEER_demo` CHEER-Clean archive contains a concrete **technology-disaggregation design in the demo source**: `Code/Sets.gms` defines `sub_elec`; `Code/electricity.gms` loads and calibrates technology-specific inputs, generation, subsidies and prices; `Model/core_Developing_Arminton.gms` specifies `yelec(sub_elec)` activities and input nests; and `Report/report_dynamic.gms` reports technology outputs and prices. Its `run.gms` actively includes these files. This is source evidence, not a new solver result. The [CHEER-CLEAN website](https://cheer.org.cn/model-structure/extension/) also describes electricity-technology disaggregation.

### Audit the included CHEER-Clean electricity workbook

The [included workbook](../assets/cheer_clean_electricity_example/v1/benchmark.xlsx) contains the teaching excerpt described in [source.json](../assets/cheer_clean_electricity_example/v1/source.json). The script reads this file automatically. Its schema uses `IO` with `Elec`, `SUM_INPUT` and `SUM_OUTPUT`, plus `ELEC` technology columns and commodity, `labor`, `capital` and `tax` rows. Monetary units follow the workbook; the example does not supply physical generation quantities or a full SAM.

With [requirements.txt](../requirements.txt) available, run the [accounting script](../scripts/audit_cheer_electricity_split.py) from the repository root:

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/cge-cheer-electricity-accounting'
python skills/model/01_socioeconomic_natural_change/cge/scripts/audit_cheer_electricity_split.py --out-dir $out
```

`$out` must be new and outside every Git checkout. Inspect `electricity_technologies.csv`, `input_reconciliation.csv` and `validation.json`: technology inputs must reconcile with the parent electricity account, control totals must balance and reported shares are monetary value shares rather than generation shares. The two supported row-reclassification groups are `AgriPr`/`FrsPr` and `Biofuel`/`OthMfg`. Preserve the input identity reported by the script. This is benchmark accounting, not a full CHEER solve.

## Implement one extension at a time

**Split a sector into technologies.** Decide whether technologies produce the same commodity: separate production activities can supply one commodity without inventing separate final goods. Obtain technology-level benchmark outputs, intermediate/factor inputs, taxes/subsidies and physical units, and reconcile them to the original sector. Following the CHEER-Clean pattern, update sets, technology calibration, production/supply nests and reports together. Document capacity or fixed-factor constraints and elasticities where used. Recalibrate and check each technology's benchmark cost/revenue, aggregate output and goods/factor market clearing before a shock. Adding a label to `sets.gms` alone creates no economic technology.

**Add household types.** Allocate benchmark consumption, factor ownership, tax, transfers and saving to each type; balance each budget and the aggregate SAM. Replace the single `ra` and related `consum(r)` demands/endowments in `core.gms` with household-indexed expressions; specify income, employment, transfers and demand rules. Expand reports and check household budgets and aggregation. Splitting only the consumption column does not identify distributional effects. The [CHEER-HI/PPS website descriptions](https://cheer.org.cn/model-structure/extension/) inform design but are not features of this CHEER-P demo.

**Add an environmental module.** Start with a one-way satellite: map physical activity or fuel to region, sector and pollutant, calculate `E = Σ(Q × EF)`, reconcile inventory totals and report outputs. For economic feedback, state and document a mechanism: a cap and allowance price, tax and revenue recycling, technology inputs and resource use, or an effect on labor/productivity. Put its price, inputs or constraint in `core.gms` and its pathway in `parshock.gms`/`partrend.gms`; inspect `dyn_CER.gms` if feedback crosses periods. The CHEER-P demo already connects **CO₂ prices and constraints** in MPSGE; this does not establish air-pollution, air-quality or health feedback. The [CHEER-HE website](https://cheer.org.cn/model-structure/extension/) describes a different coupled configuration.

**Add regions or periods.** A new region requires bilateral intermediate, consumption and investment flows, factor endowments and external trade; reconcile each regional SAM and both sides of bilateral flows. A changed time grid requires changes to `sets.gms`, exogenous pathways in `partrend.gms` and the capital/labor update exponents in `dyn_CER.gms`: the demo uses a three-year first step and five-year later steps. Extending year labels alone is insufficient.

For each change, preserve original and edited inputs/source, solve the zero-shock benchmark first, check prices, activities, budgets and market residuals, then run a paired scenario and inspect units, direction and sensitivity. Report source mapping, synthetic tutorial execution, original CHEER reproduction and extension validation as separate levels of evidence.
