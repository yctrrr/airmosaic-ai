"""Static validation for the bounded Python regression adapter (no ML imports)."""
from __future__ import annotations
from copy import deepcopy
import csv
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
from jsonschema import Draft202012Validator

DEFAULT_OUTPUTS = {"target_contract":"target.json", "prepared_data":"prepared.csv", "preprocessing":"preprocessing.json", "feature_selection":"feature-selection.csv", "candidates":"candidates.csv", "model":"model.joblib", "predictions":"predictions.csv", "metrics":"metrics.json", "provenance":"provenance.json", "reproducibility":"reproducibility.json", "status":"status.json", "artifacts":"artifacts.json", "permutation":"permutation-importance.csv", "pdp":"pdp.csv", "ice":"ice.csv", "shap":"shap.csv"}


def artifact_name(name: str) -> str:
    parts = name.split('/')
    if (not name or '\\' in name or ':' in name or PurePosixPath(name).is_absolute()
            or any(p.casefold() in {'', '.', '..', '.git', '.airmosaic', 'auth', 'credentials', 'secrets', '.env', 'temp', 'records'} for p in parts)):
        raise ValueError('invalid_artifact_name')
    return name


def validate_configuration(value: dict, repository_root: Path) -> dict:
    schema = json.loads((Path(repository_root)/'catalog/schemas/python-ml-regression-task.schema.json').read_text(encoding='utf-8'))
    if not Draft202012Validator(schema).is_valid(value):
        raise ValueError('invalid_python_ml_configuration')
    def finite_json(item):
        if isinstance(item,float): return math.isfinite(item)
        if isinstance(item,str): return not any(ord(c)<32 for c in item)
        if isinstance(item,list): return all(finite_json(v) for v in item)
        if isinstance(item,dict): return all(finite_json(k) and finite_json(v) for k,v in item.items())
        return True
    if not finite_json(value): raise ValueError('nonfinite_or_control_configuration')
    cfg = deepcopy(value)
    features = cfg['features']
    reserved = {cfg['id_column'],cfg['target'],cfg['split']['column']}
    if (len(reserved)!=3 or reserved & set(features) or not set(cfg['categorical_features']) <= set(features)
            or not set(cfg['explanation']['features']) <= set(features)
            or len({cfg['split'][s] for s in ('train','val','test')})!=3
            or len({m['id'] for m in cfg['models']})!=len(cfg['models'])
            or not any(m['learner']=='baseline_mean' for m in cfg['models'])):
        raise ValueError('invalid_python_ml_columns_or_candidates')
    for model in cfg['models']:
        allowed={'baseline_mean':set(),'linear_regression':set(),'decision_tree':{'max_depth','min_samples_leaf'},'random_forest':{'max_depth','min_samples_leaf','n_estimators','max_features'}}[model['learner']]
        if set(model['parameters'])-allowed:
            raise ValueError('unsupported_model_parameter')
        if model['learner'] in {'decision_tree','random_forest'} and 'max_depth' not in model['parameters']:
            raise ValueError('explicit_tree_depth_required')
        if model['learner']=='random_forest' and 'n_estimators' not in model['parameters']:
            raise ValueError('explicit_forest_budget_required')
    if sum(m['parameters'].get('n_estimators',1) for m in cfg['models'])>1024:
        raise ValueError('total_tree_budget_exceeded')
    ex=cfg['explanation']
    if ex['methods'] and not ex['features']:
        raise ValueError('explanation_features_required')
    if set(ex['features']) & set(cfg['categorical_features']) and set(ex['methods']) & {'pdp','ice'}:
        raise ValueError('numeric_dependence_features_required')
    if 'shap' in ex['methods'] and cfg['categorical_features']:
        raise ValueError('shap_categorical_not_implemented')
    if 'shap' in ex['methods'] and ex.get('shap_max_evals',0)*ex['background_rows']*ex['validation_rows']>2_000_000:
        raise ValueError('shap_evaluation_budget_exceeded')
    if 'shap' in ex['methods'] and (not all(k in ex for k in ('shap_algorithm','shap_output','shap_background','shap_max_evals')) or ex['shap_max_evals']<2*len(features)+1):
        raise ValueError('explicit_shap_contract_required')
    # Upper bound on dense one-hot preprocessing; data-level cardinality is also checked.
    if sum(cfg['row_limits'].values())*len(features)>5_000_000:
        raise ValueError('row_feature_budget_exceeded')
    names={**DEFAULT_OUTPUTS,**cfg.get('output_files',{})}
    if set(names)!=set(DEFAULT_OUTPUTS) or names['artifacts']!='artifacts.json':
        raise ValueError('invalid_output_roles')
    for role,name in names.items():
        artifact_name(name)
        if PurePosixPath(name).suffix!=PurePosixPath(DEFAULT_OUTPUTS[role]).suffix:
            raise ValueError('invalid_output_suffix')
    paths=[PurePosixPath(n.casefold()) for n in names.values()]
    if any(a==b or a in b.parents or b in a.parents for i,a in enumerate(paths) for b in paths[i+1:]):
        raise ValueError('overlapping_output_names')
    cfg['output_files']=names
    return cfg


def supported_outputs(cfg: dict) -> dict:
    roles=set(DEFAULT_OUTPUTS)-{'artifacts','permutation','pdp','ice','shap'}
    roles.update(cfg['explanation']['methods'])
    return {r:cfg['output_files'][r] for r in sorted(roles)}


