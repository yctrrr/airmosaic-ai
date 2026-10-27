import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
EXAMPLE = Path(__file__).resolve().parents[2] / "config/examples/environment.ps1"
pytestmark = pytest.mark.skipif(POWERSHELL is None, reason="PowerShell is unavailable")


def run_example(local_root):
    environment = os.environ.copy()
    environment["AIRMOSAIC_TEST_EXAMPLE"] = str(EXAMPLE)
    environment["AIRMOSAIC_TEST_ROOT"] = str(local_root)
    return subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "$ErrorActionPreference = 'Stop'; "
            ". $env:AIRMOSAIC_TEST_EXAMPLE -LocalRoot $env:AIRMOSAIC_TEST_ROOT; "
            "@{workspace=$env:AIRMOSAIC_ASSETS_DIR; "
            "config=$env:AIRMOSAIC_CONFIG_DIR; auth=$env:AIRMOSAIC_AUTH_DIR} "
            "| ConvertTo-Json -Compress",
        ],
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_environment_example_sets_separate_roots_without_writing(tmp_path):
    local_root = tmp_path / "local root with spaces"
    local_root.mkdir()
    marker = local_root / "existing-config.txt"
    marker.write_text("preserve", encoding="utf-8")

    result = run_example(local_root)

    assert result.returncode == 0
    settings = json.loads(result.stdout)
    assert {name: Path(value) for name, value in settings.items()} == {
        "workspace": local_root / "assets",
        "config": local_root / "config",
        "auth": local_root / "auth",
    }
    assert list(local_root.iterdir()) == [marker]
    assert marker.read_text(encoding="utf-8") == "preserve"


@pytest.mark.parametrize("git_marker_is_file", [False, True])
def test_environment_example_rejects_roots_inside_git(tmp_path, git_marker_is_file):
    checkout = tmp_path / "checkout"
    nested = checkout / "nested"
    nested.mkdir(parents=True)
    marker = checkout / ".git"
    if git_marker_is_file:
        marker.write_text("gitdir: elsewhere", encoding="utf-8")
    else:
        marker.mkdir()

    result = run_example(nested)

    assert result.returncode != 0
    assert "LocalRoot must be outside Git checkouts" in result.stderr
    assert list(nested.iterdir()) == []
