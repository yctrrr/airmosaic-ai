"""Render documented native configurations into fresh external run directories.

Reads explicit settings and version-matched static tables; no model execution/network.
Changing a date, response or control prepares a new experiment, not new validation.
"""
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import shutil
import sys

from gc_paths import bounded_links, digest, sandbox_root, save_new, within

TEMPLATES = Path(__file__).resolve().parents[1] / 'templates'
STATIC = ('chemga.dat', 'diaginfo.dat', 'globchem.dat', 'jv_atms.dat',
          'jv_spec_aod.dat', 'jv_spec.dat', 'mglob.dat', 'ratj.d', 'RXN_ID',
          'STR_ID', 'tracerinfo.dat')


def date(value):
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')


def render(text, values):
    for k, v in values.items():
        text = text.replace('@' + k + '@', str(v))
    if re.search(r'@[A-Z_]+@', text):
        raise ValueError('unresolved_template_token')
    return text


def update(text, key, value):
    lines = text.splitlines()
    ids = [i for i, line in enumerate(lines) if ':' in line and line.rsplit(':', 1)[0].strip() == key]
    if len(ids) != 1:
        raise ValueError('ambiguous_native_key:' + key)
    i = ids[0]
    lines[i] = lines[i].rsplit(':', 1)[0] + ': ' + str(value)
    return '\n'.join(lines) + '\n'


