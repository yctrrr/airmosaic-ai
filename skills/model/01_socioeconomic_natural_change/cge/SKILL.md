---
name: cge
description: Solve the bundled synthetic CGE tutorial, design or inspect a general equilibrium model, and reproduce a supplied model when its runtime is available; CHEER is the external GAMS example.
compatibility: "Python 3.10+ with NumPy/SciPy for the synthetic tutorial; external GAMS, solver, license and model data for CHEER; no registered AirMosaic tool"
metadata:
  version: "0.2.0"
---

# Design, inspect and reproduce a CGE model

**English** | [中文](SKILL_ZH.md)

Use this skill to solve a synthetic CGE tutorial, design a CGE model, inspect supplied source, or reproduce its benchmark and scenarios. Start with the [CGE method](../../../../methods/01_socioeconomic_natural_change/economic_model/cge/README.md) for the scientific logic. CHEER and CHEER-P remain external GAMS source examples. This skill has a direct Python script but no registered AirMosaic tool ID; it does not bundle CHEER code, GAMS, a solver license or a real SAM.

## Run the synthetic numerical model

The reviewed [Python script](scripts/run_toy_cge.py) reads a [manifest-listed synthetic SAM](../../../../assets/data/01_socioeconomic_natural_change/SyntheticCGE/v1/sam.csv), a scenario table and environmental satellite coefficients. It calibrates a closed-economy model with matching activity/commodity accounts, two factors, one household, fixed intermediate requirements, Cobb-Douglas value added and household demand. Cobb-Douglas substitution elasticity 1 is a **chosen assumption**, not estimated from the SAM. Wage is the numeraire. It checks a balanced SAM, reproduces the zero-shock benchmark, then solves a productivity scenario with changing prices, outputs and factor demands. The satellite emissions calculation is one-way and does not alter equilibrium.

From the repository root, in a Python 3.10+ environment with the dependencies in [requirements.txt](requirements.txt), set `AIRMOSAIC_ASSETS_DIR` to an existing **external** root and choose a fresh output directory:

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/cge-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/cge/scripts/run_toy_cge.py --input-dir assets/data/01_socioeconomic_natural_change/SyntheticCGE/v1 --out-dir $out
```

Inspect `calibration.csv`, `equilibrium.csv`, `summary.csv` and `validation.json`. The baseline must reproduce 100 units of output and price 1 in both sectors; the synthetic satellite total is 50 kg. In `food_productivity_reduction`, the food TFP multiplier is 0.9, food output is about 92.77 and its relative price about 1.08485. The script rejects unbalanced or unsupported SAM flows, incomplete scenarios, nonpositive TFP and existing or Git-contained destinations before writing results. Check the input hashes against [toy-manifest.json](../../../../assets/toy-manifest.json). This is numerical execution of **this tutorial**, not CHEER or a calibrated economy.

The [electricity technology split workbook](assets/cheer_clean_electricity_example/v1/benchmark.xlsx) is included with this skill and is read directly by the [accounting script](scripts/audit_cheer_electricity_split.py). Follow [CGE Model Extensions](references/model-extension-cases.md) for the command, input schema and output checks. This example checks benchmark technology accounts; it does not solve the full CHEER model. Workbook provenance and its separate dataset-license status are recorded in [source.json](assets/cheer_clean_electricity_example/v1/source.json).

## Set up a new model

Define the question, region and sector resolution, benchmark year, agents, goods, factors, trade and time structure. Obtain a documented social accounting matrix (SAM) and check row-column balance before calibration. State behavioral nests, tax and transfer treatment, market-clearing equations, price normalization, macro closure and elasticity sources. Implement those choices in an appropriate modeling language, calibrate the benchmark, and require a zero-shock solve that reproduces the SAM before interpreting a policy shock. Record which quantities are data, calibrated values, externally estimated parameters or scenario assumptions. Model design alone is not a numerical run.

## Establish the model actually supplied

1. Work from task-provided model source in an isolated working copy outside Git. Record its source URL or provenance, archive identity, version if stated, file list and base year. Do not substitute a current website description for the release actually supplied. Keep complete third-party source, original input databases and generated outputs outside Git; the technology-account example uses the included workbook.
2. Locate the active entry point and follow the modeling language's actual include and data references. For the reviewed CHEER-P demo, useful starting points are `run.gms`, `sets.gms`, `cal.gms`, `elasticities.gms`, `emission.gms`, `core.gms`, dynamic files and report files. Other CGE packages use different names and languages. Separate executable lines from comments and unused files.
3. Build a source map for region, sector, household, factor, resource and year sets; benchmark SAM/IO inputs; calibration and elasticity sources; production and consumption nests; market-clearing and pricing equations; closure; dynamic updates; scenario shocks; and report variables. Record units and definitions. The SAM contains monetary flows, so verify any conversion to physical quantities. Trace environmental variables separately: identify whether each is an output indicator, an input to an equilibrium equation, or an external-model exchange.

## Reproduce only when ready

4. Before execution, check the model-specific runtime, solver, license, included data and writable isolated output directory. For GAMS/MPSGE models, verify their versions and resolve relative paths and filename capitalization; the reviewed CHEER demo's lowercase default paths do not match all archive directory names exactly on case-sensitive systems. Run only the confirmed entry point in the isolated copy. `gams run.gms lo=2` is an example for an active GAMS `run.gms`, not a universal CGE command. Preserve the original files and save the exact command, log and generated reports.
5. Check the solver/model status and listing or equivalent diagnostics, then compare the solved benchmark with the source benchmark: SAM balance, market and budget residuals, sector and region totals, prices, quantities and units. A successful solve without benchmark agreement is not a verified reproduction. If a prerequisite is missing or baseline discrepancies remain unexplained, stop at source review and report the gap.

## Design and check an environmental application

6. Choose a clearly defined connection: a satellite account that calculates environmental indicators from solved activity; an endogenous constraint or response within the CGE equations; or a documented exchange with an external physical model. Trace the exact source equations and data before claiming that a model release implements the connection. For an extension, specify the physical-to-economic crosswalk, units, benchmark coefficients, changed parameter or constraint, timing and coverage. Examples include an energy or resource constraint, an environmental tax, a technology shift or a climate-related productivity change.
7. Solve a paired baseline and scenario under the same accounting definitions and closure. Check account and market balances and any environmental identity, then report activity, energy or resource use, prices, income and other requested outcomes by version, scenario, year, region and sector. Keep a one-way environmental indicator distinct from feedback. For an external model, document exchanged variables, crosswalks and whether coupling is one-pass or iterative. Check sensitivity to key elasticities, closures and environmental coefficients.

Report whether the work is **model design**, **source inspection**, **successful numerical reproduction**, or **scientifically checked scenario analysis**, with evidence for the level reached. The [CHEER downloads](https://cheer.org.cn/downloads/) and [GAMS MPSGE documentation](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html) are upstream references; neither verifies a particular local run.

The public [general-equilibrium model-builder skill](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md) informed the agent/endowment/market-clearing reasoning sequence. Its Julia code implements Cobb-Douglas pure exchange only. For production, SAM, dynamics and CHEER source edits, use the [example and extension guide](references/model-extension-cases.md) to identify the corresponding modules; a pure-exchange solve is not CHEER reproduction.
