"""Synthetic checks for bounded preparation of existing daily products."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("pm25_daily_product", ROOT /
    "skills/data_acquisition/03_atmospheric_transport/pm25-stations/scripts/prepare_daily_product.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
INTERPRETATION = {
    "status": "user_accepted_assumptions", "timezone": "Asia/Shanghai",
    "date_label": "legacy_source_date", "coordinate_crs": "EPSG:4326",
    "historical_coordinate_validity": "unverified", "evidence": "synthetic_review",
}


def example():
    return pd.DataFrame([{"date": "2020-02-29", "station_code": "001", "type": "PM2.5",
                          "value": "01.50", "count": "20", "Lon": "110.5", "Lat": 30.0}])


def prepare(frame, **kwargs):
    return M.prepare_legacy_daily(frame, kwargs.pop("station_ids", ["001"]),
        kwargs.pop("expected_dates", ["2020-02-29"]), min_source_rows=kwargs.pop("min_source_rows", 20),
        interpretation=kwargs.pop("interpretation", INTERPRETATION), **kwargs)


def test_calendar_leap_day_exact_selection_and_source_preservation():
    frame = example()
    other = pd.concat([frame.assign(type="PM2.5_24h", value=900),
                       frame.assign(type="AQI", value=800), frame.assign(station_code="002")])
    original = pd.concat([frame, other], ignore_index=True)
    before = original.copy(deep=True)
    result = prepare(original, station_ids=["001", "003"],
                     expected_dates=["2020-02-28", "20200229", "2020-03-01"])
    daily, quality = result["daily"], result["quality"]
    assert len(daily) == 6
    accepted = daily.loc[daily.daily_status.eq("accepted")].iloc[0]
    assert accepted.station_id == "001" and accepted.date_local == "2020-02-29"
    assert accepted.pm25_daily_ug_m3 == 1.5 and accepted.source_value == "01.50"
    assert accepted.source_row_count == "20" and accepted.source_longitude == "110.5"
    assert daily.pm25_daily_ug_m3.isna().sum() == 5
    assert quality["status_counts"] == {"accepted": 1, "invalid": 0, "missing": 5}
    assert quality["interpretation"] == INTERPRETATION
    assert quality["metadata_verified"] is False and quality["station_identity_verified"] is False
    assert quality["source_count_semantics"] == "legacy_n_source_rows_not_verified_valid_hours"
    pd.testing.assert_frame_equal(original, before)


@pytest.mark.parametrize("value", [None, np.nan, np.inf, -1, "bad", True])
def test_bad_target_remains_missing_with_source_value(value):
    frame = example(); frame["value"] = [value]
    row = prepare(frame)["daily"].iloc[0]
    assert np.isnan(row.pm25_daily_ug_m3) and row.daily_status == "invalid"
    assert "invalid_or_missing_target" in row.daily_reasons
    assert pd.isna(row.source_value) if pd.isna(value) else row.source_value == value


@pytest.mark.parametrize("count,reason", [(None, "invalid_or_missing_source_row_count"),
    (np.inf, "invalid_or_missing_source_row_count"), (20.5, "invalid_or_missing_source_row_count"),
    (-1, "invalid_or_missing_source_row_count"), (25, "invalid_or_missing_source_row_count"),
    (True, "invalid_or_missing_source_row_count"), ("bad", "invalid_or_missing_source_row_count"),
    (0, "insufficient_source_rows"), (19, "insufficient_source_rows")])
def test_invalid_counts_do_not_claim_valid_hours(count, reason):
    frame = example(); frame["count"] = [count]
    row = prepare(frame)["daily"].iloc[0]
    assert np.isnan(row.pm25_daily_ug_m3) and reason in row.daily_reasons


def test_duplicate_selected_station_day_refused_without_aggregation():
    with pytest.raises(ValueError, match="duplicate"):
        prepare(pd.concat([example(), example()]))


@pytest.mark.parametrize("date", ["2019-02-29", "2020-02-30", "2020-2-29", 20200229,
                                   "2020-02-29T00:00:00", None])
def test_malformed_source_dates_refused(date):
    frame = example(); frame["date"] = [date]
    with pytest.raises(ValueError, match="date"):
        prepare(frame)


@pytest.mark.parametrize("dates", [["2019-02-29"], [], ["20200229", "2020-02-29"], "2020-02-29"])
def test_invalid_requested_calendar_refused(dates):
    with pytest.raises(ValueError):
        prepare(example(), expected_dates=dates)


@pytest.mark.parametrize("key,value", [("status", "reviewed"), ("timezone", "UTC"),
    ("date_label", "inferred"), ("coordinate_crs", "unknown"),
    ("historical_coordinate_validity", "verified"), ("evidence", "")])
def test_assumptions_must_be_explicit_and_not_relabelled_verified(key, value):
    with pytest.raises(ValueError, match="accepted_assumptions"):
        prepare(example(), interpretation={**INTERPRETATION, key: value})


@pytest.mark.parametrize("ids", [["001", "001"], [1], [], "001", [str(i) for i in range(101)]])
def test_station_selection_bounds(ids):
    with pytest.raises(ValueError, match="station"):
        prepare(example(), station_ids=ids)


def test_empty_product_keeps_requested_calendar_and_deep_copies_assumptions():
    interpretation = {**INTERPRETATION, "extra": {"fixture": True}}
    result = prepare(example().iloc[:0], interpretation=interpretation)
    assert result["daily"].iloc[0].daily_status == "missing"
    interpretation["extra"]["fixture"] = False
    assert result["quality"]["interpretation"]["extra"]["fixture"] is True


@pytest.mark.parametrize("threshold", [0, 25, True, 20.5])
def test_invalid_threshold_refused(threshold):
    with pytest.raises(ValueError, match="threshold"):
        prepare(example(), min_source_rows=threshold)
