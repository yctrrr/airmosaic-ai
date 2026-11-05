"""Complete-sampling local-day means for explicit UTC gridded time series."""
from __future__ import annotations

import numpy as np
import pandas as pd


def daily_grid_mean(values, times_utc, expected_dates, *, timezone, sample_interval_hours):
    """Aggregate [time, y, x] instantaneous fields without filling gaps.

    The declared UTC samples lie on the 00:00 UTC hourly/three-hourly phase.
    Three-hourly daily means summarize eight samples, not 24 hourly observations.
    Any absent/nonfinite sample makes that day/cell unavailable. Units are
    preserved; accumulated variables require a different reviewed operation.
    """
    if timezone != "Asia/Shanghai" or sample_interval_hours not in (1, 3) or isinstance(sample_interval_hours, bool):
        raise ValueError("grid_daily_unsupported_time_contract")
    field = np.asarray(values)
    if (field.ndim != 3 or field.dtype.kind not in "fiu" or not all(field.shape)
            or field.shape[0] != len(times_utc)):
        raise ValueError("grid_daily_invalid_field")
    if np.ma.isMaskedArray(values):
        field = np.ma.asarray(values, dtype=float).filled(np.nan)
    try:
        times = pd.DatetimeIndex(pd.to_datetime(times_utc, errors="raise"))
        dates = list(expected_dates)
        parsed = pd.to_datetime(dates, format="%Y-%m-%d", errors="raise")
    except (ValueError, TypeError):
        raise ValueError("grid_daily_invalid_calendar") from None
    if (times.tz is None or times.isna().any() or times.has_duplicates or not times.is_monotonic_increasing
            or any(t.utcoffset().total_seconds() != 0 for t in times)
            or any(t.minute or t.second or t.microsecond or t.hour % sample_interval_hours for t in times)):
        raise ValueError("grid_daily_requires_unique_utc_phase_samples")
    if not dates or len(set(dates)) != len(dates) or not parsed.is_monotonic_increasing:
        raise ValueError("grid_daily_invalid_calendar")
    labels = times.tz_convert(timezone).strftime("%Y-%m-%d")
    expected = 24//sample_interval_hours
    daily = np.full((len(dates), *field.shape[1:]), np.nan)
    finite_counts = np.zeros(daily.shape, dtype=int)
    source_counts = []
    for i, day in enumerate(dates):
        selected = field[labels == day]
        source_counts.append(len(selected))
        if len(selected):
            counts = np.isfinite(selected).sum(axis=0)
            finite_counts[i] = counts
            if len(selected) == expected:
                complete = counts == expected
                daily[i, complete] = selected[:, complete].mean(axis=0)
    return {"dates": dates, "values": daily, "finite_sample_count": finite_counts,
            "source_sample_count": source_counts, "expected_samples_per_day": expected,
            "sample_interval_hours": sample_interval_hours, "timezone": timezone,
            "outside_expected_period_samples": int(sum(day not in set(dates) for day in labels)),
            "statistic": "arithmetic_mean_of_complete_instantaneous_samples"}
