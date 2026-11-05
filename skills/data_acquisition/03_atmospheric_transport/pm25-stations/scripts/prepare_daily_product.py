"""Bounded in-memory preparation of legacy daily PM2.5 tables; no aggregation."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
import re

import numpy as np
import pandas as pd


def _date_label(value):
    """Parse explicit calendar dates without timezone or time-of-day inference."""
    if isinstance(value, datetime):
        if value.tzinfo is not None or value.time() != datetime.min.time():
            raise ValueError("pm25_invalid_daily_date")
        value = value.date()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d{8}", value):
        raise ValueError("pm25_invalid_daily_date")
    try:
        pattern = "%Y-%m-%d" if "-" in value else "%Y%m%d"
        return datetime.strptime(value, pattern).date().isoformat()
    except ValueError:
        raise ValueError("pm25_invalid_daily_date") from None


def _numeric(value):
    if isinstance(value, (bool, np.bool_)):
        return np.nan
    try:
        return float(value)
    except (ValueError, TypeError, OverflowError):
        return np.nan


def prepare_legacy_daily(table, station_ids, expected_dates, *, min_source_rows, interpretation):
    """Preserve a requested station/date calendar under caller-accepted assumptions.

    ``count`` is legacy source-row n(), never verified valid hours. A passing
    row is an engineering-pilot target only. Metadata assertions do not verify
    station identity, historical positions, timezone or CRS. Input is unchanged.
    """
    declarations = {
        "status": "user_accepted_assumptions", "timezone": "Asia/Shanghai",
        "date_label": "legacy_source_date", "coordinate_crs": "EPSG:4326",
        "historical_coordinate_validity": "unverified",
    }
    if (not isinstance(interpretation, dict)
            or any(interpretation.get(key) != value for key, value in declarations.items())
            or not isinstance(interpretation.get("evidence"), str)
            or not interpretation["evidence"].strip()):
        raise ValueError("pm25_daily_interpretation_requires_accepted_assumptions")
    if isinstance(station_ids, (str, bytes)):
        raise ValueError("pm25_invalid_station_selection")
    ids = list(station_ids)
    if (not ids or len(ids) > 100
            or any(not isinstance(v, str) or not v.strip() for v in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError("pm25_invalid_station_selection")
    if isinstance(expected_dates, (str, bytes)):
        raise ValueError("pm25_invalid_expected_dates")
    dates = [_date_label(v) for v in expected_dates]
    if not dates or len(set(dates)) != len(dates):
        raise ValueError("pm25_invalid_expected_dates")
    if (isinstance(min_source_rows, bool) or not isinstance(min_source_rows, int)
            or not 1 <= min_source_rows <= 24):
        raise ValueError("pm25_invalid_source_row_threshold")
    required = {"date", "station_code", "type", "value", "count", "Lon", "Lat"}
    if (not isinstance(table, pd.DataFrame) or not table.columns.is_unique
            or not required.issubset(table.columns)):
        raise ValueError("pm25_invalid_legacy_daily_table")
    pollutant = table.loc[table["type"].eq("PM2.5")]
    if pollutant["station_code"].map(lambda v: not isinstance(v, str) or not v.strip()).any():
        raise ValueError("pm25_invalid_source_station_identity")
    selected = pollutant.loc[pollutant["station_code"].isin(ids)].copy()
    selected["date_local"] = selected["date"].map(_date_label)
    selected = selected.loc[selected["date_local"].isin(dates)]
    if selected.duplicated(["station_code", "date_local"]).any():
        raise ValueError("pm25_duplicate_daily_observation")
    indexed = selected.set_index(["station_code", "date_local"])
    rows = []
    for station in ids:
        for day in dates:
            row = {"station_id": station, "date_local": day,
                   "pm25_daily_ug_m3": np.nan, "source_value": np.nan,
                   "source_row_count": np.nan, "source_longitude": np.nan,
                   "source_latitude": np.nan, "daily_status": "missing",
                   "daily_reasons": ("missing_source_day",)}
            if (station, day) in indexed.index:
                source = indexed.loc[(station, day)]
                target, count = _numeric(source["value"]), _numeric(source["count"])
                reasons = []
                if not np.isfinite(target) or target < 0:
                    reasons.append("invalid_or_missing_target")
                if not np.isfinite(count) or count != np.floor(count) or not 0 <= count <= 24:
                    reasons.append("invalid_or_missing_source_row_count")
                elif count < min_source_rows:
                    reasons.append("insufficient_source_rows")
                row.update(source_value=source["value"], source_row_count=source["count"],
                           source_longitude=source["Lon"], source_latitude=source["Lat"],
                           daily_status="invalid" if reasons else "accepted",
                           daily_reasons=tuple(reasons))
                if not reasons:
                    row["pm25_daily_ug_m3"] = target
            rows.append(row)
    daily = pd.DataFrame(rows)
    quality = {
        "interpretation": deepcopy(interpretation), "use_scope": "engineering_pilot_only",
        "source_count_semantics": "legacy_n_source_rows_not_verified_valid_hours",
        "station_identity_verified": False, "metadata_verified": False,
        "min_source_rows": min_source_rows, "requested_station_ids": ids.copy(),
        "expected_dates": dates.copy(), "expected_calendar_rows": len(ids) * len(dates),
        "selected_source_rows": len(selected),
        "status_counts": {status: int(daily["daily_status"].eq(status).sum())
                          for status in ("accepted", "invalid", "missing")},
        "reason_counts": {reason: sum(reason in reasons for reasons in daily["daily_reasons"])
                          for reason in ("missing_source_day", "invalid_or_missing_target",
                                         "invalid_or_missing_source_row_count", "insufficient_source_rows")},
    }
    return {"daily": daily, "quality": quality}
