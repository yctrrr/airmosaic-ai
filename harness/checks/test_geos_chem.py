"""Synthetic path, provenance and derivative checks; no model inputs or SSH."""
import importlib.util
from pathlib import Path
import subprocess,sys
import pytest

SCRIPTS=Path(__file__).resolve().parents[2]/'skills/model/03_atmospheric_transport/geos-chem/scripts'
sys.path.insert(0,str(SCRIPTS))
import gc_paths
import build_classic
import prepare_classic
import bounded_inputs
import check_outputs
from datetime import datetime,timezone

def tree(tmp_path):
    root=tmp_path/'sandbox';root.mkdir();source=root/'source';source.mkdir()
    (source/'CMakeLists.txt').write_text('project(GCClassic VERSION 14.8.0)')
    return root,source

def spec(root,source,**extra):
    values=dict(model_version='14.8.0',jobs=2,max_seconds=60,fc='ifort',cc='icc',cxx='icpc')
    values.update(extra)
    return build_classic.plan_build(root,source,'build',**values)

def test_plan_does_not_create_build(tmp_path):
    root,source=tree(tmp_path)
    value=spec(root,source)
    assert value['commands'][0][0]=='cmake'
    assert not (root/'build').exists()

@pytest.mark.parametrize('args',[{'jobs':5},{'jobs':True},{'max_seconds':3601},{'model_version':'main'}])
def test_limits(tmp_path,args):
    root,source=tree(tmp_path)
    with pytest.raises(ValueError):spec(root,source,**args)


def test_classic_new_version_requires_its_model_number_not_old_commit(tmp_path):
    root,source=tree(tmp_path)
    (source/'CMakeLists.txt').write_text('project(GCClassic VERSION 14.9.0)')
    with pytest.raises(ValueError,match='version_mismatch'):spec(root,source)
    assert spec(root,source,model_version='14.9.0')['model_version']=='14.9.0'

def test_escape_and_repository_root(tmp_path):
    root,source=tree(tmp_path)
    with pytest.raises(ValueError):gc_paths.within(root,'../escape')
    with pytest.raises(ValueError):gc_paths.within(root,root)
    (tmp_path/'.git').mkdir()
    with pytest.raises(ValueError):gc_paths.sandbox_root(root)

def test_existing_build_refused(tmp_path):
    root,source=tree(tmp_path);(root/'build').mkdir()
    with pytest.raises(ValueError):spec(root,source)

def test_internal_link_escape(tmp_path):
    root,source=tree(tmp_path);outside=tmp_path/'outside';outside.write_text('other')
    try:(source/'linked.f90').symlink_to(outside)
    except OSError:pytest.skip('symlink privilege unavailable')
    with pytest.raises(ValueError):spec(root,source)

def test_child_environment_excludes_secrets(tmp_path,monkeypatch):
    root,source=tree(tmp_path);monkeypatch.setenv('AWS_SECRET_ACCESS_KEY','synthetic-secret')
    monkeypatch.setenv('SSH_AUTH_SOCK','synthetic-socket')
    env=build_classic._environment(spec(root,source))
    assert 'AWS_SECRET_ACCESS_KEY' not in env and 'SSH_AUTH_SOCK' not in env
    assert env['OMP_NUM_THREADS']=='2'

def test_blob_verification_detects_modified_source(tmp_path):
    root,source=tree(tmp_path)
    def git(*args):return subprocess.check_output(['git','-C',str(source),*args],stderr=subprocess.STDOUT)
    git('init','-q');git('add','CMakeLists.txt')
    git('-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','-qm','fixture')
    build_classic.verify_checkout(root,source)
    (source/'CMakeLists.txt').write_text('modified build code')
    with pytest.raises(ValueError,match='blob_mismatch'):build_classic.verify_checkout(root,source)

def test_inventory_uses_official_mapping_and_refuses_external_log_path(tmp_path):
    root,source=tree(tmp_path);data=root/'ExtData';data.mkdir();run=root/'run';run.mkdir()
    log=run/'log.dryrun'
    log.write_text('FILE NOT FOUND '+str(data/'GEOS_4x5/met.nc4')+'\n')
    value=bounded_inputs.inventory(root,data,run,log)
    assert value['files'][0]['key']=='GEOS_4x5/met.nc4'
    log.write_text('FILE NOT FOUND '+str(tmp_path/'outside.nc4')+'\n')
    with pytest.raises(ValueError):bounded_inputs.inventory(root,data,run,log)

def test_cumulative_budget_refused_before_network(tmp_path):
    root,source=tree(tmp_path)
    manifest={'schema':1,'portal':bounded_inputs.PORTAL,'measured':True,
        'files':[{'target':'met.nc4','key':'GEOS_4x5/met.nc4','bytes':101}]}
    with pytest.raises(ValueError,match='budget'):bounded_inputs.fetch(root,manifest,bounded_inputs.LEDGER_NAME,100)
    assert not (root/bounded_inputs.LEDGER_NAME).exists()

