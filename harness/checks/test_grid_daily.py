"""Synthetic checks for UTC/local boundaries and complete grid support."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[2]
S = importlib.util.spec_from_file_location("grid_daily",ROOT/
    "skills/model/shared/spatial_analysis/scripts/python/grid_daily.py")
M = importlib.util.module_from_spec(S);S.loader.exec_module(M)


def run(values,times,dates=("2024-01-01",),step=1):
    return M.daily_grid_mean(values,times,dates,timezone="Asia/Shanghai",sample_interval_hours=step)


@pytest.mark.parametrize("step",[1,3])
def test_full_local_day_with_previous_utc_year(step):
    start="2023-12-31 16:00+00:00" if step==1 else "2023-12-31 18:00+00:00"
    times=pd.date_range(start,periods=24//step,freq=f"{step}h")
    values=np.arange(len(times)*4,dtype=float).reshape(len(times),2,2)
    result=run(values,times,step=step)
    assert result["expected_samples_per_day"]==24//step
    np.testing.assert_allclose(result["values"][0],values.mean(axis=0))


def test_missing_timestep_masks_entire_day_without_filling():
    times=pd.date_range("2023-12-31 16:00+00:00",periods=23,freq="h")
    result=run(np.ones((23,2,2)),times)
    assert np.isnan(result["values"]).all() and result["source_sample_count"]==[23]


def test_missing_cell_only_masks_its_own_daily_support():
    times=pd.date_range("2023-12-31 16:00+00:00",periods=24,freq="h")
    values=np.ones((24,2,2));values[0,0,0]=np.nan
    result=run(values,times)
    assert np.isnan(result["values"][0,0,0]) and result["values"][0,1,1]==1
    assert result["finite_sample_count"][0,0,0]==23


def test_masked_hour_is_excluded_from_complete_daily_support():
    times=pd.date_range("2023-12-31 16:00+00:00",periods=24,freq="h")
    values=np.ma.array(np.ones((24,2,2),dtype=int),mask=False)
    values.data[0,0,0]=9999
    values.mask[0,0,0]=True
    result=run(values,times)
    assert np.isnan(result["values"][0,0,0])
    assert result["finite_sample_count"][0,0,0]==23
    assert result["values"][0,1,1]==1 and result["finite_sample_count"][0,1,1]==24
    assert result["source_sample_count"]==[24]
    assert values.mask[0,0,0] and values.data[0,0,0]==9999


def test_leap_day_and_absent_day_are_retained():
    times=pd.date_range("2024-02-28 16:00+00:00",periods=24,freq="h")
    result=run(np.ones((24,2,2)),times,dates=("2024-02-29","2024-03-01"))
    assert result["source_sample_count"]==[24,0] and np.isnan(result["values"][1]).all()


@pytest.mark.parametrize("kind",["naive","duplicate","wrong_phase"])
def test_ambiguous_or_wrong_sampling_is_rejected(kind):
    times=pd.date_range("2024-01-01",periods=8,freq="3h",tz="UTC")
    if kind=="naive":times=times.tz_localize(None)
    elif kind=="duplicate":times=times[:7].append(times[:1])
    else:times=times+pd.Timedelta(hours=1)
    with pytest.raises(ValueError):run(np.ones((8,2,2)),times,step=3)
