"""Plan or build a version-selected Classic checkout in a fresh external sandbox.

The caller loads a compatible compiler/NetCDF environment and supplies the
authorized compute allocation. This trusted helper neither SSHs nor submits
jobs, installs packages, registers a user or enables a run-tool adapter.
"""
import argparse
import hashlib
from datetime import datetime,timezone
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import time

from gc_paths import digest,sandbox_root,within,save_new,save_state,bounded_links


def classic_version(source, requested):
    if not isinstance(requested,str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:[-.][A-Za-z0-9.-]+)?',requested):
        raise ValueError('model_version_number_required')
    text=(Path(source)/'CMakeLists.txt').read_text(encoding='utf-8')
    match=re.search(r'project\s*\(\s*GCClassic\s+VERSION\s+([^\s)]+)',text,re.I)
    if not match or match.group(1)!=requested:
        raise ValueError('classic_model_version_mismatch')
    return requested


def source_identity(source):
    result={}
    for key,args in [('commit',['rev-parse','HEAD']),('description',['describe','--tags','--always'])]:
        value=subprocess.run(['git','-C',str(source)]+args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=15)
        result[key]=value.stdout.strip() if value.returncode==0 else None
    return result


def plan_build(root,source,build,*,model_version='14.8.0',jobs,max_seconds,fc,cc,cxx,netcdf_prefix=None,cmake='cmake'):
    root=sandbox_root(root);source=within(root,source,must_exist=True);build=within(root,build)
    if not (source/'CMakeLists.txt').is_file():raise ValueError('classic_cmake_source_required')
    bounded_links(root,source)
    if build.exists():raise ValueError('fresh_build_directory_required')
    if (not isinstance(jobs,int) or isinstance(jobs,bool) or not 1<=jobs<=4
            or not isinstance(max_seconds,int) or isinstance(max_seconds,bool) or not 1<=max_seconds<=3600):
        raise ValueError('build_resource_limit')
    classic_version(source,model_version)
    if any(not value or any(c in value for c in '\r\n\x00') for value in (fc,cc,cxx)):
        raise ValueError('explicit_compiler_names_required')
    netcdf_options=[]
    if netcdf_prefix is not None:
        prefix=Path(netcdf_prefix).expanduser().resolve()
        required={'NETCDF_C_LIBRARY':prefix/'lib/libnetcdf.so',
            'NETCDF_F_LIBRARY':prefix/'lib/libnetcdff.so','NETCDF_C_INCLUDE_DIR':prefix/'include',
            'NETCDF_F90_INCLUDE_DIR':prefix/'include','NETCDF_F77_INCLUDE_DIR':prefix/'include'}
        if not all(p.exists() for p in required.values()):raise ValueError('combined_netcdf_prefix_incomplete')
        netcdf_options=['-D'+k+'='+str(v) for k,v in required.items()]
    return {'root':root,'source':source,'build':build,'model_version':model_version,
        'jobs':jobs,'max_seconds':max_seconds,'compilers':{'FC':fc,'CC':cc,'CXX':cxx},
        'commands':[[cmake,'-S',str(source),'-B',str(build),'-DMECH=fullchem',
                     '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_Fortran_COMPILER='+fc,
                     '-DCMAKE_C_COMPILER='+cc,'-DCMAKE_CXX_COMPILER='+cxx]+netcdf_options,
                    [cmake,'--build',str(build),'--parallel',str(jobs)]]}


def _environment(spec):
    allowed={'PATH','HOME','LD_LIBRARY_PATH','LIBRARY_PATH','CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH',
        'NETCDF_HOME','NETCDF_ROOT','NETCDF_FORTRAN_ROOT','CMAKE_PREFIX_PATH','PKG_CONFIG_PATH',
        'INTEL_LICENSE_FILE','NLSPATH','TMPDIR','LANG','LC_ALL'}
    env={name:value for name,value in os.environ.items() if name in allowed}
    env.update(spec['compilers'])
    env.update({'OMP_NUM_THREADS':str(spec['jobs']),'MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    env['TMPDIR']=str(spec['build']/'tmp')
    return env


def verify_checkout(root,source):
    """Compare build contents to committed blobs, including every submodule.

    Content comparison also works after moving a checkout between filesystems;
    the originating platform's index stat cache is not evidence of a change.
    """
    bounded_links(root,source)
    tree=subprocess.check_output(['git','-C',str(source),'ls-tree','-rz','--full-tree','HEAD'],timeout=30)
    for entry in tree.split(b'\0'):
        if not entry:continue
        metadata,name=entry.split(b'\t',1);mode,kind,expected=metadata.split()
        path=within(root,source/os.fsdecode(name),must_exist=True)
        if kind==b'commit':
            actual=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],timeout=15).strip()
            if actual!=expected:raise ValueError('submodule_commit_mismatch')
            verify_checkout(root,path)
        else:
            original=source/os.fsdecode(name)
            if mode==b'120000':
                if not original.is_symlink():raise ValueError('source_link_type_mismatch')
                payload=os.fsencode(os.readlink(str(original)))
                checksum=hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
            else:
                if original.is_symlink() or not path.is_file():raise ValueError('source_file_type_mismatch')
                value=hashlib.sha1();value.update(b'blob '+str(path.stat().st_size).encode()+b'\0')
                with path.open('rb') as stream:
                    for chunk in iter(lambda:stream.read(1024*1024),b''):value.update(chunk)
                checksum=value.hexdigest()
            if checksum.encode()!=expected:raise ValueError('source_blob_mismatch')
    extra=subprocess.check_output(['git','-C',str(source),'ls-files','--others','--exclude-standard'],timeout=30)
    if extra.strip():raise ValueError('untracked_source_files_present')


