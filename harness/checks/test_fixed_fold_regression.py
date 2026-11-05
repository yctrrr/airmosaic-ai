import importlib.util
from pathlib import Path
import numpy as np
import pytest
pytest.importorskip('sklearn')
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fixed',ROOT/'skills/model/shared/machine_learning_model/scripts/python/models/fixed_fold_regression.py')
fixed=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixed)

@pytest.mark.parametrize('family,params',[
    ('linear_regression',{}),('decision_tree',{'max_depth':3,'min_samples_leaf':2}),
    ('random_forest',{'n_estimators':5,'max_depth':None,'min_samples_leaf':2,'max_features':.5}),
    ('histogram_gradient_boosting',{'max_iter':3,'early_stopping':False,'min_samples_leaf':2})])
def test_single_fit_and_train_imputer(family,params):
    x=np.arange(60,dtype=float).reshape(20,3);x[0,0]=np.nan;y=np.arange(20,dtype=float)
    model=fixed.fit_once(x,y,family=family,parameters=params,seed=7,max_threads=1)
    np.testing.assert_allclose(model.named_steps['impute'].statistics_,np.nanmedian(x,axis=0))
    assert np.isfinite(model.predict(x)).all()

def test_no_hidden_validation():
    with pytest.raises(ValueError,match='hidden_validation'):
        fixed.build_regressor('histogram_gradient_boosting',{},seed=7)

def test_candidate_freezing():
    space={'max_depth':[6,12,18],'min_samples_leaf':[28,56,112,224]}
    assert fixed.candidates(space,n_iter=4,seed=20261101)==fixed.candidates(space,n_iter=4,seed=20261101)
