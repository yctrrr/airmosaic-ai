"""Portable artifact writers and metrics computed without sklearn metrics."""
import csv
import hashlib
import json
import math


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(actual,predicted):
    y=[float(v) for v in actual]; p=[float(v) for v in predicted]
    if not y or len(y)!=len(p) or not all(math.isfinite(v) for v in y+p): raise ValueError('nonfinite_predictions')
    errors=[a-b for a,b in zip(y,p)]; mean=sum(y)/len(y)
    denominator=sum((v-mean)**2 for v in y)
    return {'n':len(y),'rmse':math.sqrt(sum(e*e for e in errors)/len(y)),'mae':sum(abs(e) for e in errors)/len(y),'r2':1-sum(e*e for e in errors)/denominator if denominator else None}


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as handle: json.dump(value,handle,indent=2,allow_nan=False); handle.write('\n')


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
