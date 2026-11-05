"""Network-free engineering replay: eight synthetic stations, all 366 days.

Scientific operations live in repository skills. This controller supplies a
small fixture, explicit contracts and artifact handoffs; it is not real PM2.5.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import importlib.util
import importlib.metadata
import json
import shutil

import numpy as np
import pandas as pd


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repo",required=True,type=Path)
parser.add_argument("--out",required=True,type=Path)
args=parser.parse_args()
repo=args.repo.resolve();out=args.out.resolve()
if out.exists() or any((p/".git").exists() for p in (out,*out.parents)):
    raise ValueError("fresh_external_result_directory_required")
out.mkdir(parents=True)
inputs=out/"inputs";inputs.mkdir()
generated=out/"gen_script";generated.mkdir()
shutil.copyfile(Path(__file__).resolve(),generated/"run.py")
now=lambda:datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def event(action,**details):
    with (out/"events.jsonl").open("a",encoding="utf-8") as stream:
        stream.write(json.dumps({"time":now(),"action":action,**details})+"\n")


def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False),encoding="utf-8")


def csv_gzip(data,path):
    data.to_csv(path,index=False,compression={"method":"gzip","mtime":0})


dependencies={}
def load(name,relative):
    source=repo/relative
    dependencies[relative]=hashlib.sha256(source.read_bytes()).hexdigest()
    spec=importlib.util.spec_from_file_location(name,source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


space=load("compact_bilinear","skills/model/shared/spatial_analysis/scripts/python/bilinear_helpers.py")
grid=load("compact_grid_daily","skills/model/shared/spatial_analysis/scripts/python/grid_daily.py")
obs=load("compact_pm25","skills/data_acquisition/03_atmospheric_transport/pm25-stations/scripts/prepare_hourly.py")
ml=load("compact_tuning","skills/model/shared/machine_learning_model/scripts/python/models/grouped_tuning.py")
SEED=20241030
FEATURES=["t2m","d2m","u10","v10","sp","aod550"]
plan={"data_kind":"synthetic_engineering_fixture","year":2024,"calendar_days":366,
      "station_count":8,"features":FEATURES,"target":"pm25_daily_ug_m3",
      "source_precision":"synthetic fields generated as float32",
      "feature_units":{"t2m":"K","d2m":"K","u10":"m/s","v10":"m/s","sp":"Pa","aod550":"1"},
      "coordinates_are_predictors":False,"timezone":"Asia/Shanghai",
      "station_interval_labels":"start; known synthetic generator convention",
      "min_observed_hours":20,"test_groups":["S7","S8"],
      "development_folds":{"S1":1,"S2":1,"S3":2,"S4":2,"S5":3,"S6":3},
      "families_frozen_before_test":["linear_regression","decision_tree","random_forest"],
      "model_persistence":"not_written; rebuild from compact inputs and selected parameters",
      "fit_budget":{"linear_regression":1,"decision_tree":13,"random_forest":13},
      "scientific_acceptance":"not_applicable_to_synthetic_fixture"}
write_json(generated/"plan.json",plan)
write_json(generated/"environment.json",{"python":__import__('sys').version.split()[0],
    "packages":{p:importlib.metadata.version(p) for p in ["numpy","pandas","scipy","scikit-learn","joblib","threadpoolctl"]}})
write_json(generated/"dependencies.json",dependencies)
(generated/"generation-basis_ZH.md").write_text(
    "# 生成依据\n\n这是已授权沙箱任务的合成工程验证，不代替真实站点结果。采用8个合成站点和2024年全部366天，以检验年界、闰日、20小时门槛、双线性权重、完整网格采样、分组调参及测试隔离。\n\n"
    "原始数值计算由所记录的技能函数完成；本文件只生成小型输入并连接阶段。三类模型、测试站点和搜索范围在任何测试评价前固定。搜索范围仅是有界测试设置，不是对真实数据的参数推荐。\n\n"
    "未保存模型二进制或逐折模型，所有模型共享一次输入。保留小时观测、必要网格源节点、派生表、参数、折和测试预测，供重新计算及交接检查。\n",encoding="utf-8")
(generated/"generation-basis.md").write_text(
    "# Generation basis\n\nThis authorized sandbox check uses eight synthetic stations and all 366 days of 2024. It tests year/leap-day boundaries, completeness, bilinear support, grouped tuning and held-out evaluation; it is not a real-station result.\n\n"
    "Repository skills perform the scientific operations. Model families, held-out stations and bounded test search spaces are fixed before test evaluation. Search ranges exercise software and are not scientific defaults. Inputs are shared; per-fold models and model binaries are omitted because the saved inputs, settings and environment support refitting.\n",encoding="utf-8")
event("plan_frozen",data_kind="synthetic",seed=SEED)

rng=np.random.default_rng(SEED)
dates=pd.date_range("2024-01-01","2024-12-31",freq="D").strftime("%Y-%m-%d").tolist()
station_ids=[f"S{i}" for i in range(1,9)]
points=np.array([[110.4,35.4],[110.8,35.45],[111.2,35.4],[111.6,35.5],
                 [110.4,36.1],[110.8,36.4],[111.2,36.3],[111.6,36.6]])
stations=pd.DataFrame({"station_id":station_ids,"longitude":points[:,0],"latitude":points[:,1],
                       "crs":"EPSG:4326","kind":"synthetic"})
stations.to_csv(inputs/"stations.synthetic.csv",index=False)
x=110.25+np.arange(7)*.25;y=35.25+np.arange(7)*.25
xa=x[::3];ya=y[::3]
w=space.bilinear_weights(x,y,points,station_ids,"EPSG:4326","EPSG:4326")
wa=space.bilinear_weights(xa,ya,points,station_ids,"EPSG:4326","EPSG:4326")
w.to_csv(inputs/"meteorology-weights.csv",index=False);wa.to_csv(inputs/"aod-weights.csv",index=False)
hourly_times=pd.date_range("2023-12-31 16:00",periods=366*24,freq="h",tz="UTC")
aod_times=pd.date_range("2023-12-31 18:00",periods=366*8,freq="3h",tz="UTC")
day=np.repeat(np.arange(366),24)[:,None,None]
hour=np.tile(np.arange(24),366)[:,None,None]
xx=x[None,None,:]-110.25;yy=y[None,:,None]-35.25
season=np.sin(day*2*np.pi/366);diurnal=np.sin(hour*2*np.pi/24)
synoptic=np.repeat(rng.normal(0,1,366),24)[:,None,None]
fields={
    "t2m":(285+10*season+xx*.5-yy*.3+2*diurnal+synoptic).astype("float32"),
    "d2m":(280+8*season+xx*.2-yy*.4+diurnal+synoptic*.8).astype("float32"),
    "u10":(2*np.sin(day*2*np.pi/7)+xx*.3+yy*0+diurnal).astype("float32"),
    "v10":(2*np.cos(day*2*np.pi/11)+yy*.2+xx*0+diurnal*.5).astype("float32"),
    "sp":(100000+100*np.cos(day*2*np.pi/366)-yy*30+xx*0+diurnal*50).astype("float32")}
fields["sp"][4*24,3,3]=np.nan
ad=np.repeat(np.arange(366),8)[:,None,None];ah=np.tile(np.arange(2,24,3),366)[:,None,None]
aod=(.2+.08*np.sin(ad*2*np.pi/13)+.02*(xa[None,None,:]-110.25)
     +.04*(ya[None,:,None]-35.25)+.01*np.sin(ah*2*np.pi/24)).astype("float32")
# Keep only the source nodes actually needed by station and output-grid weights.
grid_points=np.array([(gx,gy) for gy in ya for gx in xa])
grid_ids=[f"G{i}" for i in range(len(grid_points))]
gw=space.bilinear_weights(x,y,grid_points,grid_ids,"EPSG:4326","EPSG:4326")
gaw=space.bilinear_weights(xa,ya,grid_points,grid_ids,"EPSG:4326","EPSG:4326")
nodes=pd.concat([w,gw]).query("weight > 0")[["row_index","col_index"]].drop_duplicates().sort_values(["row_index","col_index"])
anodes=pd.concat([wa,gaw]).query("weight > 0")[["row_index","col_index"]].drop_duplicates().sort_values(["row_index","col_index"])
packed={name:values[:,nodes.row_index.to_numpy()-1,nodes.col_index.to_numpy()-1] for name,values in fields.items()}
packed.update({"aod550":aod[:,anodes.row_index.to_numpy()-1,anodes.col_index.to_numpy()-1],
               "meteorology_nodes":nodes.to_numpy(),"aod_nodes":anodes.to_numpy(),"x":x,"y":y,"aod_x":xa,"aod_y":ya,
               "hourly_utc":hourly_times.astype(str).to_numpy(dtype="U25"),
               "aod_utc":aod_times.astype(str).to_numpy(dtype="U25")})
np.savez_compressed(inputs/"source-stencils.synthetic.npz",**packed)
daily_fields={name:grid.daily_grid_mean(values,hourly_times,dates,timezone="Asia/Shanghai",sample_interval_hours=1)["values"]
              for name,values in fields.items()}
daily_fields["aod550"]=grid.daily_grid_mean(aod,aod_times,dates,timezone="Asia/Shanghai",sample_interval_hours=3)["values"]
prepared=pd.DataFrame({"date_local":np.repeat(dates,8),"station_id":station_ids*366})
grid_input=pd.DataFrame({"date_local":np.repeat(dates,len(grid_ids)),"grid_id":grid_ids*366})
for name,values in daily_fields.items():
    sw=wa if name=="aod550" else w;tw=gaw if name=="aod550" else gw
    prepared[name]=np.concatenate([space.sample_bilinear(v,sw)["value"].to_numpy() for v in values])
    grid_input[name]=np.concatenate([space.sample_bilinear(v,tw)["value"].to_numpy() for v in values])
event("grid_prepared",days=366,meteorology_sample_count=24,aod_sample_count=8,source_nodes=len(nodes),aod_nodes=len(anodes))
truth=(20+50*prepared.aod550-.2*(prepared.t2m-285)+.04*(prepared.d2m-280)**2
       +1.2*(prepared.u10**2+prepared.v10**2)+rng.normal(0,1,len(prepared))).to_numpy()
records=[]
for i,row in prepared.iterrows():
    for h in range(24):
        value=truth[i]+3*np.sin(h*2*np.pi/24)+rng.normal(0,.3)
        missing=(i==0 and h<5) or (i==9 and h<4)
        records.append((row.station_id,row.date_local.replace("-",""),h,"" if missing else f"{value:.6f}"))
hourly=pd.DataFrame(records,columns=["station_id","date_raw","hour_raw","value_raw"])
csv_gzip(hourly,inputs/"station-hours.synthetic.csv.gz")
_,daily=obs.prepare_daily(hourly,{"status":"reviewed","timezone":"Asia/Shanghai","hour_label":"start",
                               "evidence":"known_synthetic_generator"},20)
data=prepared.merge(daily,on=["station_id","date_local"],validate="one_to_one").rename(columns={"pm25_mean":plan["target"]})
assert len(data)==366*8 and len(daily)==366*8 and daily.n_valid_hours.min()==19
data["split"]=np.where(data.station_id.isin(plan["test_groups"]),"test","development")
data["fold_id"]=data.station_id.map(plan["development_folds"])
csv_gzip(data,inputs/"prepared-daily.synthetic.csv.gz")
event("station_daily_prepared",selected_station_count=8,source_hours=len(hourly),incomplete_days=int(data[plan['target']].isna().sum()))
valid=data[data[plan["target"]].notna()]
development=valid[valid.split=="development"].copy();test=valid[valid.split=="test"].copy()
assert set(development.station_id).isdisjoint(set(test.station_id))
csv_gzip(data[["station_id","date_local","split","fold_id"]],inputs/"split-and-folds.csv.gz")
settings={
    "linear_regression":({}, {},1,1),
    "decision_tree":({"max_depth":[3,6,10],"min_samples_leaf":[3,12]}, {},4,13),
    "random_forest":({"min_samples_leaf":[3,12],"max_features":[.5,1.]}, {"n_estimators":64,"max_depth":10},4,13)}
write_json(generated/"search-settings.json",{name:{"search_space":v[0],"fixed_parameters":v[1],"n_iter":v[2],"max_fits":v[3]}
    for name,v in settings.items()})
metrics={};selected={};predictions=[];grid_predictions=[]
for learner,(search,fixed,iterations,budget) in settings.items():
    event("model_started",learner=learner)
    result=ml.fit_grouped_regression(development,test,features=FEATURES,target=plan["target"],group_column="station_id",
        fold_id=development.fold_id.astype(int).tolist(),learner=learner,search_space=search,fixed_parameters=fixed,
        n_iter=iterations,seed=SEED,max_fits=budget)
    metrics[learner]=result["test_metrics"]
    selected[learner]={k:v for k,v in result["selection"].items() if k!="fold_id"}
    selected[learner]["fold_assignment_ref"]="inputs/split-and-folds.csv.gz"
    cv=result["cv_results"]
    if not cv.empty:
        cv[[c for c in cv.columns if "time" not in c]].to_json(out/(learner+"-cv.json"),orient="records",indent=2)
    pred=result["predictions"].copy();pred.insert(0,"date_local",test.date_local.to_numpy());pred.insert(0,"station_id",test.station_id.to_numpy());pred.insert(0,"learner",learner)
    predictions.append(pred)
    gp=grid_input[["grid_id","date_local"]].copy();gp["learner"]=learner
    gp["predicted"]=result["estimator"].predict(grid_input[FEATURES].to_numpy())
    grid_predictions.append(gp)
    event("model_finished",learner=learner,fits=result["selection"]["fits_required"],test_used_for_selection=False)
write_json(out/"metrics.json",metrics);write_json(out/"selection.json",selected)
csv_gzip(pd.concat(predictions),out/"test-predictions.csv.gz")
csv_gzip(pd.concat(grid_predictions),out/"grid-predictions.synthetic.csv.gz")
write_json(out/"workflow.json",{"status":"synthetic_passed","seed":SEED,
    "plan_ref":"gen_script/plan.json","settings_ref":"gen_script/search-settings.json",
    "generation_basis_ref":"gen_script/generation-basis.md","events_ref":"events.jsonl",
    "retrospective_ref":"retrospective.md","data_kind":"synthetic_engineering_fixture",
    "repository_adapter":False,"scientific_acceptance":False})
event("workflow_completed",status="synthetic_passed",development_rows=len(development),test_rows=len(test))
footprint={p.relative_to(out).as_posix():p.stat().st_size for p in out.rglob("*") if p.is_file()}
write_json(out/"footprint.json",{"files":footprint,"total_bytes":sum(footprint.values()),"models_written":False,
    "shared_inputs_once":True,"intermediate_grid_nodes_only":True,"contains_real_stations":False})
(out/"retrospective_ZH.md").write_text(
    f"# 回顾性摘要\n\n合成流程完成：8站、366天，开发记录{len(development)}条，测试记录{len(test)}条，四个阶段均调用项目技能。\n\n"
    "检验覆盖20小时门槛、闰日/跨年UTC窗口、1小时及3小时完整采样、双线性缺失支撑、站点组隔离、折内预处理和有界调参。\n\n"
    f"产物约{sum(footprint.values())/1024/1024:.2f} MiB，不保存每折模型或重复数据。真实站点建模仍等待2024历史位置、坐标系和时间标签依据；这些合成分数不能作为中国PM2.5预测精度。\n",encoding="utf-8")
(out/"retrospective.md").write_text(
    f"# Retrospective\n\nSynthetic replay passed: eight stations, 366 days, {len(development)} development and {len(test)} test records. Repository skills performed preparation, daily aggregation, spatial sampling and grouped regression.\n\n"
    f"The current artifacts occupy approximately {sum(footprint.values())/1024/1024:.2f} MiB. Inputs are shared and only required source nodes are stored; per-fold models are not retained. Historical station metadata and time semantics remain prerequisites for real-station modelling. Synthetic scores are not Chinese PM2.5 predictive performance.\n",encoding="utf-8")
write_json(out/"delivery-sha256.json",{p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
    for p in out.rglob("*") if p.is_file() and p.name!="delivery-sha256.json"})
print(json.dumps({"status":"synthetic_passed","stations":8,"days":366,"development_rows":len(development),
    "test_rows":len(test),"artifact_bytes":sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),
    "metrics":{name:{k:v for k,v in values.items() if k in {'rmse','mae','r2'}} for name,values in metrics.items()}}))
