# Annual gridded GDP workflow

**English** | [中文](README_ZH.md)

Combine the [public-data skill](../../skills/data_acquisition/shared/public-data/SKILL.md) and [GDP skill](../../skills/model/01_socioeconomic_natural_change/gridded-gdp/SKILL.md). The [method](../../methods/01_socioeconomic_natural_change/gridded_gdp.md) owns scientific definitions. This dedicated PowerShell controller runs the listed scripts directly; it has no run-tool/MCP adapter or general workflow engine.

## Run a synthetic case

Use PowerShell 7, curl, R, and R packages `terra, sf, exactextractr, data.table, Matrix, xgboost, jsonlite, digest`. Install into a user-selected R library if missing, then set `R_LIBS_USER`. The controller does not install packages.

```powershell
$run = Join-Path $env:TEMP ("airmosaic-gdp-" + [guid]::NewGuid().ToString('N'))
& ./workflows/gridded_gdp/Invoke-GriddedGdp.ps1 -RunDirectory $run -Mode synthetic -Append
& ./workflows/gridded_gdp/Invoke-GriddedGdp.ps1 -RunDirectory $run -Mode synthetic -Append -Resume
```

The example invents eight counties in two provinces, historical observations and three annual rasters. It packages the light TIFFs with synthetic Dataverse metadata, then runs the same archive checksum, extraction and crop scripts. Twelve-round toy models exercise prediction and calibration. The second candidate adds 2023 using the first accepted model without another fit. Synthetic validation records comparisons but disables the improvement gate. These results establish engineering behavior, not national prediction accuracy.

To read and run the model fit directly in R after the synthetic run, select a fresh output directory outside Git and outside the run. The [example](../../skills/model/01_socioeconomic_natural_change/gridded-gdp/examples/fit_synthetic_panel.R) reads the completed county-year panel, fits one forward-year comparison, and saves and reloads a full-panel booster. It writes predictions, metrics and a fit summary.

```powershell
$modelExample = './skills/model/01_socioeconomic_natural_change/gridded-gdp/examples/fit_synthetic_panel.R'
$modelOutput = "$run-r-model"
Rscript --vanilla $modelExample (Join-Path $run 'resolved-initial.json') $modelOutput
```

## Prepare a real project

Copy [workflow.json](examples/workflow.json) to a private configuration directory outside Git and replace its roots, paths and hashes. It demonstrates a 2021 update of a 2000–2020 model. Extend all annual entries and year lists together for subsequent years. Retain the original project's grid and boundary when updating existing products. Review the illustrative acceptance tolerances before starting; do not select tolerances or parameters using final evaluation results.

| Input | Intake contract |
|---|---|
| County boundary | Self-contained sf RDS or single-layer GeoPackage. Use unique six-character `PAC`, `Province_code`, valid polygons, declared CRS and 31 mainland provincial codes. Historical centroids must match. |
| Historical panel | CSV with `PAC, Province_code, observed_gdp` and the nine features below. Positive observed targets only; original 2000–2020 feature definitions and county keys. |
| Original booster | Compatible XGBoost JSON; used as the forward-year baseline. It must have been trained only through the historical cutoff with the same feature order and log target. |
| County GDP | Authorized CSMAR CRE_Cmect CSV: `Sgnyea, Prvcnm_id, Ctnm_id, Cmect07`. Nonpositive/missing targets are excluded from training and filled only during county inference. Duplicate keys stop intake. |
| Province GDP | Authorized CRE_Gdp01 CSV: `Sgnyea, Prvcnm_id, Gdp0116`; complete positive same-year province targets. |
| Night lights | Same-year harmonized NPP-VIIRS-like Version 2. A Dataverse provider specification triggers retrieval and native-grid crop; a staged TIFF needs year, product, version and SHA-256. |
| Population | Same-year LandScan Global 30 arcsecond total counts, staged locally with source metadata and SHA-256. The workflow does not automate the ORNL portal or substitute Mosaic/WorldPop. |
| Land cover | C3S v2.1.1; NetCDF `lccs_class` with embedded year, or a verified conversion with a matching annual manifest. A CDS specification uses the official client and the request template. |

