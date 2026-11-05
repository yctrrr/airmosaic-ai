# ERA5 local-day statistics

**English** | [中文](daily-statistics_ZH.md)

The [official daily product](https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics?tab=overview) computes statistics at retrieval time. For instantaneous meteorology, select `daily_mean`, `1_hourly` and `utc+08:00` explicitly. Accumulated variables require separate methods.

## Configure and acquire

The user accepts dataset terms and prepares official-client credentials. Never inspect or copy them. Keep the non-secret request in personal configuration; job records and downloads stay outside Git.

```json
{
  "product_type": "reanalysis",
  "variable": ["2m_temperature", "2m_dewpoint_temperature", "10m_u_component_of_wind", "10m_v_component_of_wind", "surface_pressure"],
  "year": "2020",
  "month": ["01"],
  "day": ["01"],
  "daily_statistic": "daily_mean",
  "frequency": "1_hourly",
  "time_zone": "utc+08:00",
  "area": [40, 115, 39, 117]
}
```

Review the region/date before use. Load [copernicus_jobs.py](../scripts/copernicus_jobs.py) as a Python module. Instantiate `CopernicusJobs(jobs_dir, cache_dir, max_total_bytes=..., max_package_bytes=...)` with task-specific caps. Call `operate(name, "derived-era5-single-levels-daily-statistics", request, mode="submit")` once, then query the saved job with `mode="status"` and download after success with `mode="download"`.

One serial controller owns the ledger. Unknown submission outcomes, unresolved partial files, changed requests and changed completed files require review. Failed payload reservations remain charged. Reuse queued requests. The helper retains ordinary proxy/TLS behavior and prevents netrc fallback on result downloads. This direct API has no registered CLI/MCP adapter or OS isolation.

## Decode and check

The five-variable [daily reader](../../../../model/shared/spatial_analysis/scripts/python/era5_daily.py) requires `xarray` and `netCDF4`. Load the linked module as `daily_reader`:

```python
result = daily_reader.read_era5_daily(
    package_path, ["2020-01-01"], area_nwse=[40, 115, 39, 117],
    temp_root=existing_private_temp_directory,
)
```

It checks the exact 0.25° grid, nominal local-date labels, units, available parameter attributes, dimensions, duplicate/missing variables and unpacking limits. Outputs include native axes, dates and `[day, latitude, longitude]` arrays. Missing cells remain missing; no unit conversion or independent full-hour verification is implied.

Before expanding a new daily workflow, compare selected dates/nodes with retained hourly inputs using the same local-day definition. Freeze identities, dates and tolerances first; bind the receipt to the exact plan, source hashes and validator. Retain the hourly small case for offline replay. Share monthly caches across runs instead of copying whole deliveries into each result.
