"""Documented auxiliary conversion and explicitly artificial initialization."""
import copy
import datetime as dt
import hashlib
import json
import pathlib
import numpy as np
from netCDF4 import Dataset, num2date
from v35l_bpch import block, read, write
from gc_paths import sandbox_root, within
import argparse

def lat_weights(source,target):
    s,t = np.sin(np.deg2rad(source)),np.sin(np.deg2rad(target))
    w = np.maximum(0.,np.minimum(t[1:,None],s[None,1:])-np.maximum(t[:-1,None],s[None,:-1]))
    return w/np.diff(t)[:,None]

def prepare(args):
    root=sandbox_root(args.root)
    out=within(root,args.output)
    assert not out.exists(), 'Fresh derived-input directory required'
    uv_path=within(root,args.uv_netcdf,must_exist=True)
    toms_path=within(root,args.toms_bpch,must_exist=True)
    restart_path=within(root,args.legacy_restart,must_exist=True)
    cn_path=within(root,args.cn_netcdf,must_exist=True)
    out.mkdir(parents=True,exist_ok=False)
    records = []
    def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    def record(rel, details):
        p = out / rel
        records.append({'path':rel, 'bytes':p.stat().st_size, 'sha256':digest(p), **details})

    # Exact reverse of official BPCH -> COARDS conversion, without rescaling data.
    uv = Dataset(uv_path)
    lon = np.arange(-180.,180.,5.)
    lat = np.r_[-89.,np.arange(-86.,87.,4.),89.]
    assert np.array_equal(uv['lon'][:], lon) and np.array_equal(uv['lat'][:], lat)
    uv_data = uv['UVALBD'][:]
    assert not np.ma.getmaskarray(uv_data).any() and np.isfinite(uv_data).all()
    assert uv_data.min() >= 0 and uv_data.max() <= 1
    dates = num2date(uv['time'][:], uv['time'].units, only_use_cftime_datetimes=False)
    assert [(x.year,x.month,x.day) for x in dates] == [(1985,m,1) for m in range(1,13)]
    # BPCH tau is always hours since 1985; the NetCDF source's time unit
    # need not be hours. Use decoded dates rather than copying raw counters.
    taus = [(dt.datetime(x.year,x.month,x.day,x.hour,x.minute,x.second)-dt.datetime(1985,1,1)).total_seconds()/3600 for x in dates]
    final_tau = (dt.datetime(1986,1,1)-dt.datetime(1985,1,1)).total_seconds()/3600
    uv_blocks = [block('GEOS1',5.,4.,'UVALBEDO',1,'percent',t0,t1,np.asarray(v).T[:,:,None])
        for v,t0,t1 in zip(uv_data,taus,taus[1:]+[final_tau])]
    uv_rel = 'uvalbedo_200111/uvalbedo.geos.4x5'
    (out / pathlib.PurePosixPath(uv_rel).parent).mkdir()
    write(out/uv_rel,'Official UV albedo climatology; faithful NC -> BPCH format conversion',uv_blocks)
    _, back = read(out/uv_rel)
    assert all(np.array_equal(a['data'],b['data']) for a,b in zip(uv_blocks,back))
    record(uv_rel, {'source_url':'https://geos-chem.s3-us-west-2.amazonaws.com/HEMCO/UVALBEDO/v2019-06/uvalbedo.geos.4x5.nc',
        'source_sha256':digest(uv_path), 'data_bitwise_roundtrip':True,
        'unit_caveat':'Official units say percent but native FAST_J receives unitless reflectivity; numeric values preserved (0.01 to 0.95), no factor-100 introduced',
        'official_README':'Says same legacy data, BPCH converted to COARDS; 4x5 provided for backward compatibility',
        'grid':[72,46], 'months':12})
    uv.close()

    # Conservative spherical area overlap, periodic in longitude, half polar cells.
    title,toms = read(toms_path)
    assert len(toms) == 36
    assert all(v['data'].shape == (360,181,1) and v['dx']==v['dy']==1 and v['halfpolar']==v['center180']==1 for v in toms)
    src_lat = np.r_[-90.,np.arange(-89.5,90.,1.),90.]
    dst_lat = np.r_[-90.,np.arange(-88.,90.,4.),90.]
    wy = lat_weights(src_lat,dst_lat)
    wx = np.zeros((72,360))
    for i,c in enumerate(lon):
        for j,sc in enumerate(np.arange(-180.,180.,1.)):
            for shift in [-360.,0.,360.]:
                wx[i,j] += max(0.,min(c+2.5,sc+shift+.5)-max(c-2.5,sc+shift-.5))/5.
    assert np.max(np.abs(wx.sum(axis=1)-1)) < 1e-12 and np.max(np.abs(wy.sum(axis=1)-1)) < 1e-12
    src_area = np.deg2rad(1.)*np.diff(np.sin(np.deg2rad(src_lat)))[None,:]
    dst_area = np.deg2rad(5.)*np.diff(np.sin(np.deg2rad(dst_lat)))[None,:]
    errors=[]; converted=[]
    for b in toms:
        assert b['header'][0].strip() == b'TOMS-O3' and b['header'][1] in (1,2,3)
        a=b['data'][:,:,0].astype('f8')
        v=wx @ a @ wy.T
        x=copy.deepcopy(b)
        x.update(dx=5.,dy=4.,data=v.astype('f4')[:,:,None])
        denom=np.sum(np.abs(a)*src_area)
        err=abs(np.sum(x['data'][:,:,0]*dst_area)-np.sum(a*src_area))/max(denom,1e-30)
        assert err < 1e-7
        errors.append(float(err)); converted.append(x)
    toms_rel='TOMS_201203/TOMS_O3col_2010.geos.4x5'
    (out/pathlib.PurePosixPath(toms_rel).parent).mkdir()
    write(out/toms_rel,'Official TOMS2010; conservative spherical 1x1 -> 4x5; metadata retained',converted)
    _,back=read(out/toms_rel)
    assert all(np.array_equal(a['data'],b['data']) for a,b in zip(converted,back))
    record(toms_rel, {'source_url':'https://geos-chem.s3-us-west-2.amazonaws.com/CHEM_INPUTS/TOMS_201203/TOMS_O3col_2010.geos.1x1',
        'source_sha256':digest(toms_path), 'conversion':'area-weighted spherical overlap; periodic longitude, half polar cells',
        'blocks':36,'max_relative_integral_error':max(errors),'block_time_category_tracer_unit_metadata_retained':True,
        'native_assumption':'Native toms_mod.f clamps any year after 2010 to 2010; this is not 2026 ozone analysis'})

    initial=restart_path
    assert digest(initial)=='d4e43215b69c64c6f8d4b20dd600905c6e15e6c1f82a440fd32c2531e8951af2'
    _,restart=read(initial)
    start=dt.datetime.strptime(args.start_utc,'%Y-%m-%dT%H:%M:%SZ')
    assert start.hour%3==0 and start.minute==start.second==0
    initial_name='initial.artificial.'+start.strftime('%Y%m%d%H')+'.bpch'
    tau=(start-dt.datetime(1985,1,1)).total_seconds()/3600
    assert len(restart)==43 and {v['header'][1] for v in restart}==set(range(1,44))
    for b in restart:
        assert b['data'].shape==(72,46,47) and b['header'][2].strip()==b'v/v' and (b['data']>=0).all()
    derived=copy.deepcopy(restart)
    for b in derived:
        b['header'][3:5]=[tau,tau]
    write(out/initial_name,'ARTIFICIAL operating point; legacy43 payload unchanged; NOT 2026 analysis',derived)
    _,back=read(out/initial_name)
    assert all(np.array_equal(a['data'],b['data']) for a,b in zip(restart,back))
    record(initial_name,{'source_url':'https://zenodo.org/records/7517355',
        'source_sha256':digest(initial),'original_date_utc':'2005-07-01T00:00:00Z',
        'changes':'BPCH tau metadata only; original GEOS5_47L label and all 43 tracer arrays preserved bitwise',
        'data_bitwise_roundtrip':True,'vertical_compatibility':'v35l pressure_mod.f uses same AP/BP 47-level definition for GEOS_5 and GEOS_FP',
        'species_mapping_caveat':'Names not embedded; 43-tracer mapping supported by archive README and v8 table, not independently embedded species metadata',
        'scientific_initial_state':False})

    with Dataset(cn_path) as cn:
        vals={k:np.asarray(cn[k][:],dtype='f8') for k in ['FRLAND','FRLANDIC','FRLAKE','FROCEAN']}
        assert all(np.isfinite(v).all() and v.min()>=0 and v.max()<=1 for v in vals.values())
        err=float(np.max(np.abs(sum(vals.values())-1)))
        assert err<0.01
        land_check={'input_sha256':digest(cn_path),'all_finite_bounded_0_1':True,
            'fraction_sum_max_absolute_error':err,'data_normalized':False,
            'land_fraction_for_component':'FRLAND + FRLANDIC',
            'sanity_bound':0.01}
    (out/'land-fraction-check.json').write_text(json.dumps(land_check,indent=2))
    (out/'manifest.json').write_text(json.dumps({'input_files':records,'scientific_acceptance':False,
        'all_outputs_reopened_and_checked':True,'original_inputs_preserved':True},indent=2))
    print(json.dumps({'derived_inputs':len(records),'toms_max_conservation_error':max(errors),'land_fraction_sum_max_error':err,'scientific_acceptance':False}))

def main():
    parser=argparse.ArgumentParser(description='Prepare the tested v35l artificial operating point and radiation formats; no network or model run.')
    for key in ['root','output','uv-netcdf','toms-bpch','legacy-restart','cn-netcdf']:
        parser.add_argument('--'+key,required=True)
    parser.add_argument('--start-utc',default='2026-10-26T03:00:00Z')
    prepare(parser.parse_args())

if __name__ == "__main__":
    main()
