"""Synthetic NetCDF/ZIP contracts for the provider daily reader."""
import importlib.util
from pathlib import Path
import zipfile
import numpy as np
import pytest
xr=pytest.importorskip('xarray')
pytest.importorskip('netCDF4')
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('daily',ROOT/'skills/model/shared/spatial_analysis/scripts/python/era5_daily.py')
daily=importlib.util.module_from_spec(spec);spec.loader.exec_module(daily)
DATES=['2020-01-01','2020-01-02'];AREA=[31,100,30.75,100.25]

def dataset():
    return xr.Dataset({name:(('valid_time','latitude','longitude'),np.arange(8).reshape(2,2,2).astype(float),
        {'units':unit,'GRIB_paramId':param}) for name,(param,unit) in daily.FIELDS.items()},
        coords={'valid_time':np.array(DATES,dtype='datetime64[ns]'),'latitude':[31,30.75],'longitude':[100,100.25]})

def read(path,tmp_path,**kwargs):
    return daily.read_era5_daily(path,DATES,area_nwse=AREA,temp_root=tmp_path,**kwargs)

def test_daily_values_and_missing_preserved(tmp_path):
    d=dataset();d['t2m'].values[0,0,0]=np.nan;p=tmp_path/'input.nc';d.to_netcdf(p,engine='netcdf4')
    out=read(p,tmp_path)
    assert np.isnan(out['fields']['t2m'][0,0,0])
    assert out['dates']==DATES and out['all_source_hours_independently_checked'] is False

@pytest.mark.parametrize('bad,reason',[
    ('units','units_mismatch'),('param','parameter_mismatch'),('grid','grid_contract_mismatch'),
    ('date','calendar_mismatch'),('hour','ambiguous_time_labels'),('duplicate_time','invalid_dates'),
    ('unknown','unexpected_variable'),('missing','missing_variable'),('infinite','infinite_value')])
def test_refusals(tmp_path,bad,reason):
    d=dataset()
    if bad=='units':d['t2m'].attrs['units']='degC'
    elif bad=='param':d['t2m'].attrs['GRIB_paramId']=168
    elif bad=='grid':d=d.assign_coords(longitude=[100,100.5])
    elif bad=='date':d=d.assign_coords(valid_time=np.array(['2020-01-02','2020-01-03'],dtype='datetime64[ns]'))
    elif bad=='hour':d=d.assign_coords(valid_time=d.valid_time.values+np.timedelta64(1,'h'))
    elif bad=='duplicate_time':d=d.assign_coords(valid_time=np.array(['2020-01-01','2020-01-01'],dtype='datetime64[ns]'))
    elif bad=='unknown':d=d.rename({'sp':'unknown'})
    elif bad=='missing':d=d.drop_vars('sp')
    elif bad=='infinite':d['t2m'].values[0,0,0]=np.inf
    p=tmp_path/'input.nc';d.to_netcdf(p,engine='netcdf4')
    with pytest.raises(ValueError,match=reason):read(p,tmp_path)

def test_zip_budgets_duplicates_and_safe_names(tmp_path):
    p=tmp_path/'input.nc';dataset().to_netcdf(p,engine='netcdf4')
    z=tmp_path/'input.zip'
    with zipfile.ZipFile(z,'w') as archive:archive.write(p,'../../escape.nc')
    assert read(z,tmp_path)['dates']==DATES
    assert not (tmp_path.parent/'escape.nc').exists()
    with pytest.raises(ValueError,match='archive_budget'):read(z,tmp_path,max_unpacked_bytes=1)
    with zipfile.ZipFile(z,'a') as archive:archive.write(p,'duplicate.nc')
    with pytest.raises(ValueError,match='duplicate_variable'):read(z,tmp_path)

def test_unexpected_member(tmp_path):
    z=tmp_path/'input.zip'
    with zipfile.ZipFile(z,'w') as archive:archive.writestr('note.txt','not data')
    with pytest.raises(ValueError,match='unexpected_archive_member'):read(z,tmp_path)
