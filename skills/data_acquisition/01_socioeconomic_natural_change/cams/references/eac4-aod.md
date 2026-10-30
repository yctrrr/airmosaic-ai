# EAC4 total AOD at 550 nm

**English** | [中文](eac4-aod_ZH.md)

Use the [CAMS method](../../../../../methods/01_socioeconomic_natural_change/cams.md) for source identity and uncertainty. The public ADS catalogue/form was checked on 2026-10-30: dataset `cams-global-reanalysis-eac4` exposes the exact request value `total_aerosol_optical_depth_550nm`. This is column-integrated, dimensionless AOD, not ground PM2.5, an ERA5 variable or an unprocessed satellite retrieval. The ERA5 single-level form checked the same day had 262 selectable variables and no AOD option. No authenticated request or AOD download was performed in this check.

## Request and verify

1. Choose the date, UTC samples, bounding box and fresh project output. The [request example](../../../../../config/examples/copernicus/cams-eac4-aod.request.json) is one UTC field for a small area, not a Chinese annual or daily product. It needs no model-level-60 selection because this variable is a column quantity.
2. Use the [official-client operation](../../era5/references/operations.md), selecting `cams-eac4-aod`, or select this variable in the [ADS form](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=download). Keep the request in a new personal configuration file; preserve other ERA5/ADS settings. The official client may internally use the user's authorized credentials; do not inspect or log them.
3. Decode the downloaded GRIB and confirm the AOD parameter identity, wavelength, dimensionless unit, actual grid, UTC valid times, finite values and missingness. Do not apply the PM2.5 kg/m³ conversion, set a universal upper cutoff of one or count a nonempty file as content acceptance. Do not promise parameter-ID checks from the earlier PM2.5 example apply to AOD.
4. For daily research, use the verified local-day window and native 3-hourly samples. Report the mean of the expected eight samples explicitly as a sampled daily covariate, with missing samples retained. The PM2.5 20-hour rule does not apply. The one-field request does not validate aggregation.
5. Match coordinates/times and record bilinear weights, masks and input-grid identity in a reviewed spatial implementation. Native output is 0.75°; interpolation to a finer grid does not create finer independent information. A common prediction grid must be declared separately from the source grids.

Authentication, path handling and interruption/retry rules remain those of the parent skill. There is no EAC4 AOD runner adapter, automatic aggregation or verified station/grid inference pipeline. Real-data decoding and spatial tests remain pending.

Primary metadata: [EAC4 catalogue](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=overview), [ERA5 single-level catalogue](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview).
