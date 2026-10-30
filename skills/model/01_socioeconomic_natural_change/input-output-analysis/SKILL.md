---
name: input-output-analysis
description: Calculate and check a balanced, fixed-coefficient input-output table and a direct-intensity final-demand footprint from supplied CSVs.
compatibility: "Python 3.10+ with NumPy; direct script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# Calculate a small input-output account

**English** | [中文](SKILL_ZH.md)

Use the [IO method](../../../../methods/01_socioeconomic_natural_change/economic_model/io/README.md) to define sectors, boundary, price year and units. This skill runs the local `scripts/run_io.py` calculator for a complete, balanced table. It does not parse a published MRIO release, estimate coefficients, solve prices or substitute for [CGE](../cge/SKILL.md). There is no run-tool ID.

## Input and calculation

Supply an input directory with `sectors.csv` (`sector,output,final_demand,direct_emission_intensity`) and `transactions.csv` (`from_sector,to_sector,value`), including explicit zero entries for every sector pair. Transactions are monetary flows from row sector to column sector. `output` and `final_demand` use the same currency unit and price basis; the demonstration intensity is `kg_CO2/currency_unit`. The script checks `x = Z1 + y`, computes `A[i,j] = Z[i,j]/x[j]`, solves `(I-A)x = y`, then multiplies the solution by direct intensity to report direct emissions and footprints by final-demand sector. It fails on missing pairs, duplicate sectors, negative quantities, unbalanced accounts or an ill-conditioned solve.

From the repository root, with NumPy installed, `AIRMOSAIC_ASSETS_DIR` set to an existing external asset root, and a fresh destination outside Git:

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/io-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/input-output-analysis/scripts/run_io.py --input-dir assets/data/01_socioeconomic_natural_change/SyntheticIO/v1 --out-dir $out
```

The [manifest-listed synthetic input](../../../../assets/data/01_socioeconomic_natural_change/SyntheticIO/v1/sectors.csv) has two sectors. Expected `sector_output.csv` reproduces 100 units for each, and `summary.json` reports 30 kg CO2 for both direct total and final-demand footprint total. Inspect `coefficients.csv` and `final_demand_footprint.csv` as well. The script creates the destination exclusively; choose another fresh path for a repeat. Check the fixture hashes against [toy-manifest.json](../../../../assets/toy-manifest.json) before treating a run as the documented demo.

For a research table, first document supply-use transformation, sector and region concordance, imports, currency and deflator, final-demand coverage, and physical intensity source. Run only on task-authorized data, write project outputs under the external `AIRMOSAIC_ASSETS_DIR`, and check closure and sensitivity. For large MRIO data, [pymrio](https://pymrio.readthedocs.io/en/stable/) supplies parsers and accounts; installing it and obtaining an authorized MRIO database are separate steps. A successful toy solve does not validate a real footprint.

This skill takes its boundary and mass-balance review pattern from the publicly released [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents); the numerical implementation here is a separate, small IO illustration.
