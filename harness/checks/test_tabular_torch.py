"""Small synthetic checks for the real-table primitives, no scientific data."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest
pytest.importorskip('torch')
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('tabular',ROOT/'skills/model/shared/machine_learning_model/scripts/python/models/tabular_torch.py')
tab=importlib.util.module_from_spec(spec);spec.loader.exec_module(tab)

@pytest.mark.parametrize('family,config',[
    ('mlp',{'hidden':[8,8],'dropout':.1,'learning_rate':.001,'weight_decay':.0001}),
    ('numerical_tabular_transformer',{'d_model':8,'layers':1,'dropout':.1,'learning_rate':.001,'weight_decay':.0001})])
@pytest.mark.parametrize('features',[3,7])
def test_fit_reload_and_train_only_state(tmp_path,family,config,features):
    rng=np.random.default_rng(9);x=rng.normal(size=(24,features));y=x[:,0]*2+x[:,1]
    x[1,1]=np.nan
    validation=np.ones((6,features))*100
    result=tab.fit_tabular(x,y,family=family,config=config,seed=9,max_epochs=2,batch_size=8,
        x_validation=validation,y_validation=np.arange(6,dtype=float),max_threads=1)
    state=result['artifact']['preprocessing']
    np.testing.assert_allclose(state['median'],np.nanmedian(x,axis=0))
    assert max(np.abs(state['mean']))<2
    before=tab.predict(result['model'],state,validation)
    path=tmp_path/'model.pt';tab.save_model(result['artifact'],path)
    model,artifact=tab.load_model(path,max_threads=1)
    np.testing.assert_array_equal(tab.predict(model,artifact['preprocessing'],validation),before)
    assert 1<=artifact['best_epoch']<=2
    with pytest.raises(ValueError,match='feature_contract'):tab.predict(model,state,np.ones((1,features+1)))

def test_missing_target_and_feature_refused():
    x=np.ones((4,2));y=np.arange(4,dtype=float)
    with pytest.raises(ValueError,match='target'):tab.fit_preprocessing(x,[1,2,np.nan,4])
    x[:,0]=np.nan
    with pytest.raises(ValueError,match='all_missing_training_feature'):tab.fit_preprocessing(x,y)

def test_fixed_epochs_and_deterministic_fit():
    config={'hidden':[4],'dropout':.1,'learning_rate':.001,'weight_decay':.0001}
    x=np.arange(30).reshape(10,3)/10;y=np.arange(10)/10
    a=tab.fit_tabular(x,y,family='mlp',config=config,seed=8,max_epochs=2,batch_size=4,max_threads=1)
    b=tab.fit_tabular(x,y,family='mlp',config=config,seed=8,max_epochs=2,batch_size=4,max_threads=1)
    assert len(a['artifact']['history'])==2 and a['artifact']['validation_used'] is False
    np.testing.assert_array_equal(tab.predict(a['model'],a['artifact']['preprocessing'],x),tab.predict(b['model'],b['artifact']['preprocessing'],x))
