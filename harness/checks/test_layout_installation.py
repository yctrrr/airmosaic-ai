"""Installed checkout discovery must not depend on the caller's directory."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from airmosaic.services import DataCatalogService, ToolRegistryService


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('location', ['repository', 'package', 'external'])
def test_installed_cli_resolves_checkout_from_any_directory(tmp_path, location):
    directory = {'repository': ROOT, 'package': ROOT / 'airmosaic', 'external': tmp_path}[location]
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('AIRMOSAIC_', 'GCAM_', 'PM25_HIA_'))}
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    expected = {item['tool_id'] for item in ToolRegistryService(ROOT).list_tools()}
    result = subprocess.run(
        [sys.executable, '-I', '-B', '-X', 'utf8', '-m', 'airmosaic.cli',
         'list-tools', '--format', 'json'],
        cwd=directory, env=env, capture_output=True, text=True,
        encoding='utf-8', timeout=30,
    )
    assert result.returncode == 0
    tools = json.loads(result.stdout)
    assert {item['tool_id'] for item in tools} == expected
    core_paths = {item['entrypoint']['path'] for item in tools if item['category'] == 'core'}
    assert core_paths == {'airmosaic/cli.py'}

    result = subprocess.run(
        [sys.executable, '-I', '-B', '-X', 'utf8', '-m', 'airmosaic.cli',
         'describe-dataset', 'population'],
        cwd=directory, env=env, capture_output=True, text=True,
        encoding='utf-8', timeout=30,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)['dataset_id'] == DataCatalogService().resolve_dataset_id('population')
