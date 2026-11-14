"""Bounded synthetic checks for acquisition, annual append and local promotion.

No real datasets, account inspection or live Copernicus calls. Run with a private
pytest --basetemp outside Git; R spatial packages and PowerShell 7 are required
for the integration fixture, while the CDS staging tests use an injected fake.
"""
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
GDP = ROOT / 'skills/model/01_socioeconomic_natural_change/gridded-gdp/scripts'
PUBLIC = ROOT / 'skills/data_acquisition/shared/public-data/scripts'
spec = importlib.util.spec_from_file_location('land_cover', GDP / 'get_cds_land_cover.py')
land_cover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(land_cover)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def call(arguments, *, ok=True):
    result = subprocess.run([str(a) for a in arguments], cwd=ROOT, text=True,
                            capture_output=True, encoding='utf-8', errors='replace', timeout=180)
    if ok:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0, result.stdout
    return result.stdout + result.stderr


def powershell(script, *args, **kwargs):
    if not shutil.which('pwsh'):
        pytest.skip('PowerShell 7 required')
    return call(['pwsh', '-NoProfile', '-File', script, *args], **kwargs)


@pytest.mark.parametrize('container', ['netcdf', 'zip'])
def test_cds_pending_request_is_reused_without_resubmission(tmp_path, container):
    calls = []

    class FakeJobs:
        def __init__(self, jobs, cache, **budgets):
            self.jobs, self.cache = jobs, cache
            jobs.mkdir(exist_ok=True)
            cache.mkdir(exist_ok=True)
            assert budgets['max_total_bytes'] == 3 * budgets['max_package_bytes']

        def operate(self, name, dataset, request, *, mode, suffix):
            calls.append(mode)
            assert dataset == 'satellite-land-cover'
            directory = self.jobs / name
            directory.mkdir(exist_ok=True)
            (directory / 'job.json').write_text('{}')
            if mode == 'submit':
                return {'status': 'accepted', 'downloaded': False}
            target = self.cache / (name + suffix)
            payload = b'CDF\x01' + b'\0' * 20
            if container == 'zip':
                with zipfile.ZipFile(target, 'w') as archive:
                    archive.writestr('nested/annual.nc', payload)
            else:
                target.write_bytes(payload)
            return {'status': 'successful', 'downloaded': True}

    request = {'year': ['2024'], 'variable': 'all', 'version': 'v2_1_1', 'area': [31, 100, 30, 101]}
    assert land_cover.stage(request, tmp_path, FakeJobs, 1000, 1000)['status'] == 'pending'
    assert land_cover.stage(request, tmp_path, FakeJobs, 1000, 1000)['status'] == 'downloaded'
    assert land_cover.stage(request, tmp_path, FakeJobs, 1000, 1000)['reused']
    assert calls == ['submit', 'download']
    assert land_cover.nc_signature(tmp_path / 'land_cover_2024.nc')
    altered = dict(request, area=[32, 100, 30, 101])
    with pytest.raises(ValueError, match='existing_land_cover_changed'):
        land_cover.stage(altered, tmp_path, FakeJobs, 1000, 1000)
    target = tmp_path / 'land_cover_2024.nc'
    target.write_bytes(b'changed')
    with pytest.raises(ValueError, match='existing_land_cover_changed'):
        land_cover.stage(request, tmp_path, FakeJobs, 1000, 1000)


@pytest.mark.parametrize('payload,reason', [(b'HTML error', 'container'), (b'CDF\x01' + b'x' * 200, 'size_limit')])
def test_cds_invalid_response_not_promoted(tmp_path, payload, reason):
    class FakeJobs:
        def __init__(self, jobs, cache, **kwargs):
            self.cache = cache
            cache.mkdir(exist_ok=True)

        def operate(self, name, dataset, request, **kwargs):
            (self.cache / (name + '.nc')).write_bytes(payload)
            return {'status': 'successful', 'downloaded': True}

    with pytest.raises(ValueError, match=reason):
        land_cover.stage({'year': ['2024']}, tmp_path, FakeJobs, 1000, 100)
    assert not (tmp_path / 'land_cover_2024.nc').exists()
    assert (tmp_path / 'land_cover_2024.nc.pending').exists()