The feature order is `Agriculture_grid, Forest_grid, Grassland_grid, NTL_Pop, Urban_grid, Wetland_grid, Year, cenlat, cenlon`. The five fractions use all valid classified pixels as denominator. County land-cover features use the original nominal 0.1° grid. It preserves the fine grid extent and rounds row and column counts. Coordinates use the historical county centroids and rounded grid centers. All GDP targets use current-price CNY/person.

[cds-request.json](../../skills/model/01_socioeconomic_natural_change/gridded-gdp/examples/cds-request.json) is an editable official-request example. Check the current CDS form, accept its terms and configure the existing official client outside Git. The land-cover helper saves the request ID before subsequent status/download calls. Pending jobs stop this attempt; resume the same run later. Unknown submission outcomes and partial payloads require review. TLS verification remains enabled. This route has synthetic request-reuse tests; a live CDS retrieval is not part of the delivered synthetic acceptance.

CSMAR uses the [authorized acquisition skill](../../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md). Stage its exports yourself through that route. The controller checks required local inputs before model work and never inspects browser sessions or credential files.

### Reuse an existing night-light crop

Follow the [public-data skill](../../skills/data_acquisition/shared/public-data/SKILL.md) to query Dataverse, download the annual archive and crop it in R. Use the bounds in `geo.extent` in west, east, south, north order. For an existing crop, set `$cropDirectory` to the folder containing `crop.tif` and `source.json`. The private config needs an `annual` row for the selected year. Set `$localConfigFile` to a new file path in an existing external directory.

```powershell
$gdp = './skills/model/01_socioeconomic_natural_change/gridded-gdp/scripts'
$localConfig = & "$gdp/Set-GdpNightLight.ps1" -Config $privateConfig -Year 2025 -CropDirectory $cropDirectory -OutputConfig $localConfigFile
```

The helper checks the product, year and coverage. It writes a new configuration with just `annual.2025.light` replaced. Population, land cover and county/province targets still need to be present for the selected years. To let the controller acquire light instead, set the light row to `{"provider":"dataverse","year":2025,"version":"10.1"}` in the private config and set `$localConfig = $privateConfig`. Once inputs are ready, pass the resulting configuration to the controller.

```powershell
& ./workflows/gridded_gdp/Invoke-GriddedGdp.ps1 -RunDirectory $freshExternalRun -Mode authorized -Config $localConfig
```

## Stages and retained implementation

| Stage | Implementation | Main evidence |
|---|---|---|
| Catalog, retrieve, crop | public-data `Get-DataverseRaster.ps1`, `crop_annual_raster.R`; GDP `Get-CdsLandCover.ps1` | Original archive, provider checksum, TIFF SHA-256, native-grid pixel comparison, annual source manifest |
| Prepare | `gdp_spatial.R`, `grid_overlap_sum.R` via `run_gdp.R prepare` | County features, aligned grid predictors, population-conservation receipt |
| Panel and paired validation | `run_gdp.R panel/validate`, `gdp_common.R` | Observed county-year panel; same-county holdout and forward-year predictions before calibration |
| Fit and reload | `run_gdp.R fit`, `config/model.json` | Frozen 4,403-round recipe, full training counts, saved/reloaded booster agreement |
| Predict and calibrate | `run_gdp.R grid` | Province factors, county targets, county factors and three-band 0.01° GeoTIFF |
| Independent readback | `run_gdp.R accept` | Reopened GeoTIFF geometry, NoData/positivity, county population conservation against the aligned input, province closure, county GDP p95/max errors |
| Optional local release | `publish_gdp.R` | Dry-run payload, verified backups, publication journal and rollback |

From the repository root, a resolved private config can also call a single stage:

