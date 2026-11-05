# Direct hourly extraction and daily preparation

**English** | [中文](hourly-preparation_ZH.md)

Use `scripts/prepare_hourly.py` for selected local station extraction and explicitly reviewed hourly-to-daily computation. It requires Python, pandas and NumPy in the project environment. It has no downloader, CLI, tool ID or `run-tool` adapter. Direct calls do not inherit runner path checks, receipts or environment isolation. Routine documentation checks use synthetic inputs; actual data use requires the bounded study scope.

## Load and check the helper without real data

Run from the repository root. This offline example defines synthetic **start-labelled** intervals; its time declaration does not describe Quotsoft.

```python
from pathlib import Path
import importlib.util
import pandas as pd

helper = Path("skills/data_acquisition/03_atmospheric_transport/pm25-stations/scripts/prepare_hourly.py")
spec = importlib.util.spec_from_file_location("pm25_prepare", helper)
assert spec is not None and spec.loader is not None
pm25 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm25)

synthetic = pd.DataFrame({
    "station_id": ["SYN001"] * 24,
    "date_raw": ["20240101"] * 24,
    "hour_raw": [str(h) for h in range(24)],
    "value_raw": ["10"] * 20 + [""] * 4,
})
synthetic_time = {
    "status": "reviewed", "timezone": "Asia/Shanghai", "hour_label": "start",
    "evidence": "Synthetic fixture definition: local start-labelled hours 0..23; not source evidence",
}
qc, daily = pm25.prepare_daily(synthetic, synthetic_time, min_hours=20)
assert len(qc) == 24 and len(daily) == 1
assert daily.iloc[0]["n_valid_hours"] == 20
assert daily.iloc[0]["pm25_mean"] == 10
assert daily.iloc[0]["daily_status"] == "complete"
```

## Project configuration and local extraction

Use explicit local paths selected for the study. The helper does not discover private directories or automatically load this configuration. Keep non-secret configuration under `${AIRMOSAIC_CONFIG_DIR}/projects/<project_id>/`; keep private inputs, code/settings, results and review evidence with the external project's `results/`, following the [project guide](../../../../../projects/README.md). Retain original bytes and acquisition URL/time/version/license/hash separately. Asset admission requires a human scientific decision; this example neither promotes data nor prescribes asset subdirectories.

The following configuration is a template. Replace the paths with the authorized project paths, and obtain actual station IDs from the selected file header. `1001A` illustrates string selection, not historical coordinate validity.

```python
config = {
    "source_csv": "/path/to/external/projects/0001_study/results/run/raw/china_sites_20240101.csv",
    "output_dir": "/path/to/external/projects/0001_study/results/run/processed",
    "station_ids": ["1001A"],
    "expected_date": "20240101",
    "min_hours": 20,
    "missing_tokens": [""],
    "time_reference": {
        "status": "unreviewed", "timezone": None, "hour_label": None, "evidence": "",
    },
}
selected = pm25.extract_quotsoft_hourly(
    config["source_csv"], config["station_ids"], expected_date=config["expected_date"]
)
assert list(selected.columns) == ["station_id", "date_raw", "hour_raw", "value_raw"]
assert set(selected["station_id"]) == set(config["station_ids"])
assert selected["date_raw"].eq(config["expected_date"]).all()
assert not selected.duplicated(["station_id", "date_raw", "hour_raw"]).any()
coverage = selected.groupby("station_id")["hour_raw"].agg(["count", "nunique"])
print(coverage)  # Structural coverage only; not valid-hour completeness.
out = Path(config["output_dir"])
out.mkdir(parents=True, exist_ok=True)
selected.to_csv(out / "pm25_hourly_selected.csv", index=False, mode="x")
```

`extract_quotsoft_hourly(source, station_ids, expected_date=None)` accepts 1–100 distinct nonempty string station IDs. It checks required/duplicate headers and malformed rows, checks `expected_date` on every source row when provided, and selects exactly `type == "PM2.5"`. It returns original cell strings with `date_raw`/`hour_raw`; it excludes AQI and `PM2.5_24h`, without claiming quality control or timezone resolution. A multi-file study calls it per file, then combines the selected rows before daily aggregation; duplicate checks must cover the combined table.

