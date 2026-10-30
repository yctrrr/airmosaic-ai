# Health-template input contract

**English** | [中文](data_requirements_ZH.md)

This page describes fields expected by the existing templates. Scientific selection and interpretation belong to the [health method](../../../../../methods/04_integrated_impacts/health_impacts.md); [operations](operations.md) explains configuration and adaptations.

## Concentration

Required fields: `X_Lon`, `Y_Lat`, `concentration`. The template expects annual mean PM2.5 in ug/m3 at the selected grid centroids. Describe the averaging/coverage rule, year and source product.

Choose spatial aggregation for the exposure represented: an area mean and a population-weighted mean answer different questions. Keep the method explicit when changing resolution. The template's concentration rounding and hard cap at 200 are implementation assumptions requiring review against the selected curve domain.

## Population

Required fields: `X_Lon`, `Y_Lat`, `GridID`, `Year`, `urarea`, `Pop`. `Pop` is a population count; `urarea` distinguishes overall/urban/rural categories used by the task. Preserve counts when regridding, verify the census/product basis and avoid summing overlapping overall and subgroup populations.

WorldPop, GPW and LandScan are possible product families, with different support and population concepts. Select a release and definition explicitly rather than treating these sources as interchangeable.

## Age-sex fractions

Required fields: `X_Lon`, `Y_Lat`, `GridID`, `Year`, `sex`, `agegroup`, `AgeStruc`. The template uses male/female labels and age-group lower bounds, ending in an open 80+ band.

Declare the denominator. Joint age-sex fractions sum to one across all age-sex groups when multiplied by total population. Within-sex fractions require sex-specific population and adapted multiplication. Inspect the original age-band metadata; if infant and ages 1–4 counts are separate, merge their non-overlapping counts before deriving a 0–4 fraction.

## Baseline mortality

Required fields: `location_name`, `Year`, `metric`, `endpoint`, `sex`, `agegroup`, `MortRate`. `MortRate` represents deaths per 100,000 matched population, with `metric=Rate`. The template's endpoint labels are `copd`, `lc`, `lri`, `ihd`, `stroke`; eligibility follows the selected response model.

Filter the original source year/location and metric before joining. A missing target year requires a documented substitution/interpolation scenario and sensitivity review, not an automatic nearest-year default. The current template rewrites mortality year, so task-copy adaptation must preserve and verify the original source year.

Do not sum age-specific rates to obtain an 80+ rate. Aggregate matched age-specific deaths and population, then divide to obtain the combined rate. Equivalently, use the matched population-weighted rate. If risk functions differ by fine age, calculate age-specific attributable deaths first and sum counts. The current template's rate summation needs adaptation.

## Relative-risk lookup

Required fields: `curve_name`, `endpoint`, `concentration`, `agegroup`, `RR`. Preserve the exact curve version, eligible endpoints/ages, reference exposure and supported concentration range. RR equals one at that curve's reference exposure; zero exposure is not a universal reference.

The template matches rounded concentration strings on a 0.1 grid. Normalize string formatting and review rounding, interpolation and out-of-range behavior in the adapted task. Do not assume a single adult-age row covers all baseline ages, and do not treat a missing join as RR=1 or zero burden.

## Alignment and checks

Concentration, population and age fractions need compatible spatial/temporal support. Mortality and risk tables join on their appropriate location, period, endpoint, sex, age and exposure definitions; they do not require a physical raster resolution themselves.

Check unique join keys, unmatched cells/groups, nonnegative populations, fraction denominators, rate units and curve support. Preserve excluded population and missing inputs in the quality report. Validate a small synthetic hand calculation and the equality of grid/summary totals after adaptation; see [operations](operations.md).

## Source parameter records are not RR lookup tables

The [ER source contract](exposure_response.md) adds an external coefficient/provenance layer. A coefficient per increment is not a `concentration, RR` curve. Require an explicit task reference, age/sex/endpoint mapping, concentration support, and uncertainty branch before generating a task-specific lookup. Current WHO adult natural-cause coefficients do not match the template's five-cause baseline by renaming endpoints. GEMM cell extracts with ambiguous headers/ages must stop normalization. Preserve an exact expected endpoint/age set and reject missing members; the template's intersection is insufficient.