@pytest.mark.parametrize('fault', ['checksum', 'unavailable', 'budget', 'multiple_tiffs'])
def test_dataverse_provider_refusals(tmp_path, fault):
    archive = tmp_path / '2024_Version2.zip'
    with zipfile.ZipFile(archive, 'w') as output:
        output.writestr('annual.tif', b'synthetic raster payload')
        if fault == 'multiple_tiffs':
            output.writestr('second.tif', b'other')
    md5 = hashlib.md5(archive.read_bytes()).hexdigest()
    version = {'versionState': 'RELEASED', 'versionNumber': 1, 'versionMinorNumber': 0, 'files': [
        {'label': archive.name, 'restricted': False,
         'dataFile': {'id': 1, 'filesize': archive.stat().st_size,
                      'checksum': {'type': 'MD5', 'value': '0' * 32 if fault == 'checksum' else md5}}}]}
    catalog = tmp_path / 'catalog.json'
    catalog.write_text(json.dumps(version))
    destination = tmp_path / 'download'
    destination.mkdir()
    output = powershell(PUBLIC / 'Get-DataverseRaster.ps1', '-Years', 2023 if fault == 'unavailable' else 2024,
                        '-Doi', '10.0000/SYNTHETIC', '-FixtureCatalog', catalog,
                        '-Action', 'Download', '-Destination', destination,
                        '-MaxArchiveBytes', 1 if fault == 'budget' else 10000, ok=False)
    assert not list(destination.glob('202*-dataverse-*'))
    assert any(word in output.lower() for word in ['checksum', 'unavailable', 'exactly one tiff'])


@pytest.fixture(scope='module')
def synthetic(tmp_path_factory):
    if not shutil.which('Rscript'):
        pytest.skip('Rscript and spatial packages required')
    base = tmp_path_factory.mktemp('gdp')
    run = base / 'run'
    controller = ROOT / 'workflows/gridded_gdp/Invoke-GriddedGdp.ps1'
    output = powershell(controller, '-RunDirectory', run, '-Mode', 'synthetic', '-Append')
    record = json.loads((run / 'workflow.json').read_text())
    assert record['status'] == 'accepted'
    candidates = [run / 'work/candidates' / name for name in record['candidates']]
    return base, run, candidates, output


def test_crop_keeps_each_annual_release_identity(synthetic, tmp_path):
    _, run, _, _ = synthetic
    raster = run / 'fixture/inputs/light-2022.tif'
    config = json.loads((run / 'resolved-initial.json').read_text())
    crops = []
    for year in (2022, 2023):
        receipt = tmp_path / f'{year}.json'
        receipt.write_text(json.dumps({'year': year, 'version': '2.0', 'product': 'synthetic',
                                       'file_id': year, 'sha256': digest(raster)}))
        output = call(['Rscript', '--vanilla', PUBLIC / 'crop_annual_raster.R',
                       raster, tmp_path, receipt, *config['geo']['extent']])
        # R's locale warnings go to stderr and can follow the stdout path.
        crop = next(p for p in tmp_path.iterdir() if p.is_dir() and p not in crops)
        saved = json.loads((crop / 'source.json').read_text())
        assert saved['year'] == year and saved['file_id'] == year, output
        crops.append(crop)
    assert digest(crops[0] / 'crop.tif') == digest(crops[1] / 'crop.tif')


