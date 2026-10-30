"""Selected validation-set prediction contributions; descriptive, never causal."""
def explain(cfg, model, datasets):
    import numpy as np
    from sklearn.metrics import mean_squared_error
    ex=cfg['explanation']; names=cfg['features']
    x,y,rows=datasets['val']; x=x[:ex['validation_rows']].copy(); y=y[:len(x)]; rows=rows[:len(x)]
    result={}; rng=np.random.default_rng(cfg['seed']); base=model.predict(x)
    if 'permutation' in ex['methods']:
        records=[]; original=mean_squared_error(y,base)
        for name in ex['features']:
            j=names.index(name)
            for repeat in range(ex['permutation_repeats']):
                changed=x.copy(); changed[:,j]=rng.permutation(changed[:,j])
                records.append({'feature':name,'repeat':repeat,'delta_mse':mean_squared_error(y,model.predict(changed))-original,'split':'val'})
        result['permutation']=records
    if set(ex['methods']) & {'pdp','ice'}:
        pdp=[]; ice=[]; train=datasets['train'][0]
        for name in ex['features']:
            j=names.index(name); vals=np.array([float(v) for v in train[:,j] if v is not None and not np.isnan(float(v))])
            grid=np.unique(np.quantile(vals,np.linspace(0,1,ex['pdp_points'])))
            for value in grid:
                changed=x.copy(); changed[:,j]=value; predictions=model.predict(changed)
                pdp.append({'feature':name,'value':value,'mean_prediction':float(np.mean(predictions)),'split':'val'})
                ice.extend({'id':r['id'],'feature':name,'value':value,'prediction':float(pred),'split':'val'} for r,pred in zip(rows,predictions))
        if 'pdp' in ex['methods']: result['pdp']=pdp
        if 'ice' in ex['methods']: result['ice']=ice
    if 'shap' in ex['methods']:
        try: import shap
        except ImportError: raise ValueError('requested_shap_dependency_unavailable') from None
        # Permutation masker operates on numeric raw features. No fabricated categorical encoding attribution.
        if cfg['categorical_features']: raise ValueError('shap_categorical_not_implemented')
        background=np.asarray(datasets['train'][0][:ex['background_rows']],dtype=float)
        observations=np.asarray(x,dtype=float)
        if not np.isfinite(background).all() or not np.isfinite(observations).all(): raise ValueError('shap_missing_input_not_implemented')
        explainer=shap.PermutationExplainer(model.predict,background,seed=cfg['seed'])
        values=explainer(observations,max_evals=ex['shap_max_evals'])
        if not np.allclose(values.base_values+values.values.sum(axis=1),base,rtol=1e-6,atol=1e-7): raise ValueError('shap_additivity_failed')
        result['shap']=[{'id':r['id'],'feature':name,'contribution':float(values.values[i,j]),'base_value':float(values.base_values[i]),'prediction':float(base[i]),'algorithm':'permutation','background':'training_first_rows','output':'raw_prediction','additivity_checked':True,'split':'val'} for i,r in enumerate(rows) for j,name in enumerate(names)]
    return result
