"""Independently compare native v35l FD_GLOB states with the baseline adjoint.

Accepts a native run tree or exported cell CSV. This is a numerical check;
terminal process status, restart validation and scientific review are separate.
"""
import argparse
import array
import csv
import json
import math
from pathlib import Path
import struct
import sys

from gc_paths import sandbox_root, within, save_new


def blocks(path):
    with Path(path).open('rb') as f:
        def record():
            raw = f.read(4)
            if not raw:
                return None
            if len(raw) != 4:
                raise ValueError('truncated_bpch_record')
            n = struct.unpack('>i', raw)[0]
            if not 0 <= n <= 100000000:
                raise ValueError('invalid_bpch_record_size')
            data = f.read(n)
            if len(data) != n or f.read(4) != raw:
                raise ValueError('truncated_or_mismatched_bpch_record')
            return data
        if record().strip() != b'CTM bin 02' or len(record()) != 80:
            raise ValueError('unsupported_bpch_format')
        result = []
        while True:
            a = record()
            if a is None:
                return result
            model, dx, dy, hp, c180 = struct.unpack('>20s2f2i', a)
            h = struct.unpack('>40si40s2d40s7i', record())
            data = record()
            if min(h[6:9]) <= 0 or len(data) != 4 * math.prod(h[6:9]) or h[-1] != len(data) + 8:
                raise ValueError('bpch_shape_mismatch')
            values = array.array('f', data)
            if sys.byteorder == 'little':
                values.byteswap()
            if not all(math.isfinite(x) for x in values):
                raise ValueError('nonfinite_bpch_values')
            result.append({'category':h[0].decode().strip(), 'tracer':h[1],
                           'units':h[2].decode().strip(), 'shape':list(h[6:9]),
                           'tau':[h[3],h[4]], 'dx':dx, 'dy':dy,
                           'values':values})


def native_rows(tree, control=1):
    rows = []
    for step in sorted(Path(tree).glob('step_*')):
        h = float(step.name[5:].replace('p', '.'))
        case = step / 'iteration_3'
        states = []
        for i in (1, 2, 3):
            files = list((case / 'diagadj').glob('gctm.fd.*.' + str(i).zfill(2)))
            if len(files) != 1:
                raise ValueError('missing_or_ambiguous_native_forward_state')
            b = blocks(files[0])
            if len(b) != 1 or b[0]['category'] != 'IJ-CHK-$' or b[0]['units'] != 'kg/box':
                raise ValueError('native_forward_state_contract')
            states.append(b[0])
        gradients = [b for b in blocks(case / 'OptData/gctm.gdt.01') if b['tracer'] == control and b['category'] == 'IJ-GDT-$']
        if len(gradients) != 1:
            raise ValueError('missing_or_ambiguous_baseline_gradient')
        g = gradients[0]
        if any(b['shape'] != [72,46,47] or b['dx'] != 5 or b['dy'] != 4 for b in states + [g]):
            raise ValueError('unsupported_native_grid')
        if any(b['tau'] != states[0]['tau'] for b in states):
            raise ValueError('forward_state_times_differ')
        for k in range(72 * 46):
            rows.append({'step':h, 'i':k % 72 + 1, 'j':k // 72 + 1,
                         'base_Ox_kg':states[0]['values'][k],
                         'plus_Ox_kg':states[1]['values'][k],
                         'minus_Ox_kg':states[2]['values'][k], 'adjoint':g['values'][k]})
    return rows


def compare(rows, rtol=0.05):
    if not math.isfinite(rtol) or not 0 < rtol < 1:
        raise ValueError('invalid_relative_tolerance')
    groups = {}
    for row in rows:
        h, base, plus, minus, g = (float(row[k]) for k in ('step','base_Ox_kg','plus_Ox_kg','minus_Ox_kg','adjoint'))
        if not 0 < h < 1 or not all(math.isfinite(v) for v in (h, base, plus, minus, g)):
            raise ValueError('invalid_gradient_row')
        key = (int(row['i']), int(row['j']))
        group = groups.setdefault(h, {})
        if min(key) < 1 or key in group:
            raise ValueError('invalid_or_duplicate_cell')
        group[key] = ((plus-minus)/(2*h), g)
    if len(groups) != 3:
        raise ValueError('three_predeclared_steps_required')
    cells = [set(g) for g in groups.values()]
    if any(s != cells[0] for s in cells[1:]):
        raise ValueError('cell_support_differs_between_steps')
    results = []
    for h, pairs in sorted(groups.items(), reverse=True):
        fdnorm = math.sqrt(math.fsum(f*f for f,g in pairs.values()))
        gnorm = math.sqrt(math.fsum(g*g for f,g in pairs.values()))
        error = math.sqrt(math.fsum((g-f)**2 for f,g in pairs.values()))
        nonzero = fdnorm > 0 and gnorm > 0
        relative = error / fdnorm if fdnorm else None
        results.append({'step':h, 'cells':len(pairs), 'finite_difference_l2':fdnorm,
                        'adjoint_l2':gnorm, 'relative_l2_error':relative,
                        'passed':nonzero and relative <= rtol,
                        'local_exceptions':sum(abs(f)>1 and abs(g-f)/abs(f)>rtol for f,g in pairs.values())})
    passed = any(a['passed'] and b['passed'] for a,b in zip(results, results[1:]))
    return {'comparison':'v35l_native_global_centered_difference_vs_baseline_adjoint',
            'rtol':rtol, 'criterion':'two_neighboring_steps', 'cases':results,
            'numerical_check_passed':passed, 'scientific_acceptance':False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    inputs = p.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--runs'); inputs.add_argument('--csv')
    p.add_argument('--control-tracer', type=int, default=1)
    p.add_argument('--rtol', type=float, required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    try:
        root = sandbox_root(a.root)
        if a.runs:
            rows = native_rows(within(root, a.runs, must_exist=True), a.control_tracer)
        else:
            with within(root, a.csv, must_exist=True).open(newline='') as f:
                rows = list(csv.DictReader(f))
        result = compare(rows, a.rtol)
        save_new(within(root, a.output), result)
        print(json.dumps(result))
        return 0 if result['numerical_check_passed'] else 2
    except Exception as exc:
        print(json.dumps({'status':'failed', 'error_type':type(exc).__name__, 'error':str(exc)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
