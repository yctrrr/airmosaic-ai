"""Validate direct R tuning contracts and exercise the synthetic route when installed."""
from pathlib import Path
import json
import shutil
import subprocess

import pytest

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "skills/model/shared/machine_learning_model/frameworks/r/mlr3/examples/automatic-tuning.R"


def run_example(*args):
    rscript = shutil.which("Rscript")
    if not rscript:
        pytest.skip("Rscript unavailable")
    # --vanilla avoids personal startup files; no real inputs or output directories.
    return subprocess.run([rscript, "--vanilla", str(EXAMPLE), *args],
                          cwd=REPO, capture_output=True, text=True, timeout=180)


def receipt(result):
    records = [line for line in result.stdout.splitlines() if line.startswith('{"status"')]
    assert records, "No structured synthetic result"
    return json.loads(records[-1])


def test_contract_rejects_group_leakage_bad_ranges_and_excess_budget():
    result = run_example("--validate-only")
    assert result.returncode == 0, "R contract checks failed"
    assert receipt(result) == {"status": "passed", "scope": "base_r_contract_only",
                               "refusal_checks": 10, "automatic_tuning_executed": False}


def test_automatic_tuning_freezes_models_and_replays_without_test_access():
    result = run_example()
    observed = receipt(result)
    if result.returncode == 77:
        assert observed["status"] == "dependencies_unavailable"
        assert observed["automatic_tuning_executed"] is False
        pytest.skip("Selected R environment lacks automatic-tuning dependencies")
    assert result.returncode == 0, "Synthetic automatic tuning failed"
    assert observed["automatic_tuning_executed"] is True
    assert observed["models"] == 4
    assert observed["holdout_rows"] == 24
    assert observed["replay_and_serialization_checked"] is True
