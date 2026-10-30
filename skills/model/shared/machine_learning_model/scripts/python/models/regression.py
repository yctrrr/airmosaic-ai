"""Fixed sklearn constructors; no dynamic estimator, callback or user model loading."""
def build_pipeline(cfg, candidate):
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.dummy import DummyRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor
    cats=[i for i,c in enumerate(cfg['features']) if c in cfg['categorical_features']]
    nums=[i for i,c in enumerate(cfg['features']) if c not in cfg['categorical_features']]
    transformers=[]
    if nums:
        steps=[]
        if cfg['missing']['policy']=='impute': steps.append(('impute',SimpleImputer(strategy='median')))
        steps.append(('scale',StandardScaler()))
        transformers.append(('numeric',Pipeline(steps),nums))
    if cats:
        steps=[]
        if cfg['missing']['policy']=='impute': steps.append(('impute',SimpleImputer(strategy='most_frequent')))
        steps.append(('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False)))
        transformers.append(('categorical',Pipeline(steps),cats))
    learner=candidate['learner']; params=candidate['parameters']
    if learner=='baseline_mean': model=DummyRegressor(strategy='mean')
    elif learner=='linear_regression': model=LinearRegression()
    elif learner=='decision_tree': model=DecisionTreeRegressor(random_state=cfg['seed'],**params)
    else: model=RandomForestRegressor(random_state=cfg['seed'],n_jobs=1,**params)
    return Pipeline([('prepare',ColumnTransformer(transformers,sparse_threshold=0)),('model',model)])