def execute_build(spec):
    if os.name!='posix':raise ValueError('build_requires_posix_compute_environment')
    allocated=os.environ.get('SLURM_CPUS_PER_TASK')
    if allocated is not None and int(allocated)<spec['jobs']:raise ValueError('insufficient_allocated_cpus')
    classic_version(spec['source'],spec['model_version'])
    identity=source_identity(spec['source'])
    if not identity['commit']:raise ValueError('source_checkout_required')
    modules=subprocess.run(['git','-C',str(spec['source']),'submodule','status','--recursive'],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=15)
    if modules.returncode or any(line[:1] in {'-','+','U'} for line in modules.stdout.splitlines()):
        raise ValueError('source_submodule_state_mismatch')
    verify_checkout(spec['root'],spec['source'])
    spec['build'].mkdir(parents=True);(spec['build']/'tmp').mkdir()
    provenance={'started_at':datetime.now(timezone.utc).isoformat(),'model_version':spec['model_version'],'source_identity':identity,
        'submodules':modules.stdout.splitlines(),'threads':spec['jobs'],'max_seconds':spec['max_seconds'],
        'compiler_names':spec['compilers'],'status':'running','scientific_validation':False}
    save_new(spec['build']/'build-receipt.json',provenance)
    begin=time.monotonic();env=_environment(spec)
    try:
        for i,command in enumerate(spec['commands'],1):
            remaining=spec['max_seconds']-(time.monotonic()-begin)
            if remaining<=0:raise TimeoutError('build_walltime_limit')
            with (spec['build']/('stage-'+str(i)+'.log')).open('x') as log:
                process=subprocess.Popen(command,cwd=str(spec['root']),env=env,stdout=log,
                    stderr=subprocess.STDOUT,start_new_session=True)
                try:exit_code=process.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGTERM)
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                    raise TimeoutError('build_walltime_limit')
            if exit_code:raise ValueError('cmake_stage_failed_'+str(i))
        binary=within(spec['root'],spec['build']/'bin/gcclassic',must_exist=True)
        if not binary.is_file() or not binary.stat().st_size:raise ValueError('compiled_binary_missing')
        provenance.update(status='complete',binary_sha256=digest(binary),binary_bytes=binary.stat().st_size)
    except Exception as error:
        provenance.update(status='failed',error_type=type(error).__name__)
        raise
    finally:
        provenance['elapsed_seconds']=time.monotonic()-begin
        save_state(spec['build']/'build-receipt.json',provenance)
    return provenance


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True);p.add_argument('--source',required=True);p.add_argument('--build',required=True)
    p.add_argument('--version',default='14.8.0',help='Model version declared by GCClassic, such as 14.8.0')
    p.add_argument('--jobs',type=int,default=1)
    p.add_argument('--max-seconds',type=int,default=3600)
    p.add_argument('--fc',required=True);p.add_argument('--cc',required=True);p.add_argument('--cxx',required=True)
    p.add_argument('--netcdf-prefix',help='Optional combined C/Fortran installation with include/ and lib/')
    p.add_argument('--cmake',default='cmake',help='Executable, independently of the compiler PATH')
    p.add_argument('--execute',action='store_true');args=p.parse_args()
    try:
        spec=plan_build(args.root,args.source,args.build,model_version=args.version,jobs=args.jobs,
            max_seconds=args.max_seconds,fc=args.fc,cc=args.cc,cxx=args.cxx,netcdf_prefix=args.netcdf_prefix,cmake=args.cmake)
        if args.execute:
            result=execute_build(spec)
            print(json.dumps({'stage':'classic_build','status':result['status'],'binary_bytes':result['binary_bytes'],
                'binary_sha256':result['binary_sha256'],'scientific_validation':False}))
        else:print(json.dumps({'mode':'plan_only','commands':len(spec['commands']),'threads':spec['jobs'],
                               'max_seconds':spec['max_seconds'],'filesystem_writes':False}))
    except Exception as error:
        print(json.dumps({'status':'failed','error_type':type(error).__name__}));return 1
    return 0

if __name__=='__main__':sys.exit(main())
