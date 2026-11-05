"""Explicit real numeric-table MLP and FT-inspired regression primitives.

Trusted direct Python API, not a runner adapter. Caller owns a reviewed feature
contract, frozen spatial/temporal folds, fit ledger, hard worker deadlines and
fresh result paths. No data acquisition, test-based selection or causal claims.
"""
import copy
import math
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn


class NumericTableModel(nn.Module):
    def __init__(self, family, n_features, config):
        super().__init__()
        self.family=family
        if family=='mlp':
            layers=[];width=n_features
            for hidden in config['hidden']:
                layers.extend([nn.Linear(width,hidden),nn.GELU(),nn.Dropout(config['dropout'])]);width=hidden
            layers.append(nn.Linear(width,1));self.network=nn.Sequential(*layers)
        elif family=='numerical_tabular_transformer':
            width=config['d_model']
            if width%4:raise ValueError('tabular_transformer_width_requires_four_heads')
            self.token_weight=nn.Parameter(torch.randn(n_features,width)*.02)
            self.token_bias=nn.Parameter(torch.zeros(n_features,width))
            self.cls=nn.Parameter(torch.zeros(1,1,width))
            layer=nn.TransformerEncoderLayer(d_model=width,nhead=4,dim_feedforward=2*width,
                dropout=config['dropout'],activation='gelu',batch_first=True,norm_first=True)
            self.encoder=nn.TransformerEncoder(layer,num_layers=config['layers'],enable_nested_tensor=False)
            self.readout=nn.Sequential(nn.LayerNorm(width),nn.Linear(width,1))
        else:raise ValueError('unsupported_tabular_torch_family')

    def forward(self,x):
        if self.family=='mlp':return self.network(x).squeeze(-1)
        tokens=x.unsqueeze(-1)*self.token_weight+self.token_bias
        tokens=torch.cat([self.cls.expand(len(x),-1,-1),tokens],dim=1)
        return self.readout(self.encoder(tokens)[:,0]).squeeze(-1)


def _xy(x,y=None):
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or not all(x.shape) or np.isinf(x).any():raise ValueError('invalid_numeric_table')
    if y is None:return x
    y=np.asarray(y,dtype=float)
    if y.ndim!=1 or len(y)!=len(x) or not np.isfinite(y).all():raise ValueError('invalid_regression_target')
    return x,y


def fit_preprocessing(x,y):
    x,y=_xy(x,y)
    if np.isnan(x).all(axis=0).any():raise ValueError('all_missing_training_feature')
    median=np.nanmedian(x,axis=0)
    filled=np.where(np.isnan(x),median,x)
    mean=filled.mean(axis=0);scale=filled.std(axis=0);scale[scale==0]=1
    ys=float(y.std())
    return {'median':median.tolist(),'mean':mean.tolist(),'scale':scale.tolist(),
            'y_mean':float(y.mean()),'y_scale':ys if ys else 1.0,'n_features':x.shape[1]}


def transform(x,state):
    x=_xy(x)
    if x.shape[1]!=state['n_features']:raise ValueError('feature_contract_changed')
    filled=np.where(np.isnan(x),np.asarray(state['median']),x)
    result=(filled-np.asarray(state['mean']))/np.asarray(state['scale'])
    if not np.isfinite(result).all():raise ValueError('nonfinite_transformed_features')
    return torch.from_numpy(result.astype('float32'))


def predict(model,preprocessing,x,*,batch_size=1024):
    transformed=transform(x,preprocessing)
    if not isinstance(batch_size,int) or isinstance(batch_size,bool) or batch_size<=0:raise ValueError('invalid_batch_size')
    model.eval();chunks=[]
    with torch.no_grad():
        for start in range(0,len(transformed),batch_size):
            chunks.append(model(transformed[start:start+batch_size]).numpy().astype(float))
    values=np.concatenate(chunks)*preprocessing['y_scale']+preprocessing['y_mean']
    if not np.isfinite(values).all():raise ValueError('nonfinite_predictions')
    return values


