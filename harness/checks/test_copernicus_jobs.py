"""Synthetic job/transfer tests; never instantiate the official client."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

pytest.importorskip('cdsapi')
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('jobs',ROOT/'skills/data_acquisition/01_socioeconomic_natural_change/era5/scripts/copernicus_jobs.py')
jobs=importlib.util.module_from_spec(spec);spec.loader.exec_module(jobs)

def manager(tmp_path):
    return jobs.CopernicusJobs(tmp_path/'jobs',tmp_path/'cache',max_total_bytes=20,max_package_bytes=10)

def test_git_root_rejected(tmp_path):
    (tmp_path/'.git').mkdir()
    with pytest.raises(ValueError,match='private_job'):
        manager(tmp_path)

def test_reservations_survive_failed_attempts(tmp_path):
    m=manager(tmp_path)
    m._reserve('one',9);m._reserve('two',9)
    with pytest.raises(ValueError,match='remaining_budget'):m._reserve('third',3)
    assert json.loads(m.ledger.read_text())['reserved_payload_bytes']==18
    with pytest.raises(ValueError,match='remaining_budget'):m._reserve('big',11)

def test_uncertain_submission_never_repeated(tmp_path,monkeypatch):
    m=manager(tmp_path);calls=[]
    class Client:
        def retrieve(self,*args):calls.append(args);raise TimeoutError()
    monkeypatch.setattr(jobs.cdsapi,'Client',lambda **kwargs:Client())
    for _ in range(2):
        with pytest.raises((ValueError,TimeoutError)):
            m.operate('one','derived-era5-single-levels-daily-statistics',{},mode='submit')
    assert len(calls)==1

def test_saved_download_verified_without_network(tmp_path,monkeypatch):
    m=manager(tmp_path)
    target=m.cache/'one.zip';target.write_bytes(b'ok')
    job=m.jobs/'one';job.mkdir()
    jobs.save_json(job/'job.json',{'name':'one','dataset':'derived-era5-single-levels-daily-statistics',
         'request':{},'status':'successful','download':{'sha256':jobs.sha256(target)}})
    monkeypatch.setattr(jobs.cdsapi,'Client',lambda **kwargs:pytest.fail('network'))
    assert m.operate('one','derived-era5-single-levels-daily-statistics',{})['downloaded']
    target.write_bytes(b'changed')
    with pytest.raises(ValueError,match='saved_source_changed'):
        m.operate('one','derived-era5-single-levels-daily-statistics',{})

@pytest.mark.parametrize('response_bytes,declared,status,reason',[
    (b'1234',3,200,'exceeds_declared'),(b'12',3,200,'incomplete'),(b'123',3,302,'http_status')])
def test_payload_refusals_are_charged_and_preserved(tmp_path,monkeypatch,response_bytes,declared,status,reason):
    import io
    m=manager(tmp_path)
    class Response:
        status_code=status;headers={};raw=io.BytesIO(response_bytes)
        def __enter__(self):return self
        def __exit__(self,*args):pass
    class Session:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def get(self,*args,**kwargs):
            assert kwargs['verify'] is True and kwargs['allow_redirects'] is False
            assert isinstance(self.auth,jobs.NoAdditionalAuth)
            return Response()
    monkeypatch.setattr(jobs.requests,'Session',Session)
    remote=SimpleNamespace(get_results=lambda:SimpleNamespace(content_length=declared,location='https://example.invalid/result'))
    with pytest.raises(ValueError,match=reason):m.download(remote,m.cache/'one.zip','one')
    ledger=json.loads(m.ledger.read_text());assert ledger['reserved_payload_bytes']==declared
    assert ledger['attempts'][0]['state']=='interrupted'
    assert not (m.cache/'one.zip').exists()

def test_partial_refuses_without_spending(tmp_path):
    m=manager(tmp_path);(m.cache/'one.zip.partial').write_bytes(b'old')
    remote=SimpleNamespace(get_results=lambda:SimpleNamespace(content_length=3))
    with pytest.raises(ValueError,match='partial_download'):m.download(remote,m.cache/'one.zip','one')
    assert not m.ledger.exists()


@pytest.mark.parametrize('exception_type', [RuntimeError, ValueError])
def test_sdk_error_is_private_and_uncertain_submission_not_repeated(tmp_path,monkeypatch,exception_type):
    import traceback
    m=manager(tmp_path);calls=[]
    class Client:
        def retrieve(self,*args):
            calls.append(args)
            raise exception_type('SYNTHETIC_PRIVATE_SENTINEL signed-url?token=private')
    monkeypatch.setattr(jobs.cdsapi,'Client',lambda **kwargs:Client())
    with pytest.raises(ValueError,match='^copernicus_operation_failed$') as exc:
        m.operate('one','derived-era5-single-levels-daily-statistics',{},mode='submit')
    assert 'SYNTHETIC_PRIVATE_SENTINEL' not in ''.join(traceback.format_exception(exc.type,exc.value,exc.tb))
    assert exc.value.__suppress_context__
    record=json.loads((m.jobs/'one'/'job.json').read_text())
    assert record['submission_started'] and 'request_id' not in record
    with pytest.raises(ValueError,match='^no_saved_request_or_uncertain_submission$'):
        m.operate('one','derived-era5-single-levels-daily-statistics',{},mode='submit')
    assert len(calls)==1


def test_download_exception_private_and_failed_reservation_retained(tmp_path,monkeypatch):
    import traceback
    m=manager(tmp_path)
    class Session:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def get(self,*args,**kwargs):
            raise jobs.requests.ConnectionError('SYNTHETIC_PRIVATE_SENTINEL signed-url?token=private')
    monkeypatch.setattr(jobs.requests,'Session',Session)
    remote=SimpleNamespace(get_results=lambda:SimpleNamespace(content_length=3,location='https://example.invalid'))
    with pytest.raises(ValueError,match='^result_download_failed$') as exc:
        m.download(remote,m.cache/'one.zip','one')
    assert 'SYNTHETIC_PRIVATE_SENTINEL' not in ''.join(traceback.format_exception(exc.type,exc.value,exc.tb))
    assert exc.value.__suppress_context__
    ledger=json.loads(m.ledger.read_text())
    assert ledger['reserved_payload_bytes']==3 and ledger['attempts'][0]['state']=='interrupted'


def test_download_metadata_exception_is_private(tmp_path):
    m=manager(tmp_path)
    def fail():raise RuntimeError('SYNTHETIC_PRIVATE_SENTINEL')
    with pytest.raises(ValueError,match='^result_metadata_failed$') as exc:
        m.download(SimpleNamespace(get_results=fail),m.cache/'one.zip','one')
    assert exc.value.__suppress_context__ and not m.ledger.exists()


def test_download_refuses_outside_cache_and_existing_target_before_network(tmp_path):
    m=manager(tmp_path)
    remote=SimpleNamespace(get_results=lambda:pytest.fail('network'))
    with pytest.raises(ValueError,match='outside_private_cache'):
        m.download(remote,tmp_path/'outside.zip','one')
    target=m.cache/'one.zip';target.write_bytes(b'original')
    with pytest.raises(ValueError,match='unrecorded_target'):
        m.download(remote,target,'one')
    assert target.read_bytes()==b'original' and not m.ledger.exists()


def test_download_refuses_cache_symlink_escape(tmp_path):
    m=manager(tmp_path)
    outside=tmp_path/'outside';outside.mkdir()
    link=m.cache/'linked'
    try:link.symlink_to(outside,target_is_directory=True)
    except OSError:pytest.skip('directory symlinks unavailable')
    remote=SimpleNamespace(get_results=lambda:pytest.fail('network'))
    with pytest.raises(ValueError,match='outside_private_cache'):
        m.download(remote,link/'one.zip','one')
    assert not (outside/'one.zip').exists() and not m.ledger.exists()


@pytest.mark.parametrize('race', [False,True])
def test_download_publication_never_overwrites_target(tmp_path,monkeypatch,race):
    import io
    m=manager(tmp_path);target=m.cache/'one.zip'
    class Response:
        status_code=200;headers={};raw=io.BytesIO(b'new')
        def __enter__(self):return self
        def __exit__(self,*args):
            if race:target.write_bytes(b'other-writer')
    class Session:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def get(self,*args,**kwargs):return Response()
    monkeypatch.setattr(jobs.requests,'Session',Session)
    remote=SimpleNamespace(get_results=lambda:SimpleNamespace(content_length=3,location='https://example.invalid'))
    if race:
        with pytest.raises(ValueError,match='^result_download_failed$'):
            m.download(remote,target,'one')
        assert target.read_bytes()==b'other-writer'
        assert target.with_suffix('.zip.partial').read_bytes()==b'new'
    else:
        m.download(remote,target,'one')
        assert target.read_bytes()==b'new' and not target.with_suffix('.zip.partial').exists()
    ledger=json.loads(m.ledger.read_text())
    assert ledger['reserved_payload_bytes']==3
    assert ledger['attempts'][0]['state']==('interrupted' if race else 'downloaded')
