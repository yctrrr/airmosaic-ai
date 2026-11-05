"""Small explicit path/provenance helpers for trusted GEOS-Chem operations."""
import hashlib
import json
import os
from pathlib import Path


def digest(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):value.update(chunk)
    return value.hexdigest()


def sandbox_root(value):
    root=Path(value).expanduser().resolve()
    if not root.is_dir():raise ValueError('existing_sandbox_root_required')
    if any((p/'.git').exists() for p in (root,)+tuple(root.parents)):
        raise ValueError('model_work_must_be_outside_git')
    return root


def within(root,value,*,must_exist=False):
    path=Path(value).expanduser()
    if not path.is_absolute():path=root/path
    resolved=path.resolve()
    try:inside=os.path.commonpath([str(root),str(resolved)])==str(root)
    except ValueError:inside=False
    if not inside or resolved==root:raise ValueError('sandbox_path_escape_or_root_target')
    if must_exist and not resolved.exists():raise ValueError('required_sandbox_path_missing')
    return resolved


def save_new(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)


def bounded_links(root,tree):
    """Validate internal links before invoking trusted build/model programs."""
    for path in Path(tree).rglob('*'):
        if path.is_symlink():within(root,path,must_exist=True)


def save_state(path,value):
    path=Path(path);temporary=path.with_name(path.name+'.tmp')
    with temporary.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2,allow_nan=False)
    os.replace(str(temporary),str(path))