def test_full_workflow_metrics_and_annual_model_reuse(synthetic):
    base, run, candidates, output = synthetic
    assert len(candidates) == 2
    assert output.count('COMPLETE fit') == 1
    assert output.count('COMPLETE validation') == 1
    assert 'REUSED accepted_model' in output
    receipts = [json.loads((p / 'receipt.json').read_text()) for p in candidates]
    assert receipts[0]['model_signature'] == receipts[1]['model_signature']
    assert receipts[0]['validation_signature'] == receipts[1]['validation_signature']
    assert receipts[0]['file_hashes']['County_interpolate/' + receipts[0]['model_file']] == receipts[1]['file_hashes']['County_interpolate/' + receipts[1]['model_file']]
    for candidate, receipt in zip(candidates, receipts):
        for name, expected in receipt['file_hashes'].items():
            assert digest(candidate / name) == expected
        with (candidate / 'grid_acceptance.csv').open() as source:
            acceptance = next(csv.DictReader(source))
        assert int(acceptance['valid_cells']) == 800
        assert int(acceptance['positive_counties']) == 8
        assert float(acceptance['province_max_rel']) < 1e-12
        assert float(acceptance['county_max_rel']) < 0.001
    paired = next((run / 'work/checkpoints/validation').glob('*/paired_before_calibration.csv'))
    with paired.open() as source:
        pairs = list(csv.DictReader(source))
    with (candidates[0] / 'validation_metrics.csv').open() as source:
        metrics = list(csv.DictReader(source))
    assert len(metrics) == 6
    for row in metrics:
        group = [p for p in pairs if p['validation'] == row['validation'] and
                 (int(row['test_year']) == 0 or p['Year'] == row['test_year'])]
        assert len(group) == int(row['n'])
        assert len({p['PAC'] for p in group}) == int(row['counties'])
        actual = [math.log(float(p['observed_gdp'])) for p in group]
        for field, label in [('old', 'old'), ('updated', 'new')]:
            pred = [float(p[field]) for p in group]
            squared = sum((math.log(x) - y) ** 2 for x, y in zip(pred, actual))
            rmse = math.sqrt(squared / len(actual))
            variance = sum((y - statistics.mean(actual)) ** 2 for y in actual)
            ape = statistics.median(abs(x / float(p['observed_gdp']) - 1) for x, p in zip(pred, group))
            assert rmse == pytest.approx(float(row[label + '_log_rmse']), abs=1e-12)
            assert 1 - squared / variance == pytest.approx(float(row[label + '_log_r2']), abs=1e-10)
            assert ape == pytest.approx(float(row[label + '_median_ape']), abs=1e-12)


def test_workflow_resume_reuses_all_completed_stages(synthetic):
    _, run, candidates, _ = synthetic
    hashes = [digest(p / 'receipt.json') for p in candidates]
    output = powershell(ROOT / 'workflows/gridded_gdp/Invoke-GriddedGdp.ps1',
                        '-RunDirectory', run, '-Mode', 'synthetic', '-Append', '-Resume')
    assert 'COMPLETE ' not in output
    assert 'REUSED fit' in output and 'REUSED accepted_model' in output
    assert hashes == [digest(p / 'receipt.json') for p in candidates]
    assert not (run / '.lock').exists()


@pytest.mark.parametrize('fault,message', [
    ('wrong_year', 'year mismatch'), ('missing_province', 'Incomplete positive province'),
    ('duplicate_county', 'Duplicate administrative-year key'), ('strict_closure', 'readback exceeds tolerance'),
])
def test_invalid_inputs_or_acceptance_cannot_create_candidate(synthetic, fault, message):
    base, run, candidates, _ = synthetic
    cfg = json.loads((run / 'resolved-append.json').read_text())
    if fault == 'wrong_year':
        cfg['annual']['2023']['population']['year'] = 2022
    elif fault == 'missing_province':
        src = Path(cfg['data_root']) / cfg['inputs']['province_gdp']
        rows = list(csv.DictReader(src.open()))
        target = base / 'missing-province.csv'
        with target.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys()); writer.writeheader()
            writer.writerows(r for r in rows if not (r['Sgnyea'] == '2023' and r['Prvcnm_id'] == '120000'))
        cfg['inputs']['province_gdp'] = str(target)
    elif fault == 'duplicate_county':
        src = Path(cfg['data_root']) / cfg['inputs']['county_gdp']
        lines = src.read_text().splitlines()
        target = base / 'duplicate.csv'; target.write_text('\n'.join(lines + [lines[1]]) + '\n')
        cfg['inputs']['county_gdp'] = str(target)
    else:
        cfg['acceptance']['county_p95_rel'] = cfg['acceptance']['county_max_rel'] = 1e-20
    config = base / (fault + '.json'); config.write_text(json.dumps(cfg))
    before = sorted(p.name for p in candidates[0].parent.iterdir())
    output = call(['Rscript', '--vanilla', GDP / 'run_gdp.R', config, 'accept'], ok=False)
    assert message.lower() in output.lower()
    assert sorted(p.name for p in candidates[0].parent.iterdir()) == before


