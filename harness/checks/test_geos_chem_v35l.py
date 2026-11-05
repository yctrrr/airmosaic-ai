"""Bounded synthetic checks of the beginner helpers; no model/data downloads."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / 'skills/model/03_atmospheric_transport/geos-chem/scripts'
sys.path.insert(0, str(SCRIPTS))
import configure_run as config
import check_v35l_gradients as gradient
import prepare_v35l as profile
import run_v35l as runner


def fixture(tmp_path, mode='adjoint'):
    root=tmp_path/'sandbox';root.mkdir()
    source=root/'source';source.mkdir();data=root/'data';data.mkdir()
    if mode=='adjoint':
        tables=source/'runs/v8-02-01/geos5';tables.mkdir(parents=True)
        for n in config.STATIC:(tables/n).write_text('synthetic '+n)
        restart=root/'initial.bpch';restart.write_bytes(b'synthetic')
        settings=dict(start_utc='2026-10-26T03:00:00Z',end_utc='2026-10-26T06:00:00Z',
                      data_root=str(data),restart_file=str(restart),control_tracer=1,response_tracer=2,fd_steps=[.1,.03,.01])
    else:
        tables=source/'src/GEOS-Chem/run/shared';tables.mkdir(parents=True)
        for n in ('species_database.yml','download_data.py','download_data.yml'):(tables/n).write_text('synthetic')
        settings=dict(start_utc='2019-01-01T00:00:00Z',end_utc='2019-01-01T01:00:00Z',data_root=str(data))
    return root,source,settings


@pytest.mark.parametrize('mode',['classic','adjoint'])
def test_render_native_templates_and_refuse_overwrite(tmp_path,mode):
    root,source,s=fixture(tmp_path,mode);run=root/'prepared'
    assert config.configure(root,source,run,s,mode)['mode']=='plan_only'
    assert not run.exists()
    receipt=config.configure(root,source,run,s,mode,True)
    assert receipt['model_executed'] is False
    for p in run.rglob('*'):
        if p.is_file() and p.suffix!='.json':assert '@DATA_ROOT@' not in p.read_text()
    if mode=='adjoint':
        adj=(run/'step_0p1/input.gcadj').read_text()
        assert '=> w/LICS: tracer     ICSFD   : 1' in adj
        assert (run/'step_0p1/ITER').read_text()=='1\n3\n'
        for n,size in [('FEB',29),('NOV',30),('OCT',31)]:
            line=next(x for x in (run/'step_0p1/input.geos').read_text().splitlines() if x.startswith('Schedule output for '+n))
            assert len(line[26:])==size
    with pytest.raises(ValueError,match='fresh_run'):config.configure(root,source,run,s,mode,True)


@pytest.mark.parametrize('changes',[
    {'control_tracer':44},{'response_tracer':True},{'fd_steps':[.01,.03,.1]},
    {'fd_steps':[.1,.1,.01]},{'fd_steps':[.1,float('nan'),.01]},
    {'end_utc':'2026-10-27T06:00:00Z'},{'unknown':1},
])
def test_invalid_settings_fail_before_write(tmp_path,changes):
    root,source,s=fixture(tmp_path);s.update(changes)
    with pytest.raises((ValueError,TypeError)):config.configure(root,source,root/'run',s,'adjoint',True)
    assert not (root/'run').exists()


def test_changed_control_response_uses_both_native_menus(tmp_path):
    root,source,s=fixture(tmp_path);s.update(control_tracer=4,response_tracer=26)
    config.configure(root,source,root/'run',s,'adjoint',True)
    adj=(root/'run/step_0p1/input.gcadj').read_text()
    assert 'ICSFD   : 4' in adj and 'NFD     : 26' in adj
    assert 'Tracer #1                      : 4    CO' in adj
    assert 'Tracer #1                      : 26    SO2' in adj


def test_close_perturbations_keep_three_distinct_native_cases(tmp_path):
    root,source,s=fixture(tmp_path)
    s['fd_steps']=[.10000002,.10000001,.01]
    prepared=root/'prepared'
    config.configure(root,source,prepared,s,'adjoint',True)
    names={p.name for p in prepared.glob('step_*')}
    assert names=={'step_0p10000002','step_0p10000001','step_0p01'}
    for h in s['fd_steps']:
        adj=(prepared/('step_'+repr(h).replace('.', 'p'))/'input.gcadj').read_text()
        assert float(next(line.rsplit(':',1)[1] for line in adj.splitlines()
                          if 'fd perturbation        FD_DIFF' in line))==h
    binary=root/'geos';binary.write_bytes(b'not executed')
    assert runner.run_cases(root,binary,prepared,root/'output')['cases']==9


def test_profile_resource_hashes_survive_autocrlf_checkout(tmp_path):
    repo=Path(__file__).resolve().parents[2]
    checkout=tmp_path/'checkout';checkout.mkdir()
    relative=Path('skills/model/03_atmospheric_transport/geos-chem/templates/adjoint_v35l')
    (checkout/relative).mkdir(parents=True)
    (checkout/'.gitattributes').write_bytes((repo/'.gitattributes').read_bytes())
    names=('chemistry-component.patch','module-dependencies.mk')
    for name in names:
        (checkout/relative/name).write_bytes((repo/relative/name).read_bytes())
    def git(*args):
        subprocess.run(['git','-C',str(checkout),'-c','core.autocrlf=true',*args],
                       check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    git('init','-q');git('add','.')
    git('-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','-qm','synthetic')
    for name in names:(checkout/relative/name).unlink()
    git('checkout','--','.')
    manifest=json.loads((repo/relative/'profile-manifest.json').read_text())
    for name,key in zip(names,('patch_sha256','dependencies_sha256')):
        assert profile.digest(checkout/relative/name)==manifest[key]


def rows():
    return [dict(step=h,i=i,j=1,base_Ox_kg=1,plus_Ox_kg=(1+h)**2,
                 minus_Ox_kg=(1-h)**2,adjoint=2) for h in (.1,.03,.01) for i in (1,2)]


def test_gradient_checks_reject_wrong_and_zero_derivatives():
    r=rows();assert gradient.compare(r)['numerical_check_passed']
    for x in r:x['adjoint']=9
    assert not gradient.compare(r)['numerical_check_passed']
    for x in r:x.update(adjoint=0,plus_Ox_kg=1,minus_Ox_kg=1)
    assert not gradient.compare(r)['numerical_check_passed']


@pytest.mark.parametrize('mutation',['duplicate','missing_cell','nonfinite'])
def test_gradient_refuses_invalid_support(mutation):
    r=rows()
    if mutation=='duplicate':r.append(copy.copy(r[0]))
    elif mutation=='missing_cell':r.pop()
    else:r[0]['base_Ox_kg']=float('nan')
    with pytest.raises(ValueError):gradient.compare(r)


def test_profile_records_source_changes_without_old_hash_restriction(tmp_path):
    code=tmp_path/'code';code.mkdir();(code/'a.f').write_text('changed')
    result=profile.profile_members(code,{'changed_files':[{'path':'a.f','before_sha256':'0'*64}]})
    assert result[0]['sha256']!='0'*64
    (code/'a.f').unlink()
    with pytest.raises(ValueError,match='member_missing'):
        profile.profile_members(code,{'changed_files':[{'path':'a.f'}]})


@pytest.mark.parametrize('applicable',[True,False])
def test_profile_uses_patch_context_instead_of_historical_commit(tmp_path,monkeypatch,applicable):
    root=tmp_path/'sandbox';root.mkdir();source=root/'source';code=source/'code';code.mkdir(parents=True)
    # A newer revision adds content outside the patch's context. Neither its
    # commit nor its file hashes should have to match a historical checkout.
    original=('old\nretained\n' if applicable else 'incompatible\nchanged\n')+'new revision comment\n'
    (code/'a.f').write_text(original,encoding='utf-8',newline='\n')
    def git(*args):return subprocess.check_output(['git','-C',str(source),*args],stderr=subprocess.STDOUT)
    git('init','-q');git('add','code/a.f')
    git('-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','-qm','new source revision')
    resources=root/'resources';resources.mkdir()
    patch=resources/'chemistry-component.patch'
    patch.write_text('diff --git a/a.f b/a.f\n--- a/a.f\n+++ b/a.f\n@@ -1,2 +1,2 @@\n-old\n+new\n retained\n',encoding='utf-8',newline='\n')
    deps=resources/'module-dependencies.mk';deps.write_text('# synthetic\n',encoding='utf-8',newline='\n')
    manifest={'model_version':'v35l','profile':'synthetic','patch_sha256':profile.digest(patch),
              'dependencies_sha256':profile.digest(deps),
              'changed_files':[{'path':'a.f','before_sha256':'0'*64,'after_sha256':'0'*64}]}
    (resources/'profile-manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(profile,'RESOURCES',resources)
    out=root/'prepared'
    if applicable:
        result=profile.prepare(root,source,out,True,model_version='v35m')
        assert result['model_version']=='v35m' and result['patch_applicability']=='passed'
        assert result['reference_file_hashes_match'] is False
        assert result['source_identity']['commit']==git('rev-parse','HEAD').decode().strip()
        assert (out/'a.f').read_text()=='new\nretained\nnew revision comment\n'
    else:
        with pytest.raises(subprocess.CalledProcessError):profile.prepare(root,source,out,True)
        assert not (out/'profile-receipt.json').exists()
    assert (code/'a.f').read_text()==original


@pytest.mark.parametrize('failure',[None,'stale_restart','exit','timeout'])
def test_native_three_invocation_protocol_and_failure_preservation(tmp_path,monkeypatch,failure):
    root,source,s=fixture(tmp_path);prepared=root/'prepared'
    config.configure(root,source,prepared,s,'adjoint',True)
    binary=root/'geos';binary.write_bytes(b'not executed')
    resource=types.SimpleNamespace(RLIMIT_STACK=1,RLIM_INFINITY=-1,getrlimit=lambda _:(-1,-1))
    monkeypatch.setitem(sys.modules,'resource',resource)
    for key,value in {'OMP_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','SLURM_CPUS_PER_TASK':'4'}.items():monkeypatch.setenv(key,value)
    seen=[]
    def fake(cmd,cwd,stdout,**kwargs):
        it=int((cwd/'ITER').read_text().splitlines()[0]);seen.append((cwd.parent.name,it))
        assert (cwd/'ITER').read_text()==f'{it}\n3\n'
        if failure=='timeout':raise subprocess.TimeoutExpired(cmd,1)
        (cwd/'OptData'/f'cfn.{it:02d}').write_text('1')
        if not (failure=='stale_restart' and it==2):(cwd/'restart.output.component.synthetic').write_bytes(b'new')
        (cwd/'ITER').write_text(str(it)+'\n')
        stdout.write(b'F I N I S H   I T E R A T I O N\n')
        return types.SimpleNamespace(returncode=1 if failure=='exit' else 0)
    monkeypatch.setattr(runner.subprocess,'run',fake)
    output=root/'execution'
    if failure:
        with pytest.raises((ValueError,subprocess.TimeoutExpired)):runner.run_cases(root,binary,prepared,output,True)
        state=json.loads((output/'run-status.json').read_text())
        assert state['mode']=='stopped_preserved'
        if failure=='stale_restart':assert len(seen)==2
    else:
        state=runner.run_cases(root,binary,prepared,output,True)
        assert state['mode']=='native_cases_complete' and len(seen)==9
        assert seen==[(h,it) for h in ('step_0p1','step_0p03','step_0p01') for it in (1,2,3)]
    assert (prepared/'step_0p1/ITER').read_text()=='1\n3\n'


def test_radiation_weights_and_bpch_roundtrip(tmp_path):
    np=pytest.importorskip('numpy');pytest.importorskip('netCDF4')
    from prepare_v35l_inputs import lat_weights
    from v35l_bpch import block,read,write
    edges=np.r_[-90.,np.arange(-89.5,90.,1.),90.]
    target=np.r_[-90.,np.arange(-88.,90.,4.),90.]
    w=lat_weights(edges,target)
    assert np.max(np.abs(w.sum(axis=1)-1))<1e-12
    source=np.arange(len(edges)-1,dtype=float)
    assert np.allclose(w@np.ones_like(source),1)
    s_area=np.diff(np.sin(np.deg2rad(edges)));t_area=np.diff(np.sin(np.deg2rad(target)))
    assert np.isclose(np.sum(source*s_area),np.sum((w@source)*t_area),rtol=1e-12)
    data=np.arange(24,dtype='f4').reshape(4,3,2)
    p=tmp_path/'synthetic.bpch';write(p,'synthetic',[block('GEOS1',5,4,'IJ-CHK-$',2,'kg/box',1,2,data)])
    title,values=read(p)
    assert np.array_equal(values[0]['data'],data)
    assert values[0]['header'][1:5]==[2,b'kg/box'.ljust(40),1,2]
    assert gradient.blocks(p)[0]['shape']==[4,3,2]
    p.write_bytes(p.read_bytes()[:-1])
    with pytest.raises(ValueError,match='truncated'):gradient.blocks(p)
