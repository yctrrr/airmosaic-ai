# Choosing emission-accounting and control-efficiency methods

**English** | [中文](emission_accounting_ZH.md)

An inventory translates a defined set of activities and source characteristics into an account of emissions. Start with a consistent boundary so changes between places or periods have an interpretable meaning.

## Define what belongs in the inventory

Specify the source categories, period, region, pollutants and reporting units. Decide whether the account follows territorial production, consumption or another stated perspective. Explain exclusions and overlapping categories before discussing a trend.

## Match the method to source information

Activity-based and process-based approaches require different source information. Choose a level of detail that the evidence can support. A fine classification without comparable coverage can create apparent differences that come from the accounting rather than the underlying sources.

Distinguish activity changes, source-specific characteristics, technology composition and end-of-pipe control. Describe how each contributes to a comparison without counting the same change twice.

## Interpret control efficiency consistently

Define the denominator, the population represented and how different source categories are aggregated. Missing source information and inactive sources need separate interpretations. A physically defined reduction efficiency and an efficiency measure constrained by cost answer different questions.

## Review the account

Plan source cross-checks, consistent aggregation, total conservation and uncertainty analysis. A change should be traceable to a change in evidence, method or underlying activity. Record which comparisons remain sensitive to coverage or classification.

The [accounting skill](../../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md) now supplies one direct, synthetic-validated calculation path. [Spatial allocation](spatial_inventory.md), temporal profiles, vertical injection, chemical speciation and transport-model exports remain separate adaptations. A checked source total is not an ambient concentration estimate or scientific acceptance. No MEIC data or code is used in this path.

## Activity, technology and control model

For activity cell i, technology t, pollutant p and mutually exclusive control route r:

```text
U_itp = A_i × s_it × EF^0_itp
E_itpr = U_itp × q_itpr × (1 − o_itpr × c_itpr × η_itpr)
E_p = Σ_i Σ_t Σ_r E_itpr
```

| Quantity | Meaning and denominator |
|---|---|
| `A` | Activity in the stated place/period; fuel mass, product output or energy are different activities |
| `s` | Share of that activity using each source technology; sums to one within activity |
| `EF⁰` | Pollutant mass per activity unit before the modeled end-of-pipe controls |
| `q` | Share of a technology's activity assigned to each exclusive control route; includes uncontrolled activity and sums to one per technology/pollutant |
| `o` | Fraction of that route's activity processed while its control system operates as specified |
| `c` | Fraction of the relevant exhaust/emissions captured for treatment while operating |
| `η` | Pollutant-specific removal efficiency of the captured stream while operating |

This partitioned model follows the [EPA activity/factor/reduction equation](https://www.epa.gov/air-emissions-factors-and-quantification/basic-information-air-emissions-factors-and-quantification); it assumes the represented uncontrolled factor and control summary apply to the activity on each route. [EPA inventory guidance](https://www.epa.gov/sites/production/files/2017-07/documents/ei_guidance_may_2017_final_rev.pdf) distinguishes capture, reduction efficiency, effectiveness and coverage. The local `o` is activity-weighted operation, not an automatic substitute for regulatory compliance or calendar uptime.

## Installation, operation and device combinations

Installed-device or capacity shares are not throughput shares without utilization evidence. Calendar operating hours equal activity-weighted operation only under comparable load; otherwise use fuel/throughput weights or subdivide states. Parallel alternatives belong in exclusive routes. For devices in series, `1 − product(1 − η_j)` is valid only when each efficiency is conditional on its own inlet and the common operation/capture assumptions hold. Do not sum efficiencies, add overlapping installation shares or assume independent failures. Derive a reviewed route-level summary from joint operation evidence; the first calculator does not reconstruct it.

If a factor already includes controls, applying removal again double counts abatement. The current script only accepts explicitly uncontrolled factors. Controlled-factor or CEMS mass accounting needs another reviewed route; permitted concentration limits are not actual emissions or emission factors. Fuel combustion, process reactions and fugitive losses need nonoverlapping boundaries, even when linked to the same product. Purchased electricity and on-site combustion are distinct accounts.

## Data needed and candidate sources

| Input | Candidate evidence | Required check |
|---|---|---|
| Fuel/product/activity | Statistical yearbooks, [National Data](https://data.stats.gov.cn/), authorized operation records | Geography/year, coverage, material/energy basis and aggregate reconciliation |
| Technology activity shares | Public sector/association statistics, process surveys and technical disclosures | Throughput-weighted shares; plant/capacity counts alone are insufficient |
| Installation/control routes | Public permit/implementation disclosures through the [permit portal](https://permit.mee.gov.cn/), surveys | Pollutant, denominator, date and mutually exclusive coverage |
| Operation and capture | Authorized operating/monitoring summaries or documented studies | Activity-weighting, bypass/down-time and capture versus removal |
| Factors/removal | Applicable official factor chapters, source tests or reviewed sector literature | Technology, fuel/material, load, pollutant definition, control status, version and uncertainty |

These are source-preparation options, not implemented downloaders, verified annual datasets or authorization to inspect private records. No such real data were retrieved for this example. Use applicable [EMEP/EEA chapters](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023); the [factor viewer](https://efdb.apps.eea.europa.eu/) gives chapter values precedence on discrepancies. [IPCC energy guidance](https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol2.html) applies to its greenhouse-gas scope; its factors do not substitute automatically for criteria pollutants.

Normalize numerator mass and activity denominator together. The script converts compatible mass/energy units, not fuel mass to energy without heating values. Reconcile dry/as-received fuel, product/precursor mass, sulfur/ash and pollutant mass conventions before use; NOx as NO₂-equivalent mass is not NO mass. Average category factors do not certify individual-source performance.

## Synthetic example and checks

All quantities here are invented arithmetic examples, not empirical coal factors or actual regional estimates. A synthetic 10,000-tonne activity uses technologies A/B at 60%/40%. SO₂ uncontrolled factors are 10/8 kg per tonne. A has 20% uncontrolled activity and 80% on a route with `o=0.9`, `c=0.95`, `η=0.9`; B has full coverage, operation/capture of one and removal of 0.95:

```text
A: 60000 × [0.2 + 0.8 × (1 − 0.9×0.95×0.9)] = 23064 kg
B: 32000 × (1 − 0.95) = 1600 kg
SO₂: uncontrolled 92000 kg = emitted 24664 kg + removed 67336 kg
```

The separate synthetic NOx inputs yield 30,960 kg emitted. Never merge different pollutants into an undefined combined mass. Full input and executable calls live only in the skill.

Check complete shares, unique keys, factor/route coverage, units/bases, `uncontrolled = emitted + removed` and agreement of detail with pollutant-specific aggregates. Missing routes do not silently mean uncontrolled activity. Preserve inputs and failed cases. Subsequent uncertainty scenarios must respect share-sum constraints and correlated factors; Monte Carlo propagation is not implemented in this first calculator.
