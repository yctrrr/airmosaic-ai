"""Single-fit classical estimators for explicit, externally frozen purged folds.

No hidden CV, validation split or refit. The caller must reserve every fit and
freeze folds/candidates before this helper is called. Prediction/evaluation of
an outer test set happens only after development-only selection is complete.
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor,HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import ParameterSampler
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor


def candidates(search_space,*,n_iter,seed):
    if not isinstance(n_iter,int) or isinstance(n_iter,bool) or not 1<=n_iter<=16:
        raise ValueError('invalid_candidate_budget')
    return list(ParameterSampler(search_space,n_iter=n_iter,random_state=seed))


def build_regressor(family,parameters,*,seed,max_threads=4):
    if not isinstance(max_threads,int) or isinstance(max_threads,bool) or not 1<=max_threads<=4:
        raise ValueError('invalid_thread_limit')
    parameters=dict(parameters)
    if family=='linear_regression':
        if parameters:raise ValueError('linear_parameters_must_be_empty')
        estimator=LinearRegression(n_jobs=max_threads)
    elif family=='decision_tree':estimator=DecisionTreeRegressor(random_state=seed,**parameters)
    elif family=='random_forest':
        if 'n_jobs' in parameters and parameters['n_jobs']!=max_threads:raise ValueError('forest_thread_contract_mismatch')
        parameters['n_jobs']=max_threads
        estimator=RandomForestRegressor(random_state=seed,**parameters)
    elif family=='histogram_gradient_boosting':
        if parameters.get('early_stopping') is not False:raise ValueError('hidden_validation_not_allowed')
        estimator=HistGradientBoostingRegressor(random_state=seed,**parameters)
    else:raise ValueError('unsupported_fixed_fold_family')
    steps=[('impute',SimpleImputer(strategy='median',keep_empty_features=True))]
    if family=='linear_regression':steps.append(('scale',StandardScaler()))
    return Pipeline([*steps,('model',estimator)])


def fit_once(x,y,*,family,parameters,seed,max_threads=4):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if (x.ndim!=2 or not all(x.shape) or y.ndim!=1 or len(y)!=len(x)
            or np.isinf(x).any() or not np.isfinite(y).all() or np.isnan(x).all(axis=0).any()):
        raise ValueError('invalid_fold_training_data')
    from threadpoolctl import threadpool_limits
    estimator=build_regressor(family,parameters,seed=seed,max_threads=max_threads)
    with threadpool_limits(limits=max_threads):estimator.fit(x,y)
    return estimator
