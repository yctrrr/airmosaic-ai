# ERA5: choosing and interpreting meteorological reanalysis

**English** | [中文](era5_ZH.md)

ERA5 supports meteorological background, research covariates and large-scale input fields. Choose variables by physical meaning, spatial/time support and uncertainty before aggregation or matching. Acquisition steps belong in the [ERA5 skill](../../skills/data_acquisition/01_socioeconomic_natural_change/era5/SKILL.md).

## Source and product identity

ERA5 is produced by ECMWF for the Copernicus Climate Change Service. The IFS model and data assimilation combine historical observations; CDS is the distribution channel. It is neither raw station data nor simple interpolation of ground observations. Individual fields may originate from analysis or forecast steps. See the [official data documentation](https://confluence.ecmwf.int/pages/viewpage.action?pageId=414588701).

Retain dataset ID, single/pressure/other levels, parameter identity, grid, times and release. ERA5, ERA5-Land and daily-statistics products are distinct. A finer export grid does not create independent information or establish effective resolving power.

## Uncertainty

| Source | Implication for research |
|---|---|
| Observation errors and changing coverage | Assimilation constraints differ by region, period and variable; examine discontinuities and known issues in long records |
| Model physics and assimilation | Systematic biases remain; compare suitable variables with independent observations in the study region |
| Grid representativeness | Terrain, coastlines and local processes differ from station support; record interpolation, distance, elevation and mask choices |
| Sampling and processing | UTC/local days, accumulation windows, regridding and missing steps can change statistics; convert according to each variable's meaning |

The [official uncertainty guidance](https://confluence.ecmwf.int/pages/viewpage.action?pageId=111158485) describes EDA spread as relative uncertainty information with incomplete representation of systematic errors. Do not treat it as a calibrated error bar for every field or assume one error percentage for all variables.

## Constructing comparable variables

1. Preserve original units, levels, UTC times, coordinates, missing flags and preliminary/final release status. Record updates such as ERA5T explicitly.
2. Convert by quantity: temperature can change from K to °C; precipitation requires distinguishing depth, accumulation and rate first. Retain originals and formulas.
3. Identify instantaneous, averaged and accumulated time support. Check accumulation start/reset and forecast steps; do not difference every accumulation field automatically.
4. Form unique variable/level/time/grid keys; inspect duplicates, missing times, longitude conventions, latitude order and masks.
5. Define UTC or local-day windows and expected sampling. Choose means, totals, extremes or time weights by quantity. State incomplete-sampling rules and sensitivity; the PM2.5 station 20-hour rule is not a meteorological-product rule.
6. For station or model comparisons, specify spatial extraction and time alignment. Surface fields do not replace vertical profiles; ERA5 files require separate model-input adaptation.
7. Report transformations, valid samples, grid changes, missingness and release versions. Fit bias correction or feature scaling only on training periods when used in prediction.

A single UTC field cannot establish a daily statistic. Independent observation comparison is needed to assess local scientific suitability.

## AOD is a separate product choice

The ERA5 single-level catalogue form checked on 2026-10-30 had no aerosol optical-depth option. Use ERA5 for the declared meteorological variables; an AOD covariate requires its actual separate product identity, for example [CAMS EAC4](cams.md). Access through a related provider does not make the products interchangeable. See the [AOD operation](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/eac4-aod.md); only public catalogue metadata was checked, not a new data download.
