"""Prepare a version-selected adjoint chemistry-component source in a fresh directory.

Plan by default; --execute applies the reviewed patch to a copy, never upstream.
This does not compile, download inputs, submit jobs or validate the science.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys

from gc_paths import bounded_links, digest, sandbox_root, save_new, within

RESOURCES = Path(__file__).resolve().parents[1] / 'templates/adjoint_v35l'


def normalized_hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def profile_members(code, manifest):
    records=[]
    for entry in manifest['changed_files']:
        rel = Path(entry['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('invalid_profile_member')
        target = code / rel
        if not target.is_file() or target.is_symlink():
            raise ValueError('profile_source_member_missing:' + entry['path'])
        records.append({'path':entry['path'],'sha256':normalized_hash(target)})
    return records


def prepare(root, source, output, execute=False, model_version='v35l'):
    root = sandbox_root(root)
    source = within(root, source, must_exist=True)
    output = within(root, output)
    if output.exists():
        raise ValueError('fresh_profile_directory_required')
    bounded_links(root, source)
    if not isinstance(model_version,str) or not re.fullmatch(r'v\d+[a-z]?',model_version):
        raise ValueError('adjoint_model_version_number_required')
    manifest = json.loads((RESOURCES / 'profile-manifest.json').read_text())
    patch = RESOURCES / 'chemistry-component.patch'
    deps = RESOURCES / 'module-dependencies.mk'
    if digest(patch) != manifest['patch_sha256'] or digest(deps) != manifest['dependencies_sha256']:
        raise ValueError('profile_resource_hash_mismatch')
    before=profile_members(source / 'code', manifest)
    from build_classic import source_identity
    result = {'mode': 'plan_only', 'model_version': model_version,'source_identity':source_identity(source),
              'profile': manifest['profile'], 'changed_files': len(manifest['changed_files']),
              'patch_applicability':'checked_on_fresh_copy_at_execution',
              'model_executed': False, 'scientific_acceptance': False}
    if not execute:
        return result
    if (source/'.git').exists():
        from build_classic import verify_checkout
        verify_checkout(root, source)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / 'code', output)
    for entry in manifest['changed_files']:
        p = output / entry['path']
        p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n'))
    subprocess.run(['git', '-C', str(output), 'apply', '--check', str(patch)], check=True, timeout=30)
    subprocess.run(['git', '-C', str(output), 'apply', str(patch)], check=True, timeout=30)
    after=profile_members(output, manifest)
    shutil.copyfile(deps, output / 'airmosaic_module_dependencies.mk')
    reference_match=all(b['sha256']==entry['before_sha256'] and c['sha256']==entry['after_sha256']
                        for b,c,entry in zip(before,after,manifest['changed_files']))
    result.update(mode='prepared',patch_applicability='passed',source_files_before=before,source_files_after=after,
                  reference_model_version=manifest['model_version'],reference_file_hashes_match=reference_match,
                  patch_sha256=digest(patch), dependencies_sha256=digest(deps))
    save_new(output / 'profile-receipt.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'source', 'output'):
        p.add_argument('--' + name, required=True)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--version', default='v35l',help='Selected model version; bundled patch was tested with v35l')
    a = p.parse_args()
    try:
        print(json.dumps(prepare(a.root, a.source, a.output, a.execute,a.version)))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__, 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