def test_unknown_size_and_existing_target_refused(tmp_path):
    root,source=tree(tmp_path)
    manifest={'schema':1,'portal':bounded_inputs.PORTAL,'measured':True,
        'files':[{'target':'existing.nc4','key':'GEOS_4x5/met.nc4','bytes':10}]}
    (root/'existing.nc4').write_bytes(b'existing')
    with pytest.raises(ValueError,match='fresh'):bounded_inputs.fetch(root,manifest,bounded_inputs.LEDGER_NAME,100)

def test_alternate_ledger_cannot_reset_task_budget(tmp_path):
    root,source=tree(tmp_path)
    manifest={'schema':1,'portal':bounded_inputs.PORTAL,'measured':True,
        'files':[{'target':'met.nc4','key':'GEOS_4x5/met.nc4','bytes':10}]}
    with pytest.raises(ValueError,match='canonical_task_ledger'):
        bounded_inputs.fetch(root,manifest,'another-ledger.json',100)
    (root/bounded_inputs.LEDGER_NAME).write_text('{"reserved_bytes":0,"transfers":[{"bytes":10}]}')
    with pytest.raises(ValueError,match='invalid_task_transfer_ledger'):
        bounded_inputs.fetch(root,manifest,bounded_inputs.LEDGER_NAME,100)

def test_state_does_not_follow_existing_temporary_link(tmp_path):
    target=tmp_path/'receipt.json';temp=tmp_path/'receipt.json.tmp';temp.write_text('retained')
    with pytest.raises(FileExistsError):gc_paths.save_state(target,{'state':'new'})
    assert temp.read_text()=='retained'

def test_cf_time_contract():
    values=check_outputs.cf_times([0,60],'minutes since 2019-01-01 00:00:00')
    assert values[0]==datetime(2019,1,1,tzinfo=timezone.utc)
    assert (values[1]-values[0]).total_seconds()==3600
    with pytest.raises(ValueError):check_outputs.cf_times([0],'unrecognized time reference')

class OutputFixture:
    mutate=None
    def __init__(self,library,path):self.restart='restart' in str(path)
    def close(self):pass
    def dimension(self,name):return {'lat':46,'lon':72,'lev':47}[name]
    def variables(self):return [('SpeciesRst_' if self.restart else 'SpeciesConcVV_')+s for s in check_outputs.SPECIES]
    def dimensions(self,name):
        if self.mutate=='field_dimensions' and name.startswith('Species'):return ('time','lat','lon')
        return (name,) if name in {'lat','lon','lev','time'} else ('time','lev','lat','lon')
    def text(self,name,attribute):
        if attribute=='simulation_start_date_and_time':return '2019-01-01 00:00:00z'
        if attribute=='simulation_end_date_and_time':return '2019-01-01 01:00:00z'
        if attribute=='calendar':return 'gregorian'
        if name=='time':return 'minutes since 2019-01-01 00:00:00'
        if attribute=='averaging_method':return 'instantaneous' if self.restart else 'time-averaged'
        return 'mol mol-1 dry'
    def values(self,name):
        if name in {'lat','lon','lev'}:
            v=check_outputs.expected_coordinates()[name][:]
            if self.mutate=='coordinate' and name=='lat':v[0]=0
            return v
        if name=='time':return [60 if self.restart else (30 if self.mutate=='timestamp' else 0)]
        return [1.0]

def test_output_contract(monkeypatch,tmp_path):
    monkeypatch.setattr(check_outputs,'NetCDF',OutputFixture)
    path=tmp_path/'concentration.nc4';path.write_bytes(b'synthetic')
    start=datetime(2019,1,1,tzinfo=timezone.utc);end=start.replace(hour=1)
    result=check_outputs.check_file('fixture',path,'SpeciesConcVV_',['mol mol-1 dry'],start,end)
    assert len(result['fields'])==21

@pytest.mark.parametrize('mutation',['coordinate','timestamp','field_dimensions'])
def test_output_rejects_false_acceptance(monkeypatch,tmp_path,mutation):
    monkeypatch.setattr(check_outputs,'NetCDF',OutputFixture);monkeypatch.setattr(OutputFixture,'mutate',mutation)
    path=tmp_path/'concentration.nc4';path.write_bytes(b'synthetic')
    start=datetime(2019,1,1,tzinfo=timezone.utc);end=start.replace(hour=1)
    with pytest.raises(ValueError):check_outputs.check_file('fixture',path,'SpeciesConcVV_',['mol mol-1 dry'],start,end)

def test_one_hour_history_required(tmp_path):
    history=tmp_path/'HISTORY.rc'
    history.write_text("SpeciesConc.frequency: 00000000 010000\nSpeciesConc.duration: 00000000 010000\nSpeciesConc.mode: 'time-averaged'\n")
    assert len(check_outputs.check_history(history))==64
    history.write_text(history.read_text().replace('010000','020000'))
    with pytest.raises(ValueError):check_outputs.check_history(history)
