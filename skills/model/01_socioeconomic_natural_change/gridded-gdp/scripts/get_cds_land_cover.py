"""Stage one annual land-cover request, retaining its official request identity.

Called by Get-CdsLandCover.ps1 after request/path validation. No credential files
are inspected here; only the existing official client's mechanism is used.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys
import zipfile


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def nc_signature(path):
    with Path(path).open('rb') as source:
        magic = source.read(8)
    return magic[:4] in (b'CDF\x01', b'CDF\x02', b'CDF\x05') or magic == b'\x89HDF\r\n\x1a\n'


def stage(request, destination, factory, max_bytes, max_extracted_bytes):
    destination = Path(destination)
    year = int(request['year'][0])
    identity = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    name = f'landcover_{year}_{identity[:16]}'
    target = destination / f'land_cover_{year}.nc'
    receipt = target.with_suffix('.nc.source.json')
    if target.exists() or receipt.exists():
        saved = json.loads(receipt.read_text(encoding='utf-8'))
        if (saved['request_sha256'] != identity or saved['year'] != year or
                target.is_symlink() or sha256(target) != saved['sha256']):
            raise ValueError('existing_land_cover_changed')
        return {'status': 'downloaded', 'reused': True}
    jobs = destination / 'cds-jobs'
    cache = destination / 'cds-cache'
    client = factory(jobs, cache, max_total_bytes=3 * max_bytes, max_package_bytes=max_bytes)
    saved_job = jobs / name / 'job.json'
    mode = 'download' if saved_job.exists() else 'submit'
    result = client.operate(name, 'satellite-land-cover', request, mode=mode, suffix='.nc')
    if mode == 'submit' and result['status'] == 'successful':
        result = client.operate(name, 'satellite-land-cover', request, mode='download', suffix='.nc')
    if not result.get('downloaded'):
        return {'status': 'pending', 'remote_status': result['status']}
    raw = cache / (name + '.nc')
    pending = target.with_suffix('.nc.pending')
    # Retain interrupted conversion evidence rather than overwriting it on retry.
    with pending.open('xb') as output:
        if zipfile.is_zipfile(raw):
            with zipfile.ZipFile(raw) as archive:
                members = [entry for entry in archive.infolist() if entry.filename.lower().endswith('.nc')]
                if len(members) != 1 or not 0 < members[0].file_size <= max_extracted_bytes:
                    raise ValueError('unexpected_land_cover_archive')
                with archive.open(members[0]) as source:
                    shutil.copyfileobj(source, output)
        else:
            if not 0 < raw.stat().st_size <= max_extracted_bytes:
                raise ValueError('land_cover_size_limit')
            with raw.open('rb') as source:
                shutil.copyfileobj(source, output)
    if not nc_signature(pending):
        raise ValueError('unexpected_land_cover_container')
    target.hardlink_to(pending)
    pending.unlink()
    receipt.write_text(json.dumps({
        'product': 'C3S satellite-land-cover', 'version': '2.1.1', 'year': year,
        'path': target.name, 'sha256': sha256(target), 'request_sha256': identity,
        'job': name,
    }, indent=2), encoding='utf-8')
    return {'status': 'downloaded', 'reused': False}


def main():
    request_path, destination, helper, max_bytes, max_extracted = sys.argv[1:]
    module_spec = importlib.util.spec_from_file_location('copernicus_jobs', helper)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    request = json.loads(Path(request_path).read_text(encoding='utf-8-sig'))
    try:
        result = stage(request, destination, module.CopernicusJobs, int(max_bytes), int(max_extracted))
    except Exception:
        raise SystemExit('CDS staging incomplete. Retain saved jobs and inspect the official request status.') from None
    print(json.dumps(result))


if __name__ == '__main__':
    main()
