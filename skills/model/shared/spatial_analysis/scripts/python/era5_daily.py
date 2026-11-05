"""Read bounded ERA5 daily NetCDF deliveries with an explicit local-date contract.

The caller must verify the official request's daily_mean, 1_hourly sampling and
UTC+08 shift. Nominal daily NetCDF labels are calendar labels, not hourly UTC
samples. This reader does not independently certify all contributing hours.
"""
from pathlib import Path
import tempfile
import zipfile
import numpy as np
import pandas as pd
import xarray as xr

FIELDS={'t2m':(167,'K'),'d2m':(168,'K'),'u10':(165,'m s**-1'),
        'v10':(166,'m s**-1'),'sp':(134,'Pa')}


def _read_one(path, expected_dates, area):
    fields={}; metadata={}
    with xr.open_dataset(path,engine='netcdf4') as dataset:
        lat='latitude' if 'latitude' in dataset.coords else 'lat'
        lon='longitude' if 'longitude' in dataset.coords else 'lon'
        time='valid_time' if 'valid_time' in dataset.coords else 'time'
        if any(c not in dataset.coords for c in (lat,lon,time)):
            raise ValueError('era5_daily_missing_axes')
        x=np.asarray(dataset[lon].values,dtype=float);y=np.asarray(dataset[lat].values,dtype=float)
        north,west,south,east=area
        ex=np.arange(round((east-west)/.25)+1)*.25+west
        ey=north-np.arange(round((north-south)/.25)+1)*.25
        if x.ndim!=1 or y.ndim!=1 or not np.array_equal(x,ex) or not np.array_equal(y,ey):
            raise ValueError('era5_daily_grid_contract_mismatch')
        times=pd.DatetimeIndex(dataset[time].values)
        if times.has_duplicates or times.isna().any() or not times.is_monotonic_increasing:
            raise ValueError('era5_daily_invalid_dates')
        # The daily-statistics service labels periods at midnight. The +08
        # averaging window is attested separately by the exact official request.
        if any(t.hour or t.minute or t.second or t.microsecond for t in times):
            raise ValueError('era5_daily_ambiguous_time_labels')
        dates=times.strftime('%Y-%m-%d').tolist()
        if dates!=list(expected_dates):raise ValueError('era5_daily_calendar_mismatch')
        for name,array in dataset.data_vars.items():
            if name not in FIELDS:raise ValueError('era5_daily_unexpected_variable')
            param,unit=FIELDS[name]
            actual_unit=array.attrs.get('units')
            if actual_unit not in ({'m s**-1','m s-1','m s^-1'} if unit=='m s**-1' else {unit}):
                raise ValueError('era5_daily_units_mismatch')
            if 'GRIB_paramId' in array.attrs and int(array.attrs['GRIB_paramId'])!=param:
                raise ValueError('era5_daily_parameter_mismatch')
            for dim in list(array.dims):
                if dim not in (time,lat,lon):
                    if array.sizes[dim]!=1:raise ValueError('era5_daily_extra_dimension')
                    array=array.isel({dim:0})
            if set(array.dims)!={time,lat,lon}:raise ValueError('era5_daily_dimension_mismatch')
            values=np.asarray(array.transpose(time,lat,lon).values,dtype=float)
            if np.isinf(values).any():raise ValueError('era5_daily_infinite_value')
            fields[name]=values
            metadata[name]={'units':actual_unit,'parameter_id_in_file':int(array.attrs['GRIB_paramId']) if 'GRIB_paramId' in array.attrs else None,
                'long_name':array.attrs.get('long_name'),'nonfinite_cells':int(np.isnan(values).sum())}
    return {'x':x,'y':y,'dates':dates,'fields':fields,'metadata':metadata}


def read_era5_daily(path, expected_dates, *, area_nwse, temp_root,
                    max_unpacked_bytes=256*1024**2, max_members=10):
    """Read one reviewed package; never download or trust archive member paths."""
    path=Path(path)
    if not expected_dates or len(set(expected_dates))!=len(expected_dates):
        raise ValueError('era5_daily_invalid_expected_calendar')
    parsed=pd.to_datetime(expected_dates,format='%Y-%m-%d',errors='raise')
    if not parsed.is_monotonic_increasing:raise ValueError('era5_daily_invalid_expected_calendar')
    if (not isinstance(max_unpacked_bytes,int) or isinstance(max_unpacked_bytes,bool)
            or max_unpacked_bytes<=0 or not isinstance(max_members,int) or isinstance(max_members,bool) or max_members<=0):
        raise ValueError('era5_daily_invalid_budget')
    results=[]
    with tempfile.TemporaryDirectory(dir=temp_root,prefix='daily_decode_') as work:
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                members=archive.infolist()
                if not 0<len(members)<=max_members or sum(i.file_size for i in members)>max_unpacked_bytes:
                    raise ValueError('era5_daily_archive_budget')
                for index,item in enumerate(members):
                    if item.is_dir() or not item.filename.endswith('.nc') or item.flag_bits&1:
                        raise ValueError('era5_daily_unexpected_archive_member')
                    # Ignore supplier names completely; write a fresh local basename.
                    target=Path(work)/f'field_{index}.nc'
                    received=0
                    with archive.open(item) as source,target.open('xb') as output:
                        while block:=source.read(65536):
                            received+=len(block)
                            if received>item.file_size:raise ValueError('era5_daily_unpacked_size_mismatch')
                            output.write(block)
                    if received!=item.file_size:raise ValueError('era5_daily_unpacked_size_mismatch')
                    results.append(_read_one(target,expected_dates,area_nwse))
        else:
            if path.stat().st_size>max_unpacked_bytes:raise ValueError('era5_daily_file_budget')
            results.append(_read_one(path,expected_dates,area_nwse))
    combined={};metadata={}
    first=results[0]
    for result in results:
        if result['dates']!=first['dates'] or not np.array_equal(result['x'],first['x']) or not np.array_equal(result['y'],first['y']):
            raise ValueError('era5_daily_member_axes_mismatch')
        if set(combined)&set(result['fields']):raise ValueError('era5_daily_duplicate_variable')
        combined.update(result['fields']);metadata.update(result['metadata'])
    if set(combined)!=set(FIELDS):raise ValueError('era5_daily_missing_variable')
    return {**first,'fields':combined,'metadata':metadata,
            'time_contract':'provider_daily_mean_1_hourly_utc_plus_08_verified_by_caller',
            'all_source_hours_independently_checked':False}