def test_modified_checkpoint_is_not_silently_reused(synthetic):
    _, run, _, _ = synthetic
    path = next((run / 'work/checkpoints/predictors-2023').glob('*/alignment.json'))
    original = path.read_bytes()
    try:
        path.write_bytes(original + b' ')
        output = call(['Rscript', '--vanilla', GDP / 'run_gdp.R', run / 'resolved-append.json', 'accept'], ok=False)
        assert 'Checkpoint checksum mismatch' in output
    finally:
        path.write_bytes(original)


def test_publish_overwrite_backup_readback_and_rollback(synthetic):
    _, run, candidates, _ = synthetic
    config = run / 'resolved-initial.json'
    cfg = json.loads(config.read_text())
    release = Path(cfg['release_root'])
    candidate = candidates[0]
    receipt = json.loads((candidate / 'receipt.json').read_text())
    payload = [p for p in receipt['file_hashes'] if '/' in p]
    release.mkdir()
    # One pre-existing file, other payloads absent: exercise both rollback paths.
    original = release / payload[0]; original.parent.mkdir(parents=True)
    original.write_bytes(b'synthetic prior release')
    old_sha = digest(original)
    other_config = run / 'wrong-release-geometry.json'
    wrong = dict(cfg, geo=dict(cfg['geo'], extent=[100, 100.4, 30, 30.3]))
    other_config.write_text(json.dumps(wrong))
    error = call(['Rscript', '--vanilla', GDP / 'publish_gdp.R', other_config, candidate, 'test', 'publish'],
                 ok=False)
    assert 'Candidate geometry or county boundary differs' in error
    assert digest(original) == old_sha
    call(['Rscript', '--vanilla', GDP / 'publish_gdp.R', config, candidate, 'test', 'plan'])
    assert digest(original) == old_sha
    call(['Rscript', '--vanilla', GDP / 'publish_gdp.R', config, candidate, 'test', 'publish'])
    for p in payload:
        assert digest(release / p) == receipt['file_hashes'][p]
    tx = release / '.gdp-releases/test'
    assert (tx / 'complete.json').exists()
    assert digest(tx / 'backup' / payload[0]) == old_sha
    call(['Rscript', '--vanilla', GDP / 'publish_gdp.R', config, candidate, 'test', 'rollback'])
    assert digest(original) == old_sha
    assert all(not (release / p).exists() for p in payload[1:])
    assert all((tx / 'rolled-back' / p).exists() for p in payload[1:])
    assert json.loads((tx / 'complete.json').read_text())['status'] == 'rolled_back'
    assert not (release / '.gdp-releases/lock').exists()


def test_hand_calculated_overlap_and_zero_population(tmp_path):
    output = call(['Rscript', '--vanilla', ROOT / 'harness/checks/gridded_gdp_cases.R', GDP, tmp_path])
    assert 'HAND-CALCULATED CASES PASS' in output


def test_existing_run_lock_is_preserved(synthetic):
    _, run, _, _ = synthetic
    lock = run / '.lock'
    lock.write_text('synthetic other controller')
    try:
        output = powershell(ROOT / 'workflows/gridded_gdp/Invoke-GriddedGdp.ps1',
                            '-RunDirectory', run, '-Mode', 'synthetic', '-Append', '-Resume', ok=False)
        assert 'Run locked' in output
        assert lock.read_text() == 'synthetic other controller'
    finally:
        lock.unlink()


def test_missing_population_blocks_acquisition_before_download(synthetic):
    base, run, _, _ = synthetic
    cfg = json.loads((run / 'fixture/initial.json').read_text())
    cfg['mode'] = 'authorized'
    cfg['annual']['2021']['population']['path'] = 'missing_population.tif'
    config = base / 'missing-annual.json'
    config.write_text(json.dumps(cfg))
    blocked = base / 'blocked-intake'
    output = powershell(ROOT / 'workflows/gridded_gdp/Invoke-GriddedGdp.ps1', '-RunDirectory', blocked,
                        '-Mode', 'authorized', '-Config', config, ok=False)
    assert 'Missing configured population input' in output
    assert not (blocked / 'acquired').exists()
    assert not (blocked / 'work').exists()
    assert json.loads((blocked / 'workflow.json').read_text())['status'] == 'incomplete'
