---
name: gridded-gdp
description: Prepare annual predictors, pair-validate, train, predict and calibrate China's gridded GDP per capita.
compatibility: "R with terra, sf, exactextractr, data.table, Matrix, xgboost, jsonlite and digest; PowerShell 7 controller."
metadata:
  version: "0.1.0"
---

# Model annual gridded GDP per capita

**English** | [中文](SKILL_ZH.md)

Use the [GDP method](../../../../methods/01_socioeconomic_natural_change/gridded_gdp.md) and [workflow](../../../../workflows/gridded_gdp/README.md). The [direct R entry](scripts/run_gdp.R) supports `preflight`, `prepare`, `panel`, `validate`, `fit`, `grid` and `accept`. The [PowerShell wrapper](scripts/Invoke-GdpWorkflow.ps1) also exposes direct release operations. Use the workflow controller for fetching and staging annual inputs first.

The workflow accepts same-year light, total population and LCCS rasters, a fixed county map and licensed county/provincial statistics. Model refresh additionally uses the historical panel and original booster. Annual append loads a hash-verified accepted booster and its validation evidence. Inspect the candidate receipt, fold metrics and county and province closure before handing off the result. The direct scripts write outside Git. Authorized outputs contain restricted derived materials and remain inside the authorized workspace.

To stage an existing annual night-light crop, use [Set-GdpNightLight.ps1](scripts/Set-GdpNightLight.ps1) with the crop directory and an existing annual configuration row. For a short R walkthrough, the [synthetic fitting example](examples/fit_synthetic_panel.R) shows the feature matrix, log-GDP target, one forward-year comparison, full-panel fit and model reload. Follow the workflow for commands and the complete validation.

The original study/method citation is [Shao et al., JHM 2026](https://doi.org/10.1016/j.jhazmat.2026.142141), with [BibTeX](references/method_citation.bib). The method explains the subsequent 2021–2024 input update and 2000–2024 retraining/paired validation. Keep historical model generations explicit when describing a Zenodo package; redistribution permission is still required.
