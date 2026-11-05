"""Durable official-client jobs and bounded result downloads for trusted callers.

This is a direct helper, not a registered runner or credential broker. A caller
must review the exact dataset/request and authorize network and client access.
Job records may contain private task references; do not publish them.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import logging
import re
import warnings

import cdsapi
import requests
from requests.auth import AuthBase


_SAFE_OPERATION_ERRORS = frozenset({
    'no_saved_request_or_uncertain_submission', 'partial_download_requires_review',
    'unrecorded_target_requires_review', 'download_target_outside_private_cache',
    'transfer_cap_changed', 'payload_attempt_cap', 'declared_payload_exceeds_remaining_budget',
    'unexpected_result_http_status', 'result_content_length_mismatch',
    'incomplete_result_stream', 'result_exceeds_declared_size',
    'result_metadata_failed', 'result_download_failed',
})


def _safe_error(exc, fallback):
    # Preserve only our value-free classifications, never arbitrary SDK text.
    if (type(exc) is ValueError and len(exc.args) == 1 and isinstance(exc.args[0], str)
            and exc.args[0] in _SAFE_OPERATION_ERRORS):
        return ValueError(exc.args[0])
    return ValueError(fallback)


def save_json(path, value):
    path = Path(path)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


class NoAdditionalAuth(AuthBase):
    """Prevent netrc fallback on a result URL; retain normal proxy/TLS policy."""
    def __call__(self, request):
        return request


class CopernicusJobs:
    """One serial controller, immutable jobs, reservation-based transfer cap.

    Fresh result targets must be below a private cache outside Git. Interrupted
    payloads are retained and require caller review; failed reservations are not
    refunded. Unknown submission outcomes cannot be resubmitted automatically.
    Do not share one instance/ledger between concurrent processes.
    """
    def __init__(self, jobs_dir, cache_dir, *, max_total_bytes, max_package_bytes):
        self.jobs = Path(jobs_dir).resolve()
        self.cache = Path(cache_dir).resolve()
        for path in (self.jobs, self.cache):
            if any((p / '.git').exists() for p in (path, *path.parents)):
                raise ValueError('private_job_and_cache_roots_required')
        if (isinstance(max_total_bytes, bool) or isinstance(max_package_bytes, bool)
                or not isinstance(max_total_bytes, int) or not isinstance(max_package_bytes, int)
                or not 0 < max_package_bytes <= max_total_bytes):
            raise ValueError('positive_integer_transfer_caps_required')
        self.total = max_total_bytes
        self.package = max_package_bytes
        self.jobs.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.ledger = self.jobs / 'transfer-budget.json'

    def _reserve(self, name, declared):
        ledger = json.loads(self.ledger.read_text(encoding='utf-8')) if self.ledger.exists() else {
            'cap_bytes': self.total, 'reserved_payload_bytes': 0, 'attempts': []}
        if ledger['cap_bytes'] != self.total:
            raise ValueError('transfer_cap_changed')
        if sum(a['name'] == name for a in ledger['attempts']) >= 3:
            raise ValueError('payload_attempt_cap')
        if not isinstance(declared, int) or not 0 < declared <= min(self.package, self.total - ledger['reserved_payload_bytes']):
            raise ValueError('declared_payload_exceeds_remaining_budget')
        attempt = {'name': name, 'declared_bytes': declared, 'received_bytes': 0, 'state': 'reserved'}
        ledger['reserved_payload_bytes'] += declared
        ledger['attempts'].append(attempt)
        save_json(self.ledger, ledger)
        return ledger, attempt

    def download(self, remote, target, name):
        target = Path(target)
        resolved = target.resolve()
        if (resolved == self.cache or not resolved.is_relative_to(self.cache)
                or any((p / '.git').exists() for p in (resolved.parent, *resolved.parent.parents))):
            raise ValueError('download_target_outside_private_cache')
        if target.exists() or target.is_symlink():
            raise ValueError('unrecorded_target_requires_review')
        part = target.with_suffix(target.suffix + '.partial')
        if part.exists() or part.is_symlink():
            raise ValueError('partial_download_requires_review')
        try:
            result = remote.get_results()
            declared = result.content_length
        except Exception:
            raise ValueError('result_metadata_failed') from None
        ledger, attempt = self._reserve(name, declared)
        try:
            with requests.Session() as session:
                session.auth = NoAdditionalAuth()
                with session.get(result.location, stream=True, timeout=(30, 60), verify=True,
                                 allow_redirects=False, headers={'Accept-Encoding': 'identity'}) as response:
                    if response.status_code != 200:
                        raise ValueError('unexpected_result_http_status')
                    if response.headers.get('Content-Length') and int(response.headers['Content-Length']) != declared:
                        raise ValueError('result_content_length_mismatch')
                    response.raw.decode_content = False
                    with part.open('xb') as stream:
                        while attempt['received_bytes'] < declared:
                            block = response.raw.read(min(65536, declared - attempt['received_bytes']))
                            if not block:
                                raise ValueError('incomplete_result_stream')
                            stream.write(block)
                            attempt['received_bytes'] += len(block)
                        if response.raw.read(1):
                            raise ValueError('result_exceeds_declared_size')
            # Atomic no-clobber publication on Windows and POSIX alike.
            target.hardlink_to(part)
            part.unlink()
            attempt['state'] = 'downloaded'
        except Exception as exc:
            attempt['state'] = 'interrupted'
            raise _safe_error(exc, 'result_download_failed') from None
        finally:
            save_json(self.ledger, ledger)

    def operate(self, name, dataset, request, *, mode='status', suffix='.zip'):
        if not re.fullmatch(r'[a-z0-9_]{1,80}', name) or suffix not in {'.zip', '.grib', '.nc'}:
            raise ValueError('invalid_job_name_or_suffix')
        if mode not in {'submit', 'status', 'download'}:
            raise ValueError('invalid_job_mode')
        if dataset not in {'derived-era5-single-levels-daily-statistics', 'reanalysis-era5-single-levels', 'cams-global-reanalysis-eac4'}:
            raise ValueError('unsupported_official_dataset')
        directory = self.jobs / name
        directory.mkdir(exist_ok=True)
        record_path = directory / 'job.json'
        record = json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else {
            'name': name, 'dataset': dataset, 'request': request}
        if record['request'] != request or record['dataset'] != dataset:
            raise ValueError('saved_request_changed')
        target = self.cache / (name + suffix)
        if record.get('download'):
            if not target.is_file() or sha256(target) != record['download']['sha256']:
                raise ValueError('saved_source_changed')
            return {'name': name, 'status': record['status'], 'downloaded': True, 'bytes': target.stat().st_size}
        if target.exists():
            raise ValueError('unrecorded_target_requires_review')
        # Silence SDK logs and callbacks: errors are classified, never stringified.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            previous = logging.root.manager.disable
            logging.disable(logging.CRITICAL)
            try:
                endpoint = ('https://ads.atmosphere.copernicus.eu/api' if dataset.startswith('cams-')
                            else 'https://cds.climate.copernicus.eu/api')
                client = cdsapi.Client(url=endpoint, quiet=True, debug=False, verify=True, retry_max=1,
                    timeout=60, progress=False, wait_until_complete=False, info_callback=lambda *a, **k: None,
                    warning_callback=lambda *a, **k: None, error_callback=lambda *a, **k: None, debug_callback=lambda *a, **k: None)
                if 'request_id' not in record:
                    if mode != 'submit' or record.get('submission_started'):
                        raise ValueError('no_saved_request_or_uncertain_submission')
                    record['submission_started'] = datetime.now(timezone.utc).isoformat()
                    save_json(record_path, record)
                    remote = client.retrieve(dataset, request)
                    record['request_id'] = remote.request_id
                    save_json(record_path, record)
                else:
                    remote = client.client.get_remote(record['request_id'])
                record['status'] = remote.status
                record['checked_at'] = datetime.now(timezone.utc).isoformat()
                save_json(record_path, record)
                if mode == 'download' and record['status'] == 'successful':
                    self.download(remote, target, name)
                    record['download'] = {'file': target.name, 'bytes': target.stat().st_size, 'sha256': sha256(target)}
                    save_json(record_path, record)
            except Exception as exc:
                raise _safe_error(exc, 'copernicus_operation_failed') from None
            finally:
                logging.disable(previous)
        return {'name': name, 'status': record['status'], 'downloaded': bool(record.get('download')),
                'bytes': record.get('download', {}).get('bytes')}
