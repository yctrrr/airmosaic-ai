"""Selected-station extraction and explicitly reviewed hourly-to-daily preparation.

No downloads, metadata inference, credential handling or implicit data discovery.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


def extract_quotsoft_hourly(source, station_ids, expected_date=None):
    """Keep selected original station cells and exact PM2.5 hourly labels only.

    The selected cells remain strings. This projection alone does not establish
    timezone, interval semantics, coordinates, quality control or daily means.
    """
    ids = list(station_ids)
    if (not ids or len(ids) > 100 or len(set(ids)) != len(ids)
            or any(not isinstance(v, str) or not v.strip() for v in ids)):
        raise ValueError("pm25_invalid_station_selection")
    records = []
    with Path(source).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if (len(set(fields)) != len(fields) or not {"date", "hour", "type", *ids}.issubset(fields)):
            raise ValueError("pm25_source_columns_missing_or_duplicated")
        for row in reader:
            if None in row or any(row.get(key) is None for key in fields):
                raise ValueError("pm25_malformed_source_row")
            if expected_date is not None and row["date"] != expected_date:
                raise ValueError("pm25_unexpected_source_date")
            if row["type"] != "PM2.5":
                continue
            for station_id in ids:
                records.append({"station_id": station_id, "date_raw": row["date"],
                    "hour_raw": row["hour"], "value_raw": row[station_id]})
    if not records:
        raise ValueError("pm25_no_hourly_rows")
    return pd.DataFrame(records, columns=["station_id", "date_raw", "hour_raw", "value_raw"])


def prepare_daily(hourly, time_reference, min_hours, missing_tokens=("",)):
    """Return interval-labelled hourly QC and daily means under explicit metadata.

    ``time_reference`` must contain status=reviewed, timezone=Asia/Shanghai,
    hour_label=start|end and a nonempty evidence reference. This is a caller
    declaration, not an authentication or source-verification service.
    A midnight *end* label belongs to the preceding measurement day.
    """
    if (not isinstance(time_reference, dict) or time_reference.get("status") != "reviewed"
            or time_reference.get("timezone") != "Asia/Shanghai"
            or time_reference.get("hour_label") not in {"start", "end"}
            or not isinstance(time_reference.get("evidence"), str)
            or not time_reference["evidence"].strip()):
        raise ValueError("pm25_time_reference_requires_review")
    if isinstance(min_hours, bool) or not isinstance(min_hours, int) or not 1 <= min_hours <= 24:
        raise ValueError("pm25_invalid_completeness_threshold")
    required = {"station_id", "date_raw", "hour_raw", "value_raw"}
    if (not isinstance(hourly, pd.DataFrame) or hourly.empty or not hourly.columns.is_unique
            or not required.issubset(hourly.columns)):
        raise ValueError("pm25_invalid_hourly_table")
    data = hourly.copy()
    if data["station_id"].map(lambda v: not isinstance(v, str) or not v.strip()).any():
        raise ValueError("pm25_invalid_station_identity")
    dates = data["date_raw"].astype(str)
    if not dates.str.fullmatch(r"\d{8}").all():
        raise ValueError("pm25_invalid_date")
    try:
        days = pd.to_datetime(dates, format="%Y%m%d", errors="raise")
        hours = pd.to_numeric(data["hour_raw"], errors="raise")
    except (ValueError, TypeError):
        raise ValueError("pm25_invalid_date_or_hour") from None
    if (not np.isfinite(hours).all() or (hours != np.floor(hours)).any()
            or (hours < 0).any() or (hours > 23).any()):
        raise ValueError("pm25_invalid_hour")
    timestamp = (days + pd.to_timedelta(hours, unit="h")).dt.tz_localize("Asia/Shanghai")
    if data.assign(timestamp=timestamp).duplicated(["station_id", "timestamp"]).any():
        raise ValueError("pm25_duplicate_hourly_observation")
    start = timestamp - pd.Timedelta(hours=1) if time_reference["hour_label"] == "end" else timestamp
    data["interval_start_utc"] = start.dt.tz_convert("UTC")
    data["interval_end_utc"] = data["interval_start_utc"] + pd.Timedelta(hours=1)
    data["date_local"] = start.dt.strftime("%Y-%m-%d")
    raw = data["value_raw"]
    is_missing = raw.isna() | raw.astype(str).isin(list(missing_tokens))
    try:
        values = pd.to_numeric(raw.where(~is_missing, np.nan), errors="raise")
    except (ValueError, TypeError):
        raise ValueError("pm25_undeclared_nonnumeric_value") from None
    valid = ~is_missing & np.isfinite(values) & (values >= 0)
    data["value"] = values
    data["value_status"] = np.where(is_missing, "missing", np.where(valid, "observed", "invalid"))
    rows = []
    for (station, day), group in data.groupby(["station_id", "date_local"], sort=True):
        observed = group[group["value_status"] == "observed"]
        count = len(observed)
        rows.append({"station_id": station, "date_local": day,
            "pm25_mean": float(observed["value"].mean()) if count >= min_hours else np.nan,
            "n_valid_hours": count, "n_source_hours": len(group),
            "n_missing_hours": int((group["value_status"] == "missing").sum()),
            "n_invalid_hours": int((group["value_status"] == "invalid").sum()),
            "daily_status": "complete" if count >= min_hours else "insufficient_observed_hours"})
    return data, pd.DataFrame(rows)
