# Existing legacy daily products

**English** | [中文](daily-product_ZH.md)

Use [`prepare_daily_product.py`](../scripts/prepare_daily_product.py) for an already loaded legacy daily table. This pure in-memory helper performs no file access, download, spatial matching or second aggregation. Load it with `importlib.util.spec_from_file_location`, then call:

```python
result = module.prepare_legacy_daily(
    table, station_ids=["001"], expected_dates=["2020-02-29"],
    min_source_rows=20,
    interpretation={
        "status": "user_accepted_assumptions", "timezone": "Asia/Shanghai",
        "date_label": "legacy_source_date", "coordinate_crs": "EPSG:4326",
        "historical_coordinate_validity": "unverified", "evidence": "review_reference",
    },
)
daily, quality = result["daily"], result["quality"]
```

Input columns are `date, station_code, type, value, count, Lon, Lat`. Exact `PM2.5` rows alone are selected; rolling means and AQI are excluded. IDs must be unique nonempty strings (at most 100); source PM2.5 station IDs must also be strings. Dates accept strict `YYYY-MM-DD`, `YYYYMMDD`, date objects or timezone-naive midnight datetime objects. Invalid selected-station source dates fail; valid dates outside the requested calendar are excluded. Requested dates must be nonempty and unique after normalization. Duplicate selected station/day records fail rather than being averaged. No source-identity verification follows from a table-shape assertion.

The output retains every requested station × date combination, in caller order. Columns are `station_id, date_local, pm25_daily_ug_m3, source_value, source_row_count, source_longitude, source_latitude, daily_status, daily_reasons`. Original values/counts/coordinates are preserved. The derived target is finite and nonnegative only when the source count is an integer between the explicit `min_source_rows` (1–24) and 24. Boolean targets/counts are invalid. Missing or invalid targets/counts leave the target NaN; no imputation occurs. Status is `accepted`, `invalid` or `missing`; `daily_reasons` is a tuple of reason codes. An absent source day has `missing_source_day`; invalid targets use `invalid_or_missing_target`; counts use `invalid_or_missing_source_row_count` or `insufficient_source_rows`.

Legacy `count` represents source-row `n()`, **not verified valid observed hours**. A threshold of 20 does not demonstrate a regulatory completeness rule. `accepted` means the engineering filter passed under user-accepted assumptions, not scientific acceptance. Local dates, EPSG:4326 and historical coordinates remain provisional; the helper preserves coordinates without validating them. Coordinate consistency and spatial eligibility require separate caller checks.

`quality` exposes the passed `interpretation` (deep copy), `use_scope=engineering_pilot_only`, `source_count_semantics=legacy_n_source_rows_not_verified_valid_hours`, false `station_identity_verified`/`metadata_verified` flags, the explicit threshold, requested IDs/dates, expected calendar size, selected source-row count, and status/reason counts. The required interpretation fields above are assertions accepted for an engineering pilot; a nonempty evidence reference is mandatory and does not itself verify metadata. This direct helper creates no tool registration or runner adapter.
