---
name: health-impact-analysis
description: Adapt PM2.5 health-impact calculation and visualization R templates to aligned concentration, population, baseline mortality and RR data. Use for method preparation and validation; no ready-to-run health model is registered.
---

# PM2.5 Health Impact Analysis

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


> Invocation status: `pm25_hia_calculate_template` and `pm25_hia_visualize_template` are catalogued R templates, disabled in `run-tool`. Input adaptation and independent scientific validation are required.

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md) and [execution guide](../../../../harness/usage/run-tool.md). Use separate, existing roots outside Git: `AIRMOSAIC_ASSETS_DIR` for data/results, `AIRMOSAIC_CONFIG_DIR` for non-secret settings and explicit task JSON, and `AIRMOSAIC_AUTH_DIR` for browser state; passwords/tokens stay in a credential manager. Do not read or share credential/profile contents. Run repository commands from the repository root with the installed project interpreter. Enabled adapters allocate `results/<project_id>/<run_id>/04_integrated_impacts/<tool_id>/` automatically; omit output parameters unless a task-specific override is needed. No personal configuration is auto-loaded. Raw scripts bypass runner checks, and the runner is not an OS sandbox.

## Purpose

Prepare a PM2.5-attributable mortality analysis using the Population Attributable Fraction (PAF) framework. This skill provides method references and adaptable calculation/visualization templates; it is not an executable end-to-end service.

## Methodology

### Core Formula

The health impact is calculated per grid cell using the standard PAF approach:

```
Attributable Deaths = Population x PAF Mortality Rate

PAF Mortality Rate = sum over (endpoint, sex, age):
    AgeStruc(age, sex) x BaselineMortRate(endpoint, sex, age) / 100,000 x PAF(conc, endpoint, age)

PAF(conc, endpoint, age) = (RR(conc, endpoint, age) - 1) / RR(conc, endpoint, age)
```

Where:
- **RR** = Relative Risk from concentration-response curve (GEMM-5COD or IER)
- **BaselineMortRate** = GBD cause-specific mortality rate per 100,000 population
- **AgeStruc** = fraction of population in each age-sex group
- **concentration** = annual mean PM2.5 (ug/m3), capped at the RR curve maximum

### Concentration-Response Curves

Two standard curves are supported:

| Curve | Full Name | Source | Endpoints |
|---|---|---|---|
| GEMM-5COD | Global Exposure Mortality Model, 5 Causes of Death | Burnett et al. (2018, 2022) | COPD, LC, LRI, IHD, Stroke |
| IER | Integrated Exposure-Response | GBD 2010/2013 | COPD, LC, LRI, IHD, Stroke |

RR values are stored in a lookup table with columns:
curve_name, endpoint, concentration, agegroup, RR

Concentrations are binned at 0.1 ug/m3 resolution. Values above the maximum curve concentration are capped.

### Age Group Handling

- Standard GBD 5-year age groups: 0, 5, 10, ..., 75, 80+
- Harmonizing an 80+ open-ended group with finer mortality ages requires explicit population denominators and a reviewed mapping. Inspect the template's age handling rather than accepting sums of rates or historical age IDs as a validated aggregation.

## Required Input Data

### 1. PM2.5 Concentration Grid
- Format: CSV with columns X_Lon, Y_Lat, concentration
- Resolution: analysis resolution (e.g., 0.1 degree)
- Unit: ug/m3 annual mean
- Source examples: TAP, satellite-derived (MODIS/MISR/SeaWiFS), chemical transport model output

### 2. Population Grid
- Format: RDS or CSV with columns X_Lon, Y_Lat, GridID, Year, urarea, Pop
- Resolution: must match concentration grid
- Source examples: WorldPop, GPW, LandScan

### 3. Age Structure Fractions
- Format: RDS or CSV with columns X_Lon, Y_Lat, GridID, Year, sex, agegroup, AgeStruc
- Each grid cell's age fractions must sum to 1 per sex
- Source: derived from WorldPop age-sex population products

### 4. Baseline Mortality Rates
- Format: CSV with columns location_name, Year, metric, endpoint, sex, agegroup, MortRate
- Unit: deaths per 100,000 population
- Source: GBD Results (IHME), national or subnational

### 5. RR Curve Lookup Table
- Format: CSV with columns curve_name, endpoint, concentration, agegroup, RR
- Concentration values as character (rounded to 0.1 for matching)
- Verify RR = 1 at the lookup table's documented reference concentration; do not assume zero as a universal curve threshold.

## Output

### Grid-Level Results
pm25_premature_death_grid_{curve}_{year}.csv

| Column | Description |
|---|---|
| X_Lon, Y_Lat | Grid centroid coordinates |
| GridID | Unique grid identifier |
| Year | Data year |
| urarea | Urban/rural/overall classification |
| Pop | Population count |
| curve_name | RR curve used |
| concentration | PM2.5 concentration (ug/m3) |
| MortRate_PM25 | PAF-attributable mortality rate |
| Mort | Attributable premature deaths |

### Summary Statistics
pm25_premature_death_summary_{curve}_{year}.csv

Aggregated by Year, curve_name, urarea:
- Total population, total deaths, population-weighted mean concentration

### Visualization
- Grid map of Mort values, binned: <1, 1-5, 5-10, 10-25, 25-50, 50-75, 75-100, 100-150, >150
- Spectral color palette (reversed), units: deaths per grid cell
- China boundary overlay with South China Sea inset

## Manual adaptation and scientific boundary

Query `pm25_hia_calculate_template` and `pm25_hia_visualize_template` with `describe-tool` for their real locations and requirements. Both are templates disabled in `run-tool`; there is no ready-to-run health-impact service.

Copy the needed template to a new local task directory, then adapt the concentration grid, population/age denominators, baseline mortality, RR curves, years, sex/age mappings, missing values and all output paths. Sourcing these R files executes work; it is not a safe help/discovery action. Current hardcoded assumptions, including mortality-year selection and age harmonization, need domain review. Validate simple cases and group totals before a real analysis; a template's presence or exit code proves neither epidemiological validity nor scientific acceptance. See the [model guide](../../../../harness/usage/model-analysis.md) for exact environment names and checkpoints.

## Explicit template configuration

There is no automatic YAML/config-file loader. Set the variables read by the adapted R task explicitly: `PM25_HIA_CONC_DIR`, `PM25_HIA_POP_DIR`, `PM25_HIA_MORT_FILE`, `PM25_HIA_RR_FILE`, `PM25_HIA_OUTPUT_DIR`, `PM25_HIA_YEARS`, `PM25_HIA_CURVE`. Visualization additionally uses `PM25_HIA_POP_FILE` and `PM25_HIA_SHP_DIR`. Use new task outputs outside Git, preserve originals, and sanitize any standalone logs before sharing.

## References

- references/methodology.md: Full PAF derivation, GEMM vs IER comparison, uncertainty considerations
- references/data_requirements.md: Detailed data specifications, expected schemas, preprocessing notes

## Templates

- templates/calculate_pm25_deaths.R: Generalized grid-level PAF death calculation
- templates/visualize_pm25_deaths.R: Generalized mortality map generation

## Examples

- examples/workflow_pm25_hia.R: End-to-end example from data loading through visualization

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
