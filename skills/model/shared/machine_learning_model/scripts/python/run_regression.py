"""Bounded prepared-data regression. Direct invocation has no runner path sandbox."""
from pathlib import Path
import argparse
from importlib import metadata
import json
import sys

REPO=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(REPO))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime.services.python_ml_workflow import validate_configuration,validate_against_input,supported_outputs,artifact_name
from common.artifacts import digest,metrics,write_json,write_csv
from models.regression import build_pipeline
from contribution.prediction import explain


def run(input_csv,task_config,out_dir,review_bundle=None):
    cfg=validate_configuration(json.loads(task_config.read_text(encoding='utf-8-sig')),REPO)
    input_identity=digest(input_csv)
    if cfg['execution']['purpose']=='new_study':
        # Shared plan review validates the exact input, task and generated code; no boolean bypass.
        from runtime.services.model_plan_gate import require_python_plan
        require_python_plan(cfg,input_csv,Path(__file__).resolve(),review_bundle=review_bundle)
    prepared=validate_against_input(cfg,input_csv)
    files=supported_outputs(cfg)
    for name in [*files.values(),'artifacts.json']:
        path=out_dir/artifact_name(name)
        if path.exists() or path.is_symlink(): raise ValueError('artifact_already_exists')
        if not path.resolve().is_relative_to(out_dir.resolve()): raise ValueError('linked_output_outside_root')
        for parent in (path,*path.parents):
            if not parent.is_relative_to(out_dir): break
            if (parent/'.git').exists(): raise ValueError('nested_git_output')
    try:
        import numpy as np
        import sklearn
        import joblib
        from sklearn.metrics import mean_squared_error,mean_absolute_error
    except ImportError: raise ValueError('required_sklearn_dependency_unavailable') from None
    # Optional capabilities fail explicitly before fitting or producing a successful receipt.
    if 'shap' in cfg['explanation']['methods']:
        try: import shap
        except ImportError: raise ValueError('requested_shap_dependency_unavailable') from None
    datasets={}
    for split in ('train','val','test'):
        rows=[r for r in prepared['rows'] if r['split']==split]
        matrix=[[np.nan if r['values'][c] is None else r['values'][c] for c in cfg['features']] for r in rows]
        datasets[split]=(np.array(matrix,dtype=object),np.array([r['values'][cfg['target']] for r in rows],dtype=float),rows)
    train_x,train_y,_=datasets['train']; val_x,val_y,_=datasets['val']
    candidates=[]; selected=None; best=float('inf')
    for candidate in cfg['models']:
        model=build_pipeline(cfg,candidate); model.fit(train_x,train_y)
        score=metrics(val_y,model.predict(val_x))['rmse']
        candidates.append({'id':candidate['id'],'learner':candidate['learner'],'validation_rmse':score,'parameters':json.dumps(candidate['parameters'],sort_keys=True)})
        if score<best: best=score; selected=(candidate,model)
    candidate,model=selected
    # Freeze selection; test predictions are made only here, for the selected fitted pipeline.
    scores={}; predictions=[]; raw_predictions={}
    independent=True
    for split in ('train','val','test'):
        x,y,rows=datasets[split]; p=model.predict(x); raw_predictions[split]=p
        scores[split]=metrics(y,p)
        independent=independent and bool(np.isclose(scores[split]['rmse']**2,mean_squared_error(y,p))) and bool(np.isclose(scores[split]['mae'],mean_absolute_error(y,p)))
        predictions.extend({'id':r['id'],'source_row':r['source_row'],'split':split,'observed':float(a),'predicted':float(b),'model_id':candidate['id']} for r,a,b in zip(rows,y,p))
    contributions=explain(cfg,model,datasets)
    if digest(input_csv)!=input_identity:
        raise ValueError('input_changed_during_execution')
    out_dir.mkdir(parents=True,exist_ok=True)
    def path(role): return out_dir/files[role]
    model_path=path('model'); model_path.parent.mkdir(parents=True,exist_ok=True)
    # This is the sole load call: only the artifact just created by this execution is accepted.
    joblib.dump(model,model_path)
    reloaded=joblib.load(model_path)
    equal=all(np.allclose(reloaded.predict(datasets[s][0]),raw_predictions[s],rtol=1e-12,atol=1e-12) for s in datasets)
    if not equal or not independent: raise ValueError('model_or_metric_reproducibility_failed')
    write_json(path('target_contract'),{k:cfg[k] for k in ('target','target_unit','target_definition','features','id_column','split')})
    # Keep all original columns and original cell strings for retained rows; all exclusions have keyed records below.
    write_csv(path('prepared_data'),[r['source'] for r in prepared['rows']])
    train_stats={}
    for c in cfg['features']:
        vals=[r['values'][c] for r in datasets['train'][2] if r['values'][c] is not None]
        train_stats[c]={'observed_train_count':len(vals),'mean':sum(vals)/len(vals)} if c not in cfg['categorical_features'] else {'observed_train_count':len(vals),'categories':sorted(set(vals))}
    write_json(path('preprocessing'),{'fit_split':'train','pipeline':'imputation_if_selected_then_standard_scaler_or_one_hot','missing_policy':cfg['missing'],'counts':prepared['counts'],'dropped':prepared['dropped'],'missing_counts':prepared['missing_counts'],'train_statistics':train_stats,'unseen_categories':'ignored_all_zero','source_lineage':prepared['source_lineage'],'excluded_rows':prepared['excluded_rows'],'row_limits':'fail_not_sample'})
    write_csv(path('feature_selection'),[{'feature':c,'selected':True,'method':'explicit_manual'} for c in cfg['features']])
    write_csv(path('candidates'),candidates); write_csv(path('predictions'),predictions)
    write_json(path('metrics'),scores)
    for role,records in contributions.items(): write_csv(path(role),records)
    sources=[Path(__file__).resolve(),*sorted(Path(__file__).parent.glob('*/*.py')),REPO/'runtime/services/python_ml_workflow.py',REPO/'catalog/schemas/python-ml-regression-task.schema.json']
    versions={'python':sys.version.split()[0],'scikit-learn':sklearn.__version__,'numpy':np.__version__,
              'scipy':metadata.version('scipy'),'joblib':joblib.__version__}
    if 'shap' in cfg['explanation']['methods']: versions['shap']=metadata.version('shap')
    write_json(path('provenance'),{'schema_version':1,'backend':'python','configuration':cfg,'input_sha256':input_identity,'configuration_sha256':digest(task_config),'source_sha256':{p.relative_to(REPO).as_posix():digest(p) for p in sources},'versions':versions,'selection':'minimum_validation_rmse_first_tie','selected_model':candidate['id'],'refit_on_validation':False,'test_used_for_selection':False,'scientific_acceptance':'not_established','causal_claim':False})
    write_json(path('reproducibility'),{'reload_predictions_equal':equal,'independent_metrics_equal':independent,'model_sha256':digest(model_path),'load_scope':'fresh_artifact_created_in_this_execution_only','r_python_forest_equivalence':'not_guaranteed'})
    write_json(path('status'),{'status':'completed','analysis':'prediction','backend':'python'})
    write_json(out_dir/'artifacts.json',{'schema_version':1,'analysis':'prediction','backend':'python','files':files})
    return {'status':'completed','selected_model':candidate['id']}


class SafeParser(argparse.ArgumentParser):
    def error(self,message):
        print(json.dumps({'status':'failed','error':'invalid_arguments'})); raise SystemExit(64)


def main():
    parser=SafeParser(allow_abbrev=False); parser.add_argument('--input-csv',type=Path,required=True); parser.add_argument('--task-config',type=Path,required=True); parser.add_argument('--out-dir',type=Path,required=True); parser.add_argument('--review-bundle',type=Path)
    args=parser.parse_args()
    try: print(json.dumps(run(args.input_csv,args.task_config,args.out_dir.resolve(),args.review_bundle))); return 0
    except Exception as error:
        public_codes={'requested_shap_dependency_unavailable','required_sklearn_dependency_unavailable','shap_categorical_not_implemented','shap_missing_input_not_implemented','shap_additivity_failed'}
        code=str(error) if str(error) in public_codes else 'python_regression_failed'
        print(json.dumps({'status':'failed','error':code})); return 71

if __name__=='__main__': raise SystemExit(main())
