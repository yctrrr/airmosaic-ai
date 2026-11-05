"""Create the documented Classic 14.8.0 transport smoke preset; no data retrieval."""
import argparse,json,os,re,shlex,shutil,subprocess,sys
from pathlib import Path
from gc_paths import sandbox_root,within,bounded_links,save_new


def prepare(root,source,run,data,execute=False,model_version='14.8.0'):
    root=sandbox_root(root);source=within(root,source,must_exist=True)
    run=within(root,run);data=within(root,data,must_exist=True)
    if run.exists():raise ValueError('fresh_run_required')
    bounded_links(root,source)
    from build_classic import classic_version,source_identity
    classic_version(source,model_version)
    template=within(root,source/'src/GEOS-Chem/run/GCClassic',must_exist=True)
    shared=within(root,template.parent/'shared',must_exist=True)
    settings=[shared/'settings'/n for n in ('4x5.txt','global_grid.txt','gmao_hemco.txt','merra2.txt')]
    for p in settings+[template/'init_rd.sh']:
        if not p.is_file():raise ValueError('upstream_template_missing')
    if not execute:return {'mode':'plan_only','preset':'transport_20190101_1h','filesystem_writes':False}
    if os.name!='posix':raise ValueError('posix_required')
    identity=source_identity(source)
    run.mkdir(parents=True);(run/'Restarts').mkdir()
    values={'RUNDIR_DATA_ROOT':str(data),'RUNDIR_SIM_NAME':'TransportTracers',
        'RUNDIR_MET_FIELD_CONFIG':'HEMCO_Config.rc.gmao_metfields','RUNDIR_GCAP2_VERTRES':'47',
        'RUNDIR_GCAP2_SCENARIO':'not_used','RUNDIR_GCAP2_RUNID':'not_used',
        'RUNDIR_SIM_START_DATE':'20190101','RUNDIR_SIM_END_DATE':'20190101',
        'RUNDIR_SIM_START_TIME':'000000','RUNDIR_SIM_END_TIME':'010000','RUNDIR_GRID_NLEV':'47',
        'RUNDIR_GRID_HALF_POLAR':'true','RUNDIR_CENTER_LON_180':'true',
        'RUNDIR_TRANSPORT_TS':'600','RUNDIR_CHEMISTRY_TS':'1200',
        'RUNDIR_USE_NLPBL':'true','RUNDIR_READ_RESTART_AS_REAL8':'false',
        'RUNDIR_USE_GCCLASSIC_TIMERS':'false','RUNDIR_MET_AVAIL':'# 1980-2021',
        'RUNDIR_HIST_TIME_AVG_DUR':'00000000 010000','RUNDIR_HIST_TIME_AVG_FREQ':'00000000 010000'}
    base=run/'rundir-vars.sh'
    base.write_text('\n'.join(k+'='+shlex.quote(v) for k,v in values.items())+'\n')
    (run/'runScriptSamples').symlink_to(template/'runScriptSamples',target_is_directory=True)
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','LANG','LC_ALL'}}
    with (run/'prepare.log').open('x') as log:
        result=subprocess.run(['bash',str(template/'init_rd.sh'),str(base)]+[str(p) for p in settings]+[str(base)],
            cwd=str(run),env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    if result.returncode:raise ValueError('upstream_template_render_failed')
    for name in ('geoschem_config.yml','HEMCO_Config.rc','HISTORY.rc','HEMCO_Config.rc.gmao_metfields'):
        if re.search(r'\$\{?RUNDIR_[A-Z0-9_]+',(run/name).read_text()):
            raise ValueError('unresolved_template_variable')
    for name in ('species_database.yml','download_data.py','download_data.yml'):
        shutil.copyfile(str(shared/name),str(run/name))
    (run/'CodeDir').symlink_to(source,target_is_directory=True)
    bounded_links(root,run)
    receipt={'preset':'transport_20190101_1h','model_version':model_version,'source_identity':identity,'simulation':'TransportTracers',
        'grid':'4x5','levels':47,'meteorology':'MERRA2','start_utc':'2019-01-01T00:00:00Z',
        'end_utc':'2019-01-01T01:00:00Z','input_downloaded':False,'personal_registration':False}
    save_new(run/'prepare-receipt.json',receipt)
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('root','source','run','data'):p.add_argument('--'+key,required=True)
    p.add_argument('--version',default='14.8.0')
    p.add_argument('--execute',action='store_true');a=p.parse_args()
    try:print(json.dumps(prepare(a.root,a.source,a.run,a.data,a.execute,a.version)))
    except Exception as e:print(json.dumps({'status':'failed','error_type':type(e).__name__}));return 1
    return 0
if __name__=='__main__':sys.exit(main())