def validate_against_input(cfg: dict, input_csv: Path) -> dict:
    """Read bounded prepared rows, preserving supplied keys and explicit labels."""
    with Path(input_csv).open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle)
        header=reader.fieldnames or []
        needed={cfg['id_column'],cfg['target'],cfg['split']['column'],*cfg['features']}
        if len(header)!=len(set(header)) or not needed<=set(header):
            raise ValueError('missing_or_duplicate_columns')
        rows=[]; excluded_rows=[]; seen=set(); counts={s:0 for s in ('train','val','test')}; dropped={s:0 for s in counts}; missing={c:0 for c in [cfg['target'],*cfg['features']]}
        labels={cfg['split'][s]:s for s in counts}
        max_rows=sum(cfg['row_limits'].values())
        for index,row in enumerate(reader):
            if index>=max_rows or None in row or any(v is None for v in row.values()):
                raise ValueError('input_row_budget_or_shape')
            key=row[cfg['id_column']]
            if not key or key in seen:
                raise ValueError('empty_or_duplicate_id_split_overlap')
            seen.add(key)
            if row[cfg['split']['column']] not in labels:
                raise ValueError('unknown_split_label')
            split=labels[row[cfg['split']['column']]]; counts[split]+=1
            if counts[split]>cfg['row_limits'][split]: raise ValueError('split_row_budget_exceeded')
            values={}; absent=[]
            for col in [cfg['target'],*cfg['features']]:
                raw=row[col]
                is_missing=not raw.strip()
                if col not in cfg['categorical_features'] and not is_missing:
                    try: number=float(raw)
                    except ValueError: raise ValueError('non_numeric_value') from None
                    is_missing=not math.isfinite(number) or number in cfg['missing']['sentinels']
                    values[col]=number
                else: values[col]=raw
                if is_missing: missing[col]+=1; absent.append(col); values[col]=None
            if absent:
                if cfg['missing']['policy']=='error': raise ValueError('missing_values_forbidden')
                if cfg['missing']['policy']=='drop' or cfg['target'] in absent:
                    dropped[split]+=1; excluded_rows.append({'id':key,'source_row':index+2,'split':split,'missing_columns':absent}); continue
            rows.append({'source_row':index+2,'id':key,'split':split,'values':values,'source':row})
    for split in counts:
        if sum(r['split']==split for r in rows)<2: raise ValueError('insufficient_split_rows')
    train=[r for r in rows if r['split']=='train']
    for col in cfg['features']:
        if not any(r['values'][col] is not None for r in train): raise ValueError('all_missing_train_feature')
        if col in cfg['categorical_features'] and len({r['values'][col] for r in train})>64: raise ValueError('categorical_cardinality_budget')
    expanded=sum(len({r['values'][c] for r in train if r['values'][c] is not None}) if c in cfg['categorical_features'] else 1 for c in cfg['features'])
    if expanded*len(rows)>5_000_000: raise ValueError('dense_preprocessing_budget_exceeded')
    return {'excluded_rows':excluded_rows,'rows':rows,'header':header,'counts':counts,'dropped':dropped,'missing_counts':missing,'source_lineage':'caller_supplied_not_certified'}


def validate_outputs(output: Path) -> bool:
    try:
        if (output/'artifacts.json').is_symlink(): return False
        manifest=json.loads((output/'artifacts.json').read_text(encoding='utf-8'))
        files=manifest['files']
        if not isinstance(files,dict) or len(files)>20: return False
        for name in files.values():
            path=output/artifact_name(name)
            if not path.is_file() or path.stat().st_size==0 or path.is_symlink() or not path.resolve().is_relative_to(output.resolve()): return False
            for parent in (path,*path.parents):
                if not parent.is_relative_to(output): break
                if parent.is_symlink() or (parent/'.git').exists(): return False
        status=json.loads((output/files['status']).read_text(encoding='utf-8'))
        provenance=json.loads((output/files['provenance']).read_text(encoding='utf-8'))
        repro=json.loads((output/files['reproducibility']).read_text(encoding='utf-8'))
        metrics=json.loads((output/files['metrics']).read_text(encoding='utf-8'))
        with (output/files['predictions']).open(encoding='utf-8',newline='') as handle:
            predictions=list(csv.DictReader(handle))
        keys=[r['id'] for r in predictions]
        if len(keys)!=len(set(keys)) or not all(r['split'] in {'train','val','test'} for r in predictions): return False
        for split in ('train','val','test'):
            rows=[r for r in predictions if r['split']==split]
            actual=[float(r['observed']) for r in rows]; predicted=[float(r['predicted']) for r in rows]
            if not rows or not all(math.isfinite(v) for v in actual+predicted): return False
            rmse=math.sqrt(sum((a-b)**2 for a,b in zip(actual,predicted))/len(rows))
            mae=sum(abs(a-b) for a,b in zip(actual,predicted))/len(rows)
            if metrics[split]['n']!=len(rows) or not math.isclose(rmse,metrics[split]['rmse'],rel_tol=1e-9,abs_tol=1e-12) or not math.isclose(mae,metrics[split]['mae'],rel_tol=1e-9,abs_tol=1e-12): return False
        if hashlib.sha256((output/files['model']).read_bytes()).hexdigest()!=repro['model_sha256']: return False
        return (set(metrics)=={'train','val','test'} and all(type(metrics[s]['n']) is int and metrics[s]['n']>=2 and all(type(metrics[s][k]) in (int,float) and math.isfinite(metrics[s][k]) and metrics[s][k]>=0 for k in ('rmse','mae')) for s in metrics)
                and files==supported_outputs(provenance['configuration']) and status['status']=='completed'
                and repro['reload_predictions_equal'] is True and repro['independent_metrics_equal'] is True
                and all(math.isfinite(metrics[s]['rmse']) for s in ('val','test')))
    except (OSError,ValueError,TypeError,KeyError,AttributeError,OverflowError): return False