## Reviewed time declaration and daily call

[Quotsoft's publisher page](https://quotsoft.net/air/) documents the one-hour PM2.5 type and date/hour fields, but does not establish timezone, start/end labelling or midnight assignment. It describes station-list CSV/XLSX fields and dated filenames, linking full tables through a cloud drive; that does not confirm historical coordinate validity or CRS. Do not infer these from current stations or a map.

[HJ 653—2021, Annex A, Table A.1](https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/202201/W020220324400870798705.pdf) defines instrument hourly labels as measurement end times. This normative convention alone does not prove Quotsoft's transformation into `date,hour`. Keep that source-specific mapping unresolved until reviewed evidence supports it.

The caller must review all four `time_reference` fields: `status="reviewed"`, `timezone="Asia/Shanghai"`, `hour_label="start"` or `"end"`, and a nonempty evidence reference identifying the source/version and the documented mapping. The helper only validates the declaration's form; it does not verify its truth. It supports only that timezone and 0–23 integer hours. It cannot accept 24, other timezones or arbitrary interval lengths. Do not set `reviewed` just to pass the gate. A reviewed timezone alone is insufficient if hour-label mapping remains unknown.

Once the configuration contains a genuinely reviewed declaration and verified missing symbols, the following call is executable. The unreviewed template above intentionally fails with `pm25_time_reference_requires_review`.

```python
qc, daily = pm25.prepare_daily(
    selected, time_reference=config["time_reference"],
    min_hours=config["min_hours"], missing_tokens=config["missing_tokens"],
)
assert len(qc) == len(selected)
assert qc["date_raw"].equals(selected["date_raw"])
assert qc["hour_raw"].equals(selected["hour_raw"])
assert not qc.duplicated(["station_id", "interval_start_utc"]).any()
assert (qc["interval_end_utc"] - qc["interval_start_utc"]).eq(pd.Timedelta(hours=1)).all()
assert daily["n_valid_hours"].le(daily["n_source_hours"]).all()
insufficient = daily["n_valid_hours"] < config["min_hours"]
assert daily.loc[insufficient, "pm25_mean"].isna().all()
assert daily.loc[insufficient, "daily_status"].eq("insufficient_observed_hours").all()
qc.to_csv(out / "pm25_hourly_qc.csv", index=False, mode="x")
daily.to_csv(out / "pm25_daily.csv", index=False, mode="x")
```

`prepare_daily(hourly, time_reference, min_hours, missing_tokens=("",))` returns `(hourly_qc, daily)`. It retains input labels, adds UTC interval boundaries and interval-start local dates, rejects duplicate station/timestamp records, and never imputes. Missing tokens/NA become `missing`; finite nonnegative numbers become `observed`; negative or nonfinite numeric values become `invalid`. Undeclared nonnumeric symbols cause an error rather than silent coercion. This is basic numeric screening, not full regulatory quality assurance. Verify concentration units/state and source quality flags separately.

Daily output contains `station_id`, `date_local`, `pm25_mean`, `n_valid_hours`, `n_source_hours`, `n_missing_hours`, `n_invalid_hours`, and `daily_status`. The last two hour counts describe present source rows; they do not count absent rows. Entirely absent station-days are not synthesized. `complete` means the requested observed-hour threshold was met, not that all 24 hours or all target dates are present or scientifically approved. Compare with the study's expected station/date calendar separately.

For `hour_label="end"`, midnight belongs to the preceding measurement day. A CSV with labels 0–23 can therefore contribute to two local days; the following day's midnight may be needed to close the requested final day. Combine boundary files only within authorization, then filter by derived `date_local`. A minimum of 20 unique observed hours is the caller's explicit policy here, not evidence that an unresolved calendar boundary is acceptable.

The helper does not join station-history tables, resolve CRS, transform coordinates or perform spatial matching. Keep unresolved history/CRS as separate gates. Review source, extraction, time mapping, numeric screening, calendar coverage and scientific acceptance separately before downstream use.
