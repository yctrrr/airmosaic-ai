---
name: life-cycle-assessment
description: Calculate a small linear single-output life cycle inventory and characterized impact from supplied process CSVs, with explicit boundaries and units.
compatibility: "Python 3.10+ with NumPy; direct script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# Calculate a small LCA foreground

**English** | [中文](SKILL_ZH.md)

Start with the [LCA method](../../../../methods/01_socioeconomic_natural_change/economic_model/life_cycle_assessment.md): state goal, functional unit, product-system boundary, region, time, allocation and impact category. `scripts/run_lca.py` demonstrates only a linear single-output foreground LCI and LCIA calculation. It is not a full ISO 14040 study, a licensed inventory database, or a registered run-tool adapter.

## Input and calculation

Supply five CSVs in one input directory:

| File | Columns | Meaning |
|---|---|---|
| `processes.csv` | `process,product,product_unit` | One unique reference product per process |
| `technosphere.csv` | `product,process,amount` | Positive reference output, nonpositive input; list every product/process pair |
| `demand.csv` | `product,amount` | Functional demand; list every product, using explicit zero where needed |
| `biosphere.csv` | `flow,process,amount_kg` | Nonnegative elementary flow per process scale; list every flow/process pair |
| `characterization.csv` | `impact_category,flow,factor,impact_unit` | One explicit factor per category and flow |

The script solves `T s = d`, computes `g = B s`, then sums characterized inventory `score_k = Σ_f CF[k,f] g[f]`. It rejects missing factors or matrix cells, duplicate identifiers, invalid sign conventions, ill-conditioned systems and negative process scales. It reports `process_scales.csv`, `inventory.csv`, `impacts.csv` and a hashed `summary.json`.

From the repository root, with NumPy installed, `AIRMOSAIC_ASSETS_DIR` set to an existing external asset root, and an unused output path:

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/lca-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/life-cycle-assessment/scripts/run_lca.py --input-dir assets/data/01_socioeconomic_natural_change/SyntheticLCA/v1 --out-dir $out
```

The [manifest-listed synthetic LCA](../../../../assets/data/01_socioeconomic_natural_change/SyntheticLCA/v1/processes.csv) demands one toy product unit, requires 0.5 kg toy material and yields 2 kg CO2e for its single `climate_change` indicator. Verify this against the output and [toy-manifest.json](../../../../assets/toy-manifest.json). The script cannot model co-products, recycling allocation, dynamic emissions, uncertainty distributions or multiple locations. For real datasets and broader LCIA, [Brightway](https://docs.brightway.dev/en/latest/) is an open-source scripting path; database access, method selection and scientific review remain separate. Keep research data and outputs under authorized external asset roots.

The public [Tiangong LCA skills](https://github.com/tiangong-lca/agent-skills) informed the separate inventory-review and calculation gates, while the [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents) informed boundary checks. Their runtime and datasets are not part of this script.
