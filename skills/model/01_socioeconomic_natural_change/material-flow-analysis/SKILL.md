---
name: material-flow-analysis
description: Check an explicitly classified economy-boundary material balance and calculate direct material consumption from supplied physical-flow CSVs.
compatibility: "Python 3.10+ standard library; direct script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# Calculate a material balance

**English** | [中文](SKILL_ZH.md)

Use the [MFA method](../../../../methods/01_socioeconomic_natural_change/economic_model/material_flow_analysis.md) to define the material, boundary, stock and year before assigning any flow. `scripts/run_mfa.py` is a small economy-boundary account, not a general process-network or dynamic-stock model. No run-tool ID is registered.

## Input and calculation

Provide `flows.csv` with `year,material,flow_type,amount_t`. For each year and material, list exactly one nonnegative-tonne row for each of `extraction`, `import`, `export`, `environment_output`, `stock_addition`, `balancing_input`, `balancing_output`; use explicit zero rows. The script calculates `DMC = extraction + import - export` and `residual = extraction + import + balancing_input - export - environment_output - stock_addition - balancing_output`. A balancing item represents a documented physical-account adjustment; do not insert one solely to hide an unexplained residual.

From the repository root, with `AIRMOSAIC_ASSETS_DIR` set to an existing external asset root and a fresh output directory:

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/mfa-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/material-flow-analysis/scripts/run_mfa.py --input assets/data/01_socioeconomic_natural_change/SyntheticMFA/v1/flows.csv --out-dir $out --require-balanced
```

The [manifest-listed synthetic flow](../../../../assets/data/01_socioeconomic_natural_change/SyntheticMFA/v1/flows.csv) yields DMC 9 tonnes and zero residual. Inspect `balances.csv` and `summary.json`. Without `--require-balanced`, the script reports an open residual instead of inventing a missing flow; with it, an imbalance stops before output creation. It rejects missing classes, duplicates and negative or nonfinite amounts. The output path must not already exist or be inside the checkout; verify the input hash in [toy-manifest.json](../../../../assets/toy-manifest.json).

For measured systems, trace sources and destinations, distinguish internal recycling from boundary flows, and keep material composition and residence/territory definitions consistent. Report remaining imbalance. [flodym](https://flodym.readthedocs.io/en/latest/) is a separate open-source path for multidimensional flows and dynamic stocks; this small script does not implement its stock-cohort models. Research inputs and outputs stay in authorized external asset locations.

The publicly released [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents) informed the system-boundary and mass-balance checklist; the local script uses its own explicit balance schema.