```powershell
$gdp = './skills/model/01_socioeconomic_natural_change/gridded-gdp/scripts'
Rscript --vanilla "$gdp/run_gdp.R" $resolvedConfig preflight
Rscript --vanilla "$gdp/run_gdp.R" $resolvedConfig validate
Rscript --vanilla "$gdp/run_gdp.R" $resolvedConfig accept
```

A later stage resolves dependencies first. Immutable checkpoints hash inputs, configuration, code and relevant runtime versions; reuse checks the full file inventory and hashes. Do not edit completed checkpoints. Keep failed attempts for diagnosis and start a new run when code/design changes. `-Resume` requires the original code and request identity. The controller records stage-boundary events and status, not every inner R operation or the agent's complete generation history.

## Annual append and local publication

For a new year, set `accepted_model` to the prior accepted candidate ID, `accepted_model_root` to its external candidates directory and `accepted_receipt_sha256` to the verified receipt hash. Keep its training years, feature contract, boundary and geometry. Set `output_years` to later years and provide their complete annual and county/province inputs. The controller reuses the accepted booster and paired metrics; it skips panel construction, validation fitting and full retraining. A new model refresh instead omits `accepted_model` and runs the paired gate before fitting.

Candidates are under `work/candidates/<id>/` with `receipt.json, grid_acceptance.csv, validation_metrics.csv` and original-style output folders:

- `Grid_interpolate_0.01g/Grid_XGBoost_GDP_pc_0.01g_<year>.tif`: `GDP_pc, Pop_all, factor2`.
- `Grid_interpolate_0.01g/Grid_to_county_XGBoost_GDP_pc_<year>.csv`.
- `County_interpolate/County_XGBoost_GDP_pc_<year>.csv` and `Province_GDP_pc_calibration_<year>.csv`.
- `County_interpolate/Xgboost_GDP_model_<first>-<last>.json`.

The annual county tables do not replace the project's historical combined table. Existing yearly products stay untouched until a separately selected local release operation:

```powershell
Rscript --vanilla "$gdp/publish_gdp.R" $resolvedConfig $candidate 'reviewed-release' plan
Rscript --vanilla "$gdp/publish_gdp.R" $resolvedConfig $candidate 'reviewed-release' publish
Rscript --vanilla "$gdp/publish_gdp.R" $resolvedConfig $candidate 'reviewed-release' rollback
```

Select a separate external `release_root`. The publisher backs up changed files, journals the transaction before replacing payloads and verifies readback. A release is complete only when its transaction's `complete.json` says `published`; rollback changes it to `rolled_back`. Interrupted multi-file publication may need rollback. Consumers must avoid reading during publication. This is local file promotion, not public repository publication.

## Interpretation and remaining inputs

`validation_metrics.csv` reports log RMSE, log R², median absolute percentage error **as a fraction** (multiply by 100 for percent), sample count and distinct counties, for each year and pooled rows (`test_year=0`). The production improvement gate requires lower pooled log RMSE and median APE in both validation domains. It does not tune the model. Post-calibration county closure measures numerical consistency; it does not establish pixel accuracy.

For the transferred project, 2025 same-product annual population and nationwide same-definition county GDP were still missing at handoff. Recheck availability before a real update; the present workflow has not filled those gaps or rerun formal national GDP results. Source rights, boundary provenance and historical-feature definitions also require project review. Authorized tables, calibration factors, trained weights and resulting grids stay private until their redistribution rights are established.

Cite the original paper and the eventual versioned dataset DOI separately. The subsequent update adds 2021–2024 inputs, 2000–2024 retraining and paired validation. Historical 2000–2020 grids retain their original model generation. The proposed Zenodo package uses one `grids_2000-2024.zip`, preserves each year's extent and records the model generation. Redistribution rights for CSMAR-derived outputs remain to be established. [Shao et al., Journal of Hazardous Materials 510 (2026), 142141](https://doi.org/10.1016/j.jhazmat.2026.142141)
