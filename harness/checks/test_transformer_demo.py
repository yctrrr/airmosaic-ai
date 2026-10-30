"""Synthetic software cases and path/privacy checks; never inspect research inputs."""
import csv
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "skills/model/shared/machine_learning_model/scripts/python/run_transformer_demo.py"
CONFIG = ROOT / "config/examples/machine-learning-model/python/transformer.synthetic.json"
spec = importlib.util.spec_from_file_location("synthetic_transformer_entry", ENTRY)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    for name, leaf in [("AIRMOSAIC_ASSETS_DIR", "assets"), ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")]:
        path = tmp_path / leaf
        path.mkdir()
        monkeypatch.setenv(name, str(path))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config.update(samples={"train": 16, "val": 8, "test": 8}, epochs=1, d_model=8, batch_size=8)
    path = tmp_path / "config/task.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    output = tmp_path / "assets/results/synthetic_demo/fresh"
    return config, path, output


@pytest.mark.parametrize("change", [
    {"input_csv": "unaccepted.csv"}, {"purpose": "new_study"},
    {"seed": True}, {"samples": {"train": 2, "val": 8, "test": 8}},
    {"d_model": 9, "heads": 2}, {"epochs": 1000}, {"learning_rate": float("nan")},
])
def test_rejects_arbitrary_data_and_unbounded_settings(setup, change):
    config, _, _ = setup
    with pytest.raises(demo.DemoError):
        demo.validate_configuration({**config, **change})


def test_preview_does_not_import_torch_or_create_outputs(setup, monkeypatch, capsys):
    import builtins
    _, config, output = setup
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name == "torch" or name.startswith("torch."):
            pytest.fail("Preview imported the training runtime")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded)
    assert demo.main(["--case", "fusion", "--config-file", str(config), "--out-dir", str(output), "--dry-run"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["output_created"] is False
    assert not output.exists() and not output.parent.exists()


def test_private_configuration_is_refused_without_reading(setup, monkeypatch):
    _, _, output = setup
    private = Path(os.environ["AIRMOSAIC_AUTH_DIR"]) / "private.json"
    private.write_text("synthetic secret marker", encoding="utf-8")
    original = Path.read_text
    def guarded(path, *args, **kwargs):
        if path == private:
            pytest.fail("Authentication contents were read")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", guarded)
    with pytest.raises(demo.DemoError, match="demo_configuration_root"):
        demo.prepare(str(private), str(output), "fusion")


@pytest.mark.parametrize("kind", ["auth", "data", "git", "overlap", "exists"])
def test_storage_boundaries_and_no_overwrite(setup, monkeypatch, kind):
    _, config, output = setup
    if kind == "auth":
        output = Path(os.environ["AIRMOSAIC_AUTH_DIR"]) / "results/task/fresh"
    elif kind == "data":
        output = Path(os.environ["AIRMOSAIC_ASSETS_DIR"]) / "data/task/fresh"
    elif kind == "git":
        output.parent.mkdir(parents=True)
        (output.parent / ".git").mkdir()
    elif kind == "overlap":
        monkeypatch.setenv("AIRMOSAIC_AUTH_DIR", os.environ["AIRMOSAIC_CONFIG_DIR"])
    else:
        output.mkdir(parents=True)
        (output / "preserve.txt").write_text("original", encoding="utf-8")
    with pytest.raises(demo.DemoError):
        demo.prepare(str(config), str(output), "fusion")
    if kind == "exists":
        assert (output / "preserve.txt").read_text(encoding="utf-8") == "original"


@pytest.mark.parametrize("case", demo.CASES)
def test_actual_cpu_cases_metrics_reload_and_safe_artifacts(setup, case):
    torch = pytest.importorskip("torch")
    config, path, output = setup
    validated, checked_output = demo.prepare(str(path), str(output), case)
    assert demo.execute(validated, checked_output, case)["status"] == "succeeded"
    rows = list(csv.DictReader((output / "predictions.csv").open(encoding="utf-8")))
    assert len(rows) == len({r["sample_id"] for r in rows}) == config["samples"]["test"]
    errors = [float(r["observed"]) - float(r["predicted"]) for r in rows]
    scores = json.loads((output / "metrics.json").read_text())
    assert math.isclose(scores["network"]["rmse"], math.sqrt(sum(e*e for e in errors)/len(errors)))
    assert math.isclose(scores["network"]["mae"], sum(abs(e) for e in errors)/len(errors))
    checkpoint = torch.load(output / "checkpoint.pt", map_location="cpu", weights_only=True)
    train, labels = demo.synthetic_split(config, "train", case)
    for name, values in train.items():
        assert torch.equal(checkpoint["preprocessing"][name]["mean"], values.mean(0))
    checks = json.loads((output / "checks.json").read_text())
    assert checks["reload_equal"] and checks["independent_metrics"] and checks["nonzero_finite_gradients"]
    events = [json.loads(line)["event"] for line in (output / "events.jsonl").read_text().splitlines()]
    assert events.index("checkpoint_selected") < events.index("test_evaluated")
    assert checks["scientific_acceptance"] is False
    manifest = json.loads((output / "artifacts.json").read_text())
    assert all(not Path(entry["path"]).is_absolute() for entry in manifest["files"].values())
    assert str(output) not in (output / "status.json").read_text()


def test_heldout_targets_do_not_change_fitting_or_selection(setup, monkeypatch):
    torch = pytest.importorskip("torch")
    config, _, output = setup
    original = demo.synthetic_split
    selected_output, shift = None, 0
    def changed(config, split, case):
        if split == "test":
            assert (selected_output / "checkpoint.pt").is_file()
        inputs, target = original(config, split, case)
        return inputs, target + shift if split == "test" else target
    monkeypatch.setattr(demo, "synthetic_split", changed)
    states, reports = [], []
    for name, shift in [("first", 0), ("second", 100)]:
        selected_output = output.parent / name
        demo.execute(config, selected_output, "fusion")
        states.append(torch.load(selected_output / "checkpoint.pt", weights_only=True, map_location="cpu")["model"])
        reports.append(json.loads((selected_output / "metrics.json").read_text()))
    assert all(torch.equal(states[0][key], states[1][key]) for key in states[0])
    assert reports[0]["best_epoch"] == reports[1]["best_epoch"]
    assert reports[0]["validation_mse"] == reports[1]["validation_mse"]
    assert reports[1]["network"]["rmse"] > reports[0]["network"]["rmse"] + 50


def test_cli_rejects_unknown_arguments_without_values(setup):
    private_marker = "synthetic_private_argument"
    result = subprocess.run([sys.executable, str(ENTRY), "--checkpoint", private_marker], capture_output=True, text=True)
    assert result.returncode == 2
    assert private_marker not in result.stdout + result.stderr


@pytest.mark.parametrize("root_name", ["AIRMOSAIC_AUTH_DIR", "AIRMOSAIC_CONFIG_DIR"])
def test_python_entry_cannot_bypass_output_boundaries(setup, root_name):
    config, _, _ = setup
    outside = Path(os.environ[root_name]) / "results/task/fresh"
    with pytest.raises(demo.DemoError, match="demo_output_outside_results"):
        demo.execute(config, outside, "fusion")
    assert not outside.exists()


def test_python_entry_cannot_bypass_budget_validation(setup):
    config, _, output = setup
    with pytest.raises(demo.DemoError, match="demo_budget_exceeded"):
        demo.execute({**config, "epochs": 1000}, output, "fusion")
    assert not output.exists()


def test_fusion_has_gradient_paths_from_each_source(setup):
    torch = pytest.importorskip("torch")
    from models.transformer_demo import SyntheticTransformer
    config, _, _ = setup
    torch.manual_seed(config["seed"])
    model = SyntheticTransformer("fusion", config)
    inputs, _ = demo.synthetic_split(config, "train", "fusion")
    model(inputs).sum().backward()
    for branch in ("static", "history", "grid"):
        gradient = model.projections[branch].weight.grad
        assert gradient is not None and torch.isfinite(gradient).all() and float(gradient.abs().sum()) > 0
    broken = dict(inputs)
    broken["grid"] = inputs["grid"].clone()
    broken["grid"][0, 0, 0, 0] = float("nan")
    with pytest.raises(ValueError, match="invalid_demo_tensor"):
        model(broken)
