"""Inventory, measure or retrieve public inputs from a Classic native dry-run.

HTTPS is anonymous and restricted to the official public data bucket. No AWS
SDK, login profile, personal configuration, retries or partial-file overwrite.
"""
import argparse,json,os,re,sys,urllib.parse,urllib.request
from pathlib import Path
from gc_paths import sandbox_root,within,digest,save_new,save_state

PORTAL='https://geos-chem.s3-us-west-2.amazonaws.com/'
RESTART_KEY='GEOSCHEM_RESTARTS/GC_14.8.0/GEOSChem.Restart.TransportTracers.20190101_0000z.nc4'
LEDGER_NAME='input-transfer-ledger.json'

class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not newurl.startswith(PORTAL):raise ValueError('unapproved_redirect')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def open_public(key,method='GET'):
    if not key or key.startswith('/') or '..' in Path(key).parts or any(c in key for c in '?&#\\\r\n'):
        raise ValueError('invalid_public_object_key')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),RestrictedRedirect())
    request=urllib.request.Request(PORTAL+urllib.parse.quote(key,safe='/'),method=method)
    return opener.open(request,timeout=60)

def inventory(root,data,run,log):
    root=sandbox_root(root);data=within(root,data,must_exist=True);run=within(root,run,must_exist=True)
    log=within(root,log,must_exist=True);items={}
    for line in log.read_text(errors='replace').splitlines():
        upper=line.upper()
        if not any(x in upper for x in (': OPENING',': READING','FILE NOT FOUND')):continue
        raw=line.split()[-1];path=Path(raw)
        if not path.is_absolute():path=run/path
        path=within(root,path)
        if path.is_file():continue
        try:key=path.relative_to(data).as_posix()
        except ValueError:
            if path==run/'Restarts/GEOSChem.Restart.20190101_0000z.nc4':key=RESTART_KEY
            else:raise ValueError('missing_input_outside_supported_data_mapping')
        items[str(path)]={'target':path.relative_to(root).as_posix(),'key':key}
    if not items:raise ValueError('no_missing_inputs_in_log')
    return {'schema':1,'portal':PORTAL,'files':sorted(items.values(),key=lambda x:x['target']),
        'measured':False,'scientific_validation':False}

def validate_manifest(root,manifest):
    if manifest.get('schema')!=1 or manifest.get('portal')!=PORTAL or not manifest.get('files'):
        raise ValueError('unsupported_input_manifest')
    seen=set()
    for item in manifest['files']:
        target=within(root,item['target'])
        if target in seen:raise ValueError('duplicate_input_target')
        seen.add(target)
        key=item['key']
        if not key or key.startswith('/') or '..' in Path(key).parts or any(c in key for c in '?&#\\\r\n'):
            raise ValueError('invalid_public_object_key')
        if 'bytes' in item and (type(item['bytes']) is not int or item['bytes']<=0):
            raise ValueError('positive_integer_input_size_required')

def measure(root,manifest,max_bytes):
    validate_manifest(root,manifest)
    total=0
    for item in manifest['files']:
        with open_public(item['key'],'HEAD') as response:
            length=int(response.headers.get('Content-Length','0'))
            if length<=0:raise ValueError('unknown_remote_size')
            item['bytes']=length;total+=length
    manifest.update(measured=True,total_bytes=total,within_budget=total<=max_bytes)
    return manifest

def fetch(root,manifest,ledger_path,max_bytes):
    validate_manifest(root,manifest)
    if not manifest.get('measured') or any('bytes' not in x for x in manifest['files']):
        raise ValueError('measure_before_fetch')
    if not 0<max_bytes<=2*1024**3:raise ValueError('input_budget_limit')
    ledger_path=within(root,ledger_path)
    if ledger_path!=within(root,LEDGER_NAME):raise ValueError('canonical_task_ledger_required')
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'reserved_bytes':0,'transfers':[]}
    if (type(ledger.get('reserved_bytes')) is not int or ledger['reserved_bytes']<0
            or not isinstance(ledger.get('transfers'),list)
            or any(type(x.get('bytes')) is not int or x['bytes']<=0 for x in ledger['transfers'])
            or ledger['reserved_bytes']!=sum(x['bytes'] for x in ledger['transfers'])):
        raise ValueError('invalid_task_transfer_ledger')
    pending=[]
    for item in manifest['files']:
        target=within(root,item['target']);partial=target.with_name(target.name+'.partial')
        if target.exists() or partial.exists():raise ValueError('fresh_input_targets_required')
        pending.append((item,target,partial))
    if ledger['reserved_bytes']+sum(x[0]['bytes'] for x in pending)>max_bytes:
        raise ValueError('cumulative_input_budget_exceeded')
    for item,target,partial in pending:
        target.parent.mkdir(parents=True,exist_ok=True)
        # Reserve the full attempted object before the network request; failures
        # retain their reservation and partial evidence rather than auto-retrying.
        record=dict(item,status='started');ledger['transfers'].append(record)
        ledger['reserved_bytes']+=item['bytes'];save_state(ledger_path,ledger)
        try:
            count=0
            with open_public(item['key']) as response,partial.open('xb') as stream:
                if int(response.headers.get('Content-Length','0'))!=item['bytes']:
                    raise ValueError('remote_size_changed')
                while True:
                    chunk=response.read(min(1024*1024,item['bytes']-count+1))
                    if not chunk:break
                    count+=len(chunk)
                    if count>item['bytes']:raise ValueError('remote_size_exceeded')
                    stream.write(chunk)
            if count!=item['bytes']:raise ValueError('incomplete_input_transfer')
            # A single caller owns this task; an existing destination is refused.
            if target.exists():raise ValueError('input_destination_appeared')
            partial.rename(target);record.update(status='complete',sha256=digest(target))
        except Exception as error:
            record.update(status='failed',error_type=type(error).__name__)
            raise
        finally:save_state(ledger_path,ledger)
    return ledger

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['inventory','measure','fetch'])
    for name in ('root','manifest'):p.add_argument('--'+name,required=True)
    for name in ('data','run','log','output','ledger'):p.add_argument('--'+name)
    p.add_argument('--max-bytes',type=int,default=2*1024**3);p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    try:
        root=sandbox_root(a.root);manifest_path=within(root,a.manifest)
        if a.mode=='inventory':
            if not all((a.data,a.run,a.log)):raise ValueError('inventory_paths_required')
            value=inventory(root,a.data,a.run,a.log);save_new(manifest_path,value)
        else:
            value=json.loads(manifest_path.read_text());validate_manifest(root,value)
            if a.mode=='measure':
                if not a.output:raise ValueError('fresh_measured_output_required')
                output=within(root,a.output)
                if output.exists():raise ValueError('fresh_measured_output_required')
                value=measure(root,value,a.max_bytes);save_new(output,value)
            else:
                if not a.execute or not a.ledger:raise ValueError('explicit_execution_and_ledger_required')
                value=fetch(root,value,a.ledger,a.max_bytes)
        print(json.dumps({'mode':a.mode,'files':len(value.get('files',value.get('transfers',[]))),
            'total_bytes':value.get('total_bytes',value.get('reserved_bytes')),
            'within_budget':value.get('within_budget'),'scientific_validation':False}))
    except Exception as e:print(json.dumps({'status':'failed','error_type':type(e).__name__}));return 1
    return 0
if __name__=='__main__':sys.exit(main())
