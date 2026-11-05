"""Synthetic PM2.5 label, completeness and lossless-selection checks."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("pm25_preparation", ROOT /
    "skills/data_acquisition/03_atmospheric_transport/pm25-stations/scripts/prepare_hourly.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
REFERENCE = {"status": "reviewed", "timezone": "Asia/Shanghai", "hour_label": "start", "evidence": "synthetic_fixture"}


def example(count=24):
    return pd.DataFrame({"station_id": ["A"]*count, "date_raw": ["20240229"]*count,
        "hour_raw": list(range(count)), "value_raw": [str(v) for v in range(count)]})


def test_select_exact_pollutant_and_station_preserving_original_cells(tmp_path):
    p = tmp_path/"day.csv"
    p.write_text("date,hour,type,A,B\n20240229,0,PM2.5,01.00,999\n20240229,0,PM2.5_24h,800,800\n20240229,0,AQI,500,500\n",encoding="utf-8")
    selected = M.extract_quotsoft_hourly(p, ["A"], "20240229")
    assert len(selected)==1 and selected.iloc[0]["value_raw"]=="01.00" and set(selected.station_id)=={"A"}


def test_unreviewed_time_metadata_fails_before_aggregation():
    with pytest.raises(ValueError, match="requires_review"):
        M.prepare_daily(example(), {**REFERENCE, "status": "unknown"}, 20)


@pytest.mark.parametrize("count,valid", [(19, False), (20, True), (24, True)])
def test_threshold_uses_observed_hours_not_fixed_sample_counts(count, valid):
    _, daily = M.prepare_daily(example(count), REFERENCE, 20)
    assert daily.iloc[0].n_valid_hours==count
    assert bool(pd.notna(daily.iloc[0].pm25_mean))==valid
    if valid: assert daily.iloc[0].pm25_mean==pytest.approx((count-1)/2)


def test_end_midnight_belongs_to_previous_measurement_day():
    frame=example();frame["hour_raw"]=list(range(1,24))+[0]
    frame.loc[23,"date_raw"]="20240301"
    hourly,daily=M.prepare_daily(frame,{**REFERENCE,"hour_label":"end"},20)
    assert list(daily.date_local)==["2024-02-29"] and daily.iloc[0].n_valid_hours==24
    assert str(hourly.iloc[23].interval_start_utc)=="2024-02-29 15:00:00+00:00"


def test_missing_invalid_and_duplicates_are_explicit():
    frame=example();frame.loc[0,"value_raw"]="";frame.loc[1,"value_raw"]="-1";frame.loc[2,"value_raw"]="inf"
    hourly,daily=M.prepare_daily(frame,REFERENCE,20)
    assert daily.iloc[0].n_valid_hours==21 and daily.iloc[0].n_missing_hours==1 and daily.iloc[0].n_invalid_hours==2
    assert np.isnan(hourly.iloc[0].value)
    with pytest.raises(ValueError,match="duplicate"):
        M.prepare_daily(pd.concat([frame,frame.iloc[[0]]]),REFERENCE,20)


@pytest.mark.parametrize("column,value", [("date_raw","20240230"),("hour_raw",24),("hour_raw",.5),("value_raw","not-a-number")])
def test_malformed_values_are_not_silently_replaced(column,value):
    frame=example();frame[column]=frame[column].astype(object);frame.loc[0,column]=value
    with pytest.raises(ValueError):M.prepare_daily(frame,REFERENCE,20)
