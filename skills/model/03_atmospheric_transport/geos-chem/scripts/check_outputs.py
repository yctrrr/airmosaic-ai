"""Check the transport smoke's NetCDF fields through an installed NetCDF-C library.

Uses ctypes and the Python standard library; loading the explicitly selected
trusted library executes its native code under the caller's permissions.
"""
import argparse,ctypes,json,math,re,sys
from datetime import datetime,timedelta,timezone
from gc_paths import sandbox_root,within,digest,save_new

# Public 47-level hybrid coefficients: GEOS-Chem 14.8.0
# GeosUtil/pressure_mod.F90, Ap/Bp reduced grid; eta at reference Ps=1000 hPa.
AP=[0,.04804826,6.593752,13.1348,19.61311,26.09201,32.57081,38.98201,
    45.33901,51.69611,58.05321,64.36264,70.62198,78.83422,89.09992,99.36521,
    109.1817,118.9586,128.6959,142.91,156.26,169.609,181.619,193.097,
    203.259,212.15,218.776,223.898,224.363,216.865,201.192,176.93,
    150.393,127.837,108.663,92.36572,78.51231,56.38791,40.17541,28.36781,
    19.7916,9.292942,4.076571,1.65079,.6167791,.211349,.06600001,.01]
BP=[1,.984952,.963406,.941865,.920387,.898908,.877429,.856018,.8346609,
    .8133039,.7919469,.7706375,.7493782,.721166,.6858999,.6506349,
    .6158184,.5810415,.5463042,.4945902,.4437402,.3928911,.3433811,
    .2944031,.2467411,.2003501,.1562241,.1136021,.06372006,.02801004,
    .006960025,8.175413e-9]+[0]*16
SPECIES={'Rn222','Pb210','Pb210s','Be7','Be7s','Be10','Be10s','aoa','aoa_bl',
    'aoa_nh','CH3I','CO_25','CO_50','e90','e90_n','e90_s','nh_5','nh_50',
    'PassiveTracer','SF6','st80_25'}

def expected_coordinates():
    return {'lat':[-89]+[-86+4*i for i in range(44)]+[89],
        'lon':[-180+5*i for i in range(72)],
        'lev':[(AP[i]+AP[i+1])/2000+(BP[i]+BP[i+1])/2 for i in range(47)]}

class NetCDF:
    def __init__(self,library,path):
        self.lib=ctypes.CDLL(library);self.id=ctypes.c_int()
        self.check(self.lib.nc_open(str(path).encode(),0,ctypes.byref(self.id)))
    def check(self,code):
        if code:raise ValueError('netcdf_error_'+str(code))
    def close(self):self.check(self.lib.nc_close(self.id))
    def varid(self,name):
        value=ctypes.c_int();self.check(self.lib.nc_inq_varid(self.id,name.encode(),ctypes.byref(value)));return value
    def text(self,name,attribute):
        var=self.varid(name) if name is not None else -1;size=ctypes.c_size_t()
        self.check(self.lib.nc_inq_attlen(self.id,var,attribute.encode(),ctypes.byref(size)))
        if size.value>4096:raise ValueError('oversize_attribute')
        result=ctypes.create_string_buffer(size.value+1)
        self.check(self.lib.nc_get_att_text(self.id,var,attribute.encode(),result))
        return result.value.decode()
    def dimension(self,name):
        dim=ctypes.c_int();size=ctypes.c_size_t()
        self.check(self.lib.nc_inq_dimid(self.id,name.encode(),ctypes.byref(dim)))
        self.check(self.lib.nc_inq_dimlen(self.id,dim,ctypes.byref(size)));return size.value
    def values(self,name):
        var=self.varid(name);ndims=ctypes.c_int();self.check(self.lib.nc_inq_varndims(self.id,var,ctypes.byref(ndims)))
        if not 0<=ndims.value<=8:raise ValueError('unsupported_variable_dimensions')
        dims=(ctypes.c_int*ndims.value)();self.check(self.lib.nc_inq_vardimid(self.id,var,dims))
        count=1
        for dim in dims:
            size=ctypes.c_size_t();self.check(self.lib.nc_inq_dimlen(self.id,dim,ctypes.byref(size)));count*=size.value
        if not 0<count<=5000000:raise ValueError('smoke_variable_size_limit')
        data=(ctypes.c_double*count)();self.check(self.lib.nc_get_var_double(self.id,var,data))
        result=list(data)
        if not all(math.isfinite(x) and abs(x)<1e30 for x in result):raise ValueError('nonfinite_or_fill_values')
        return result
    def dimensions(self,name):
        var=self.varid(name);ndims=ctypes.c_int();self.check(self.lib.nc_inq_varndims(self.id,var,ctypes.byref(ndims)))
        if not 0<=ndims.value<=8:raise ValueError('unsupported_variable_dimensions')
        dims=(ctypes.c_int*ndims.value)();self.check(self.lib.nc_inq_vardimid(self.id,var,dims));result=[]
        for dim in dims:
            buf=ctypes.create_string_buffer(257);self.check(self.lib.nc_inq_dimname(self.id,dim,buf));result.append(buf.value.decode())
        return tuple(result)
    def variables(self):
        count=ctypes.c_int();self.check(self.lib.nc_inq_nvars(self.id,ctypes.byref(count)))
        names=[]
        for i in range(count.value):
            buf=ctypes.create_string_buffer(257);self.check(self.lib.nc_inq_varname(self.id,i,buf));names.append(buf.value.decode())
        return names