def fit_tabular(x_train,y_train,*,family,config,seed,max_epochs,batch_size=1024,
                x_validation=None,y_validation=None,patience=6,min_delta=.0001,
                gradient_norm_clip=1.0,max_seconds=1200,max_threads=4):
    """Fit once; early stopping sees only the supplied development fold.

    For final refits omit validation and provide the preselected fixed epoch
    count. Runtime deadline here is cooperative; caller also needs a hard
    process deadline. Neither helper nor reload starts additional fits.
    """
    x_train,y_train=_xy(x_train,y_train)
    if (x_validation is None)!=(y_validation is None):raise ValueError('paired_validation_required')
    if not all(isinstance(v,int) and not isinstance(v,bool) and v>0 for v in (max_epochs,batch_size,patience,max_threads)):
        raise ValueError('positive_training_limits_required')
    if max_threads>4 or not 0<max_seconds<=1200 or min_delta<0 or gradient_norm_clip<=0:
        raise ValueError('unsupported_training_limits')
    start=time.monotonic();torch.set_num_threads(max_threads)
    torch.manual_seed(seed);torch.use_deterministic_algorithms(True)
    state=fit_preprocessing(x_train,y_train)
    x=transform(x_train,state);y=torch.tensor((y_train-state['y_mean'])/state['y_scale'],dtype=torch.float32)
    val=None
    if x_validation is not None:
        xv,yv=_xy(x_validation,y_validation)
        val=(transform(xv,state),torch.tensor((yv-state['y_mean'])/state['y_scale'],dtype=torch.float32))
    model=NumericTableModel(family,x.shape[1],config)
    optimizer=torch.optim.AdamW(model.parameters(),lr=config['learning_rate'],weight_decay=config['weight_decay'])
    generator=torch.Generator().manual_seed(seed)
    history=[];best=float('inf');best_epoch=0;best_weights=None;stale=0
    for epoch in range(1,max_epochs+1):
        model.train();order=torch.randperm(len(x),generator=generator);squared=0.;seen=0
        for begin in range(0,len(order),batch_size):
            if time.monotonic()-start>=max_seconds:raise TimeoutError('neural_fit_deadline')
            idx=order[begin:begin+batch_size];optimizer.zero_grad(set_to_none=True)
            loss=nn.functional.mse_loss(model(x[idx]),y[idx])
            if not torch.isfinite(loss):raise ValueError('nonfinite_training_loss')
            loss.backward();nn.utils.clip_grad_norm_(model.parameters(),gradient_norm_clip);optimizer.step()
            squared+=float(loss.detach())*len(idx);seen+=len(idx)
        row={'epoch':epoch,'train_normalized_mse':squared/seen}
        if val is not None:
            model.eval();total=0.
            with torch.no_grad():
                for begin in range(0,len(val[0]),batch_size):
                    if time.monotonic()-start>=max_seconds:raise TimeoutError('neural_fit_deadline')
                    pred=model(val[0][begin:begin+batch_size]);target=val[1][begin:begin+batch_size]
                    total+=float(nn.functional.mse_loss(pred,target,reduction='sum'))
            value=total/len(val[0]);row['validation_normalized_mse']=value
            if not math.isfinite(value):raise ValueError('nonfinite_validation_loss')
            if value<best-min_delta:
                best=value;best_epoch=epoch;best_weights=copy.deepcopy(model.state_dict());stale=0
            else:stale+=1
        history.append(row)
        if val is not None and stale>=patience:break
    if val is not None:model.load_state_dict(best_weights)
    else:best_epoch=max_epochs
    artifact={'schema_version':1,'family':family,'config':config,'seed':int(seed),'preprocessing':state,
              'state_dict':model.state_dict(),'best_epoch':best_epoch,'history':history,
              'elapsed_seconds':time.monotonic()-start,'validation_used':val is not None,
              'published_ft_reproduction':False}
    return {'model':model,'artifact':artifact}


def save_model(artifact,path):
    with Path(path).open('xb') as stream:torch.save(artifact,stream)


def load_model(path,*,max_threads=4):
    # Own hash-verified checkpoint; restrict Torch unpickling as well.
    if not isinstance(max_threads,int) or isinstance(max_threads,bool) or not 1<=max_threads<=4:
        raise ValueError('invalid_inference_thread_limit')
    torch.set_num_threads(max_threads)
    artifact=torch.load(path,map_location='cpu',weights_only=True)
    if artifact.get('schema_version')!=1:raise ValueError('unknown_tabular_checkpoint')
    model=NumericTableModel(artifact['family'],artifact['preprocessing']['n_features'],artifact['config'])
    model.load_state_dict(artifact['state_dict']);model.eval()
    return model,artifact
