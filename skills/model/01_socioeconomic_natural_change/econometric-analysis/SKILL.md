---
name: econometric-analysis
description: Choose an estimand and identification strategy for applied econometrics, then run a bounded cross-sectional OLS illustration on supplied CSV data when appropriate.
compatibility: "Python 3.10+ with NumPy; direct OLS script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# Design an econometric analysis

**English** | [中文](SKILL_ZH.md)

Start with the [econometrics method](../../../../methods/01_socioeconomic_natural_change/economic_model/econometrics/README.md). Record the target population, observation unit, outcome, exposure or treatment, time horizon and desired estimand. Distinguish description, prediction, causal inference and structural estimation. For a causal question, state the confounding paths and the source of identifying variation before choosing a method. A coefficient from the included OLS script is a conditional association unless an external research design justifies a stronger interpretation.

## Choose the route

- **Simple cross-sectional association:** use `scripts/run_ols.py` with an explicit outcome and predictor list, after checking variable units, sample construction and data support. The script includes an intercept and reports classical and HC1 standard errors, fitted values and diagnostics. These standard errors assume independent observations; use another implementation for clustered, panel or time-series data.
- **Policy effect or another causal estimand:** specify treatment assignment, comparison, timing, interference and assumptions. Select a reviewed DiD, IV, RDD, panel or other implementation only after the design is defensible. This skill has no such estimator or automatic causal inference.
- **Prediction:** define a held-out validation design and leakage controls; use a predictive modeling workflow. **Structural analysis:** specify behavior, calibration or estimation targets and counterfactuals explicitly, and use an appropriate model implementation.

## Run the small OLS illustration

The CSV requires one nonempty unique `unit_id`, a numeric outcome and numeric predictors for each cross-sectional row; missing and nonfinite values fail. Duplicate header names, insufficient observations, rank deficiency, severe conditioning and zero outcome variation also fail. The provided manifest-listed toy CSV uses `unit_id,y,x1,x2`. From the repository root with NumPy installed and `AIRMOSAIC_ASSETS_DIR` set to an existing external asset root, choose a fresh output directory outside Git:

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/ols-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/econometric-analysis/scripts/run_ols.py --input assets/data/01_socioeconomic_natural_change/SyntheticEconometrics/v1/rows.csv --outcome y --predictors x1 x2 --out-dir $out
```

Inspect `coefficients.csv`, `fitted.csv` and `summary.json`, including input SHA256 and the standard-error scope. Compare its hash with [toy-manifest.json](../../../../assets/toy-manifest.json). The toy data were designed with an approximate intercept of 2, `x1` slope of 3 and `x2` slope of 1; do not interpret those as scientific parameters. The destination is created exclusively, so use a new path for another run. Real-data runs need a task-authorized input, an external results path, a sample/variable provenance record and a method-specific review of identification and inference. The script is a direct helper, with no run-tool ID or automatic registration.

## Public skill precedents

This workflow adapts the identification-first routing and reproducibility separation in [EconAgentSkills](https://github.com/JonasWeinert/EconAgentSkills) and the outcome/treatment/confounding/variation checklist in the publicly released [econometrics-skill](https://github.com/xiaomihu1992/econometrics-skill/blob/main/SKILL.md). It does not copy their estimator libraries. Review an external skill's implementation and defaults before applying it to research data; [fixest](https://lrberge.github.io/fixest/reference/feols.html) is an alternative official implementation for selected panel estimators.
