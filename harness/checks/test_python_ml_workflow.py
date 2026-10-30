"""Synthetic engineering checks; never scientific acceptance or source certification."""
from copy import deepcopy
import csv
import importlib.util
import json
from pathlib import Path
import sys
import pytest

from runtime.services.python_ml_workflow import validate_configuration,validate_against_input,validate_outputs

REPO=Path(__file__).resolve().parents[2]
SCRIPT=REPO/'skills/model/shared/machine_learning_model/scripts/python/run_regression.py'

@pytest.fixture
def config():
    cfg=json.loads((REPO/'config/examples/machine-learning-model/python/synthetic-regression.json').read_text())
    cfg['features']=['x']; cfg['explanation']['features']=['x']; cfg['explanation']['methods']=[]
    cfg['row_limits']={'train':20,'val':10,'test':10}
    return cfg


def data(path,duplicate=False,missing=False):
    rows=[]
    for split,start in [('train',0),('val',100),('test',1000)]:
        for i in range(6):
            x=start+i
            rows.append({'id':f'{split}_{i}','dataset':split,'x':str(x),'outcome':str(2*x+3),'untouched':'keep'})
    if duplicate: rows[-1]['id']=rows[0]['id']
    if missing: rows[0]['x']=''
    with path.open('w',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return rows


def load_runner():
    pytest.importorskip('sklearn')
    sys.path.insert(0,str(SCRIPT.parent))
    spec=importlib.util.spec_from_file_location('bounded_python_regression',SCRIPT)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_static_configuration_rejects_leakage_and_unknown_estimators(config):
    cfg=deepcopy(config); cfg['features'].append('outcome')
    with pytest.raises(ValueError): validate_configuration(cfg,REPO)
    cfg=deepcopy(config); cfg['models'][0]['learner']='arbitrary.callable'
    with pytest.raises(ValueError): validate_configuration(cfg,REPO)
    cfg=deepcopy(config); cfg['models'][-1]['parameters']['n_jobs']=-1
    with pytest.raises(ValueError): validate_configuration(cfg,REPO)
    cfg=deepcopy(config); cfg['output_files']={'metrics':'../escape.json'}
    with pytest.raises(ValueError): validate_configuration(cfg,REPO)


def test_split_overlap_and_missing_audit(config,tmp_path):
    source=tmp_path/'rows.csv'; data(source,duplicate=True)
    cfg=validate_configuration(config,REPO)
    with pytest.raises(ValueError,match='duplicate_id'): validate_against_input(cfg,source)
    data(source,missing=True)
    with pytest.raises(ValueError,match='missing_values'): validate_against_input(cfg,source)
    config['missing']['policy']='drop'; cfg=validate_configuration(config,REPO)
    result=validate_against_input(cfg,source)
    assert result['dropped']['train']==1
    assert result['excluded_rows'][0]['id']=='train_0'
    assert result['rows'][0]['id']=='train_1' and result['rows'][0]['source_row']==3


def test_real_fit_reload_train_only_and_independent_metrics(config,tmp_path):
    runner=load_runner(); source=tmp_path/'rows.csv'; original=data(source)
    task=tmp_path/'task.json'; task.write_text(json.dumps(config)); output=tmp_path/'out'
    result=runner.run(source,task,output)
    assert result['selected_model']=='linear'
    assert validate_outputs(output)
    preprocessing=json.loads((output/'preprocessing.json').read_text())
    assert preprocessing['train_statistics']['x']['mean']==2.5
    assert preprocessing['fit_split']=='train'
    provenance=json.loads((output/'provenance.json').read_text())
    assert provenance['test_used_for_selection'] is False
    with (output/'prepared.csv').open() as h: assert list(csv.DictReader(h))==original
    with (output/'predictions.csv').open() as h: predictions=list(csv.DictReader(h))
    test=[r for r in predictions if r['split']=='test']
    independent=(sum((float(r['predicted'])-float(r['observed']))**2 for r in test)/len(test))**0.5
    assert independent==pytest.approx(json.loads((output/'metrics.json').read_text())['test']['rmse'])
    import joblib
    # Load only this test's freshly generated trusted artifact, never caller-provided serialized objects.
    pipeline=joblib.load(output/'model.joblib')
    assert pipeline['prepare'].named_transformers_['numeric']['scale'].mean_[0]==2.5
    with pytest.raises(ValueError,match='already_exists'): runner.run(source,task,output)


def test_heldout_changes_do_not_change_selection(config,tmp_path):
    runner=load_runner(); source=tmp_path/'rows.csv'; rows=data(source); task=tmp_path/'task.json'; task.write_text(json.dumps(config))
    first=runner.run(source,task,tmp_path/'first')
    for row in rows:
        if row['dataset']=='test': row['outcome']='-1000000'
    with source.open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    second=runner.run(source,task,tmp_path/'second')
    assert first['selected_model']==second['selected_model']
    assert (tmp_path/'first/candidates.csv').read_bytes()==(tmp_path/'second/candidates.csv').read_bytes()


def test_explanations_and_missing_shap_explicit(config,tmp_path,monkeypatch):
    runner=load_runner(); source=tmp_path/'rows.csv'; data(source)
    config['explanation']['methods']=['permutation','pdp','ice']
    task=tmp_path/'task.json'; task.write_text(json.dumps(config)); runner.run(source,task,tmp_path/'out')
    assert validate_outputs(tmp_path/'out')
    for name in ['permutation-importance.csv','pdp.csv','ice.csv']: assert (tmp_path/'out'/name).stat().st_size>20
    config['explanation'].update(methods=['shap'],shap_algorithm='permutation',shap_output='raw_prediction',shap_background='training_first_rows',shap_max_evals=8)
    task.write_text(json.dumps(config)); monkeypatch.setitem(sys.modules,'shap',None)
    with pytest.raises(ValueError,match='requested_shap_dependency_unavailable'): runner.run(source,task,tmp_path/'shap-out')
    assert not (tmp_path/'shap-out/artifacts.json').exists()


def test_imputation_and_unseen_category_are_train_fitted(config,tmp_path):
    runner=load_runner(); source=tmp_path/'rows.csv'; rows=data(source,missing=True)
    config['features']=['x','category']; config['categorical_features']=['category']; config['missing']['policy']='impute'
    for i,row in enumerate(rows): row['category']='a' if row['dataset']=='train' else 'unseen'
    rows[1]['category']=''
    with source.open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    task=tmp_path/'task.json'; task.write_text(json.dumps(config)); output=tmp_path/'out'
    runner.run(source,task,output)
    assert validate_outputs(output)
    import joblib
    model=joblib.load(output/'model.joblib')
    assert model['prepare'].named_transformers_['numeric']['impute'].statistics_[0]==3
    assert list(model['prepare'].named_transformers_['categorical']['encode'].categories_[0])==['a']


def test_isolated_cli_sanitizes_bad_arguments(tmp_path):
    import subprocess
    value='SYNTHETIC_PRIVATE_PATH_MARKER'
    result=subprocess.run([sys.executable,'-I','-B',str(SCRIPT),'--unknown',value],capture_output=True,text=True)
    assert result.returncode==64
    assert value not in result.stdout+result.stderr
    assert 'invalid_arguments' in result.stdout


def test_artifact_validation_detects_tampered_metrics(config,tmp_path):
    runner=load_runner(); source=tmp_path/'rows.csv'; data(source); task=tmp_path/'task.json'; task.write_text(json.dumps(config)); output=tmp_path/'out'
    runner.run(source,task,output)
    metrics=json.loads((output/'metrics.json').read_text()); metrics['test']['rmse']=999
    (output/'metrics.json').write_text(json.dumps(metrics))
    assert not validate_outputs(output)


def test_requested_shap_additivity_with_optional_dependency(config,tmp_path):
    pytest.importorskip('shap')
    runner=load_runner(); source=tmp_path/'rows.csv'; data(source)
    config['explanation'].update(methods=['shap'],shap_algorithm='permutation',shap_output='raw_prediction',shap_background='training_first_rows',shap_max_evals=8,validation_rows=3,background_rows=4)
    task=tmp_path/'task.json'; task.write_text(json.dumps(config)); output=tmp_path/'out'
    runner.run(source,task,output)
    assert validate_outputs(output)
    assert json.loads((output/'provenance.json').read_text())['versions']['shap']
    with (output/'shap.csv').open() as handle: records=list(csv.DictReader(handle))
    assert len(records)==3
    for record in records:
        assert float(record['base_value'])+float(record['contribution'])==pytest.approx(float(record['prediction']))
        assert record['additivity_checked']=='True'


def test_changed_input_is_rejected_before_publishing_artifacts(config,tmp_path,monkeypatch):
    runner=load_runner(); source=tmp_path/'rows.csv'; data(source)
    task=tmp_path/'task.json'; task.write_text(json.dumps(config)); output=tmp_path/'out'
    def changed(*args,**kwargs):
        source.write_text('changed synthetic source\n')
        return {}
    monkeypatch.setattr(runner,'explain',changed)
    with pytest.raises(ValueError,match='input_changed_during_execution'):
        runner.run(source,task,output)
    assert not (output/'artifacts.json').exists()


def test_cli_file_error_does_not_reveal_private_argument(tmp_path):
    import subprocess
    marker='SYNTHETIC_PRIVATE_FILE_MARKER'
    result=subprocess.run([sys.executable,'-I','-B',str(SCRIPT),'--input-csv',str(tmp_path/'rows.csv'),
        '--task-config',str(tmp_path/(marker+'.json')),'--out-dir',str(tmp_path/'out')],
        capture_output=True,text=True)
    assert result.returncode==71
    assert marker not in result.stdout+result.stderr
    assert json.loads(result.stdout)['error']=='python_regression_failed'
