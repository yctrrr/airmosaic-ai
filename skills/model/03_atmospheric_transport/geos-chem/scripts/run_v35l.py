"""Run the reviewed three-step v35l native test serially, with bounded fresh outputs.

The caller supplies a compatible compute allocation and reviewed physical inputs.
Plan by default. No SSH, scheduler submission, downloads or installation.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from gc_paths import bounded_links, digest, sandbox_root, save_new, save_state, within


def run_cases(root, binary, prepared, output, execute=False, case_seconds=1800, total_seconds=10800):
    root = sandbox_root(root)
    binary = within(root, binary, must_exist=True)
    prepared = within(root, prepared, must_exist=True)
    output = within(root, output)
    if output.exists():
        raise ValueError('fresh_output_directory_required')
    if not 1 <= case_seconds <= 1800 or not 1 <= total_seconds <= 10800:
        raise ValueError('model_time_budget')
    bounded_links(root, prepared)
    receipt = json.loads((prepared / 'configuration-receipt.json').read_text())
    if receipt['model'] != 'adjoint' or receipt['mode'] != 'prepared':
        raise ValueError('prepared_adjoint_configuration_required')
    for item in receipt['files']:
        if digest(within(root, prepared / item['path'], must_exist=True)) != item['sha256']:
            raise ValueError('prepared_input_changed')
    expected = ['step_' + repr(h).replace('.', 'p') for h in receipt['settings']['fd_steps']]
    if len(set(expected)) != 3 or {p.name for p in prepared.glob('step_*')} != set(expected):
        raise ValueError('three_prepared_steps_required')
    plan = {'mode':'plan_only', 'cases':9, 'threads':4, 'case_seconds':case_seconds,
            'total_seconds':total_seconds, 'binary_sha256':digest(binary), 'scientific_acceptance':False}
    if not execute:
        return plan
    import resource
    if os.environ.get('OMP_NUM_THREADS') != '4' or any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')):
        raise ValueError('explicit_four_thread_environment_required')
    if os.environ.get('SLURM_CPUS_PER_TASK', '4') != '4':
        raise ValueError('allocation_mismatch')
    if resource.getrlimit(resource.RLIMIT_STACK)[0] != resource.RLIM_INFINITY:
        raise ValueError('set_main_stack_unlimited_before_start')
    output.mkdir(parents=True)
    state = dict(plan, mode='running', completed=[], started_epoch=time.time(), model_seconds_used=0)
    status = output / 'run-status.json'
    save_new(status, state)
    start = time.monotonic()
    try:
        for step in expected:
            seed = prepared / step
            previous = seed
            for iteration in (1,2,3):
                case = output / seed.name / ('iteration_' + str(iteration))
                # Reserve space for the next trajectory as well as its copied predecessor.
                logical = sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())
                copy_bytes = sum(p.stat().st_size for p in previous.rglob('*') if p.is_file() and not p.is_symlink())
                if logical + copy_bytes + 1073741824 >= 10737418240:
                    raise ValueError('ten_gib_sandbox_budget')
                shutil.copytree(previous, case)
                # Only remove inherited products in this newly copied case. Inputs
                # and trajectory checkpoints remain intact for the native protocol.
                for product in case.glob('restart.output.component.*'):
                    product.unlink()
                current_cost = case / 'OptData' / f'cfn.{iteration:02d}'
                if current_cost.exists():
                    current_cost.unlink()
                (case / 'ITER').write_text(f'{iteration}\n3\n')
                state['active_case'] = {'step':seed.name,'iteration':iteration}
                save_state(status, state)
                remaining = total_seconds - (time.monotonic()-start)
                if remaining <= 0:
                    raise ValueError('total_model_time_budget_exhausted')
                started = time.monotonic()
                with (case/'model.log').open('wb') as log:
                    result = subprocess.run([str(binary)], cwd=case, stdout=log, stderr=subprocess.STDOUT,
                                            timeout=min(case_seconds,remaining), check=False)
                text = (case/'model.log').read_text(errors='replace')
                good = (result.returncode == 0 and 'F I N I S H   I T E R A T I O N' in text and
                        (case/'OptData'/f'cfn.{iteration:02d}').is_file() and
                        any(p.stat().st_size > 0 for p in case.glob('restart.output.component.*')))
                state['completed'].append({'step':seed.name,'iteration':iteration,'exit':result.returncode,
                                           'operational_gates_passed':good,'seconds':time.monotonic()-started})
                state['model_seconds_used'] = time.monotonic()-start
                save_state(status, state)
                if not good:
                    raise ValueError('native_invocation_failed_preserved')
                previous = case
        state['mode'] = 'native_cases_complete'
        state['active_case'] = None
    except Exception as exc:
        state.update(mode='stopped_preserved', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        state['model_seconds_used'] = time.monotonic()-start
        save_state(status, state)
    return state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('root','binary','prepared','output'):
        p.add_argument('--'+n, required=True)
    p.add_argument('--case-seconds', type=int, default=1800)
    p.add_argument('--total-seconds', type=int, default=10800)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    try:
        print(json.dumps(run_cases(a.root,a.binary,a.prepared,a.output,a.execute,a.case_seconds,a.total_seconds)))
    except Exception as exc:
        print(json.dumps({'status':'failed','error_type':type(exc).__name__,'error':str(exc)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