def cf_times(values,units):
    match=re.fullmatch(r'(seconds|minutes|hours|days) since (\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})(?:\.0+)?(?: UTC|Z)?',units)
    if not match:raise ValueError('unsupported_cf_time_units')
    origin=datetime.strptime(match[2]+' '+match[3],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    factor={'seconds':1,'minutes':60,'hours':3600,'days':86400}[match[1]]
    return [origin+timedelta(seconds=x*factor) for x in values]

def check_history(path):
    text=path.read_text()
    for key in ('frequency','duration'):
        if not re.search(r'^\s*SpeciesConc\.'+key+r':\s*00000000\s+010000\s*,?\s*$',text,re.M):
            raise ValueError('one_hour_history_contract_required')
    if not re.search(r"^\s*SpeciesConc\.mode:\s*'time-averaged'\s*,?\s*$",text,re.M):
        raise ValueError('time_averaged_history_required')
    return digest(path)

def check_file(library,path,prefix,expected_units,start,end,restart=False):
    data=NetCDF(library,path)
    try:
        dims={k:data.dimension(k) for k in ('lat','lon','lev')}
        if dims!={'lat':46,'lon':72,'lev':47}:raise ValueError('smoke_grid_mismatch')
        for coord,expected in expected_coordinates().items():
            actual=data.values(coord)
            if data.dimensions(coord)!=(coord,) or len(actual)!=len(expected) or any(
                    not math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-9) for a,b in zip(actual,expected)):
                raise ValueError('smoke_coordinate_mismatch')
        for attribute,expected in [('simulation_start_date_and_time',start),('simulation_end_date_and_time',end)]:
            timestamp=datetime.strptime(data.text(None,attribute),'%Y-%m-%d %H:%M:%Sz').replace(tzinfo=timezone.utc)
            if timestamp!=expected:raise ValueError('simulation_period_mismatch')
        if data.text('time','calendar') not in {'gregorian','standard','proleptic_gregorian'}:
            raise ValueError('unsupported_time_calendar')
        units=data.text('time','units');times=cf_times(data.values('time'),units)
        if data.dimensions('time')!=('time',) or times!=[end if restart else start]:
            raise ValueError('diagnostic_or_restart_time_mismatch')
        fields=[n for n in data.variables() if n.startswith(prefix)]
        if {n[len(prefix):] for n in fields}!=SPECIES:raise ValueError('transport_species_set_mismatch')
        summaries={}
        for name in fields:
            if data.dimensions(name)!=('time','lev','lat','lon'):raise ValueError('species_dimensions_mismatch')
            if data.text(name,'units') not in expected_units:raise ValueError('species_unit_mismatch')
            if data.text(name,'averaging_method')!=('instantaneous' if restart else 'time-averaged'):
                raise ValueError('species_averaging_method_mismatch')
            values=data.values(name)
            summaries[name]={'count':len(values),'min':min(values),'max':max(values)}
        return {'sha256':digest(path),'bytes':path.stat().st_size,'grid':dims,
            'times_utc':[t.isoformat() for t in times],'fields':summaries,'scientific_validation':False}
    finally:data.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('root','library','concentration','restart','history','output'):p.add_argument('--'+key,required=True)
    p.add_argument('--unit',action='append',required=True,help='Expected unit from the selected species contract')
    a=p.parse_args()
    try:
        root=sandbox_root(a.root);start=datetime(2019,1,1,tzinfo=timezone.utc);end=start+timedelta(hours=1)
        history_sha=check_history(within(root,a.history,must_exist=True))
        conc=check_file(a.library,within(root,a.concentration,must_exist=True),'SpeciesConcVV_',a.unit,start,end)
        restart=check_file(a.library,within(root,a.restart,must_exist=True),'SpeciesRst_',a.unit,start,end,True)
        result={'preset':'transport_20190101_1h','concentration':conc,'restart':restart,'technical_check_passed':True,
            'interval_start_utc':start.isoformat(),'interval_end_utc':end.isoformat(),'history_sha256':history_sha,
            'interval_basis':'simulation_global_attributes_start_timestamp_averaging_method_and_history'}
        save_new(within(root,a.output),result)
        print(json.dumps({'technical_check_passed':True,'concentration_fields':len(conc['fields']),
            'restart_fields':len(restart['fields']),'scientific_validation':False}));return 0
    except Exception as e:print(json.dumps({'status':'failed','error_type':type(e).__name__}));return 1
if __name__=='__main__':sys.exit(main())