def configure(root, source, run, settings, mode, execute=False):
    root = sandbox_root(root)
    source = within(root, source, must_exist=True)
    if mode not in ('classic', 'adjoint'):
        raise ValueError('unsupported_model_mode')
    run = within(root, run)
    if run.exists():
        raise ValueError('fresh_run_required')
    bounded_links(root, source)
    allowed = {'start_utc', 'end_utc', 'data_root'}
    allowed |= {'restart_file', 'control_tracer', 'response_tracer', 'fd_steps'} if mode == 'adjoint' else set()
    if set(settings) != allowed:
        raise ValueError('settings_keys_do_not_match_mode')
    start, end = date(settings['start_utc']), date(settings['end_utc'])
    if end <= start:
        raise ValueError('end_must_follow_start')
    data = within(root, settings['data_root'], must_exist=True)
    if not data.is_dir() or re.search(r'[\s\x00@]', str(data)):
        raise ValueError('native_data_path_must_be_directory_without_whitespace_or_tokens')
    values = {'DATA_ROOT': str(data), 'START_DATE': start.strftime('%Y%m%d'),
              'START_TIME': start.strftime('%H%M%S'), 'END_DATE': end.strftime('%Y%m%d'),
              'END_TIME': end.strftime('%H%M%S')}
    files, static, dirs = {}, [], []
    if mode == 'classic':
        if (end-start).total_seconds() % 3600 or start.minute or start.second or end.minute or end.second:
            raise ValueError('classic_template_requires_whole_hour_intervals')
        template = TEMPLATES / 'classic_14.8.0'
        for p in template.glob('*.in'):
            files[p.stem] = render(p.read_text(), values)
        shared = source / 'src/GEOS-Chem/run/shared'
        static = [(shared / n, n) for n in ('species_database.yml', 'download_data.py', 'download_data.yml')]
        dirs = ['Restarts', 'OutputDir']
    else:
        if (end-start).total_seconds() != 10800 or start.date() != end.date() or start.hour % 3 or start.minute or start.second:
            raise ValueError('v35l_component_requires_same_day_three_hour_I3_interval')
        restart = within(root, settings['restart_file'], must_exist=True)
        if not restart.is_file() or re.search(r'[\s\x00@]', str(restart)) or len(str(restart)) >= 255:
            raise ValueError('invalid_native_restart_path')
        values['RESTART_FILE'] = str(restart)
        steps = settings['fd_steps']
        if (not isinstance(steps, list) or len(steps) != 3 or
            any(isinstance(h, bool) or not isinstance(h, (int, float)) or not math.isfinite(h) or not 0 < h < 1 for h in steps) or
            len(set(steps)) != 3 or steps != sorted(steps, reverse=True)):
            raise ValueError('three_distinct_descending_positive_steps_below_one_required')
        template = TEMPLATES / 'adjoint_v35l'
        geos = render((template / 'input.geos.in').read_text(), values)
        geos = update(geos, 'Start YYYYMMDD, HHMMSS', start.strftime('%Y%m%d %H%M%S'))
        geos = update(geos, 'End   YYYYMMDD, HHMMSS', end.strftime('%Y%m%d %H%M%S'))
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        # The native fixed FORMAT always reads 29 columns for February.
        for month, length in zip(months, (31,29,31,30,31,30,31,31,30,31,30,31)):
            geos = update(geos, 'Schedule output for ' + month, ''.join('3' if months[end.month-1] == month and day == end.day else '0' for day in range(1, length + 1)))
        names = {int(i): name for i, name in re.findall(r'^Tracer #\d+\s*:\s*(\d+)\s+(\S+)', geos, re.M)}
        for k in ('control_tracer', 'response_tracer'):
            if type(settings[k]) is not int or settings[k] not in names:
                raise ValueError('tracer_index_must_match_native_43_tracer_table')
        control, response = settings['control_tracer'], settings['response_tracer']
        adj = render((template / 'input.gcadj.in').read_text(), values)
        adj = update(adj, '=> w/LICS: tracer     ICSFD', control)
        adj = update(adj, '=> tracer (STT #)     NFD', response)
        adj = update(adj, '=>  Forcing time till', start.strftime('%Y%m%d %H%M%S'))
        adj = adj.replace('Tracer #1                      : 1    NOx      1          1         0.5',
                          f'Tracer #1                      : {control}    {names[control]}      1          1         0.5')
        adj = adj.replace('Tracer #1                      : 2    Ox',
                          f'Tracer #1                      : {response}    {names[response]}')
        for h in steps:
            # repr preserves distinct float values; default 'g' rounds to six
            # significant digits and can silently merge two reviewed steps.
            name = 'step_' + repr(h).replace('.', 'p')
            files[name + '/input.geos'] = geos
            files[name + '/input.gcadj'] = update(adj, 'fd perturbation        FD_DIFF', h)
            files[name + '/ITER'] = '1\n3\n'
            dirs += [name + '/' + n for n in ('TMP', 'OptData', 'adjtmp', 'diagadj')]
        original = source / 'runs/v8-02-01/geos5'
        static = [(original / n, name + '/' + n) for name in sorted({p.split('/')[0] for p in files}) for n in STATIC]
    for src, _ in static:
        if not src.is_file():
            raise ValueError('version_matched_static_input_missing:' + src.name)
    result = {'mode': 'plan_only', 'model': mode, 'settings': settings,
              'native_configuration_files': sorted(files), 'model_executed': False,
              'input_contents_validated': False, 'scientific_acceptance': False}
    if not execute:
        return result
    run.mkdir(parents=True)
    for n in dirs:
        (run / n).mkdir(parents=True, exist_ok=True)
    for n, text in files.items():
        p = run / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8', newline='\n')
    for src, n in static:
        shutil.copyfile(src, run / n)
    result.update(mode='prepared', files=[{'path':p.relative_to(run).as_posix(), 'sha256':digest(p)} for p in run.rglob('*') if p.is_file()])
    save_new(run / 'configuration-receipt.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('root', 'source', 'run', 'settings'):
        p.add_argument('--' + n, required=True)
    p.add_argument('--mode', choices=['classic', 'adjoint'], required=True)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    try:
        settings = json.loads(Path(a.settings).read_text())
        print(json.dumps(configure(a.root, a.source, a.run, settings, a.mode, a.execute)))
        return 0
    except Exception as exc:
        print(json.dumps({'status':'failed', 'error_type':type(exc).__name__, 'error':str(exc)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
