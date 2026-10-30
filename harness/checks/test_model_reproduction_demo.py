"""The documented synthetic task runs without real data or a personal login."""
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "skills/model/shared/model_reproduction/scripts"


def test_documented_synthetic_task(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    import compare_existing
    spec = importlib.util.spec_from_file_location("synthetic_reproduction_fixture", SCRIPTS / "make_synthetic_fixture.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    for name, folder in (("AIRMOSAIC_ASSETS_DIR", "assets"), ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")):
        root = tmp_path / folder
        root.mkdir()
        monkeypatch.setenv(name, str(root))
    assert fixture.create("synthetic_v1")["status"] == "preflight_passed"
    assert not (tmp_path / "assets/results").exists()
    assert fixture.create("synthetic_v1", execute=True)["status"] == "created"
    with pytest.raises(ValueError):
        fixture.create("synthetic_v1", execute=True)
    task = tmp_path / "config/task.json"
    task.write_text((REPO / "config/examples/model-reproduction/compare-existing.json").read_text(encoding="utf-8"), encoding="utf-8")
    preview = compare_existing.run(task, "demo_compare")
    assert preview["prediction_rows_read"] == 0
    outcome = compare_existing.run(task, "demo_compare", execute=True)
    assert outcome["paired_row_count"] == 5
    assert outcome["unmatched_row_count"] == 0
    assert outcome["reported_metric_assertions"] == "passed"
