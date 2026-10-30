"""Configuration, data leakage, deterministic artifacts and local path boundaries."""

from copy import deepcopy
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from runtime.services import ToolRunnerService, ToolExecutionError
from runtime.services import mlr3_workflow, tool_runner


REPO = Path(__file__).resolve().parents[2]
TOOL = "ml_regression_workflow"
STAGE = "03_atmospheric_transport"


def configuration():
    return {"schema_version": 1, "task_type": "regression", "target": "y", "target_unit": "example_unit",
            "features": ["x", "category"], "id_column": "id",
            "split": {"column": "split", "train": "train", "val": "val", "test": "test"},
            "categorical_features": ["category"],
            "missing": {"policy": "train_median_mode", "sentinels": [-999]},
            "models": [{"id": "tree", "learner": "regr.rpart", "parameters": {"maxdepth": 3}},
                       {"id": "forest", "learner": "regr.ranger", "parameters": {"num.trees": 12}}],
            "selection_metric": "rmse", "seed": 401,
            "row_limits": {"train": 60, "val": 20, "test": 20},
            "explanation": {"features": ["x", "category"], "background_rows": 12,
                            "validation_rows": 12, "permutation_repeats": 2, "pdp_points": 4}}


@pytest.fixture
def task(tmp_path, monkeypatch):
    roots = {}
    for name, folder in (("AIRMOSAIC_ASSETS_DIR", "assets"), ("AIRMOSAIC_CONFIG_DIR", "settings"),
                         ("AIRMOSAIC_AUTH_DIR", "auth")):
        root = tmp_path / folder
        root.mkdir()
        monkeypatch.setenv(name, str(root))
        roots[name] = root
    source = roots["AIRMOSAIC_ASSETS_DIR"] / "data" / "sample.csv"
    source.parent.mkdir()
    rows = []
    for split, n in (("train", 60), ("val", 20), ("test", 20)):
        for i in range(n):
            rows.append({"id": f"{split}_{i:03}", "split": split,
                         "x": -999 if i == 3 else i / 5,
                         "category": "A" if i % 2 else "B", "y": 2 * i / 5 + (i % 2)})
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    cfg = roots["AIRMOSAIC_CONFIG_DIR"] / "task.json"
    cfg.write_text(json.dumps(configuration()), encoding="utf-8")
    return roots, source, cfg


def require_r_packages():
    executable = shutil.which("Rscript")
    if executable is None:
        pytest.skip("Rscript is unavailable")
    env = {**os.environ}
    library = os.environ.get("AIRMOSAIC_R_LIBRARY", "")
    for key in ("R_LIBS", "R_LIBS_USER", "R_LIBS_SITE"):
        env[key] = library or str(REPO / ".missing-test-r-library")
    result = subprocess.run([executable, "--vanilla", "-e",
                             'quit(status=if(all(vapply(c("mlr3","mlr3learners","ranger","rpart","jsonlite"), requireNamespace, logical(1), quietly=TRUE))) 0L else 1L)'],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    if result.returncode:
        pytest.skip("Required packages not available in the explicit R library")


def execute_task(task, parameters=None):
    roots, source, cfg = task
    record = ToolRunnerService().run(TOOL, parameters or {"task_config": str(cfg), "input_csv": str(source)},
                                     project_id="synthetic_regression", stage=STAGE, timeout=120)
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_regression" / record["run_id"]
    return record, output


@pytest.mark.parametrize("change", [
    lambda c: c.update(task_type="classification"),
    lambda c: c["features"].append("y"),
    lambda c: c["features"].append("split"),
    lambda c: c["features"].append("x"),
    lambda c: c["split"].update(test="val"),
    lambda c: c["models"][0].update(learner="system"),
    lambda c: c["models"][0]["parameters"].update(cp="synthetic-secret"),
    lambda c: c["models"][0].update(id="baseline"),
    lambda c: c["models"][1]["parameters"].update(mtry=3),
    lambda c: c["models"][1]["parameters"].update(num_threads=64),
    lambda c: c.update(execute="synthetic-secret"),
])
def test_task_contract_rejects_unsupported_settings_without_values(change):
    cfg = configuration()
    change(cfg)
    with pytest.raises(ToolExecutionError, match="^invalid_workflow_configuration$"):
        mlr3_workflow.validate_configuration(cfg, REPO)


def test_preview_does_not_read_csv_or_spawn_and_keeps_receipt_private(task, monkeypatch):
    roots, source, cfg = task
    original = Path.open
    def guarded(path, *args, **kwargs):
        if path == source:
            pytest.fail("preview read data contents")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("preview started a process"))
    record = ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(cfg)},
                                     dry_run=True, project_id="synthetic_regression", stage=STAGE)
    assert record["can_execute"]
    assert record["r_dependencies"]["status"] == "unverified"
    assert str(source) not in json.dumps(record) and str(cfg) not in json.dumps(record)
    assert not (roots["AIRMOSAIC_ASSETS_DIR"] / "results").exists()


def test_config_and_dependency_library_cannot_use_auth_or_git(task, monkeypatch):
    roots, source, cfg = task
    bad = roots["AIRMOSAIC_AUTH_DIR"] / "settings.json"
    bad.write_text('{"synthetic_secret":"do-not-open"}', encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="parameter_file_outside_allowed_roots"):
        ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(bad)},
                                dry_run=True, project_id="synthetic_regression", stage=STAGE)
    for library in (roots["AIRMOSAIC_AUTH_DIR"], roots["AIRMOSAIC_CONFIG_DIR"], source.parent, REPO):
        monkeypatch.setenv("AIRMOSAIC_R_LIBRARY", str(library))
        with pytest.raises(ToolExecutionError, match="invalid_r_dependency_library"):
            ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(cfg)},
                                    dry_run=True, project_id="synthetic_regression", stage=STAGE)


def test_synthetic_pipeline_is_deterministic_train_only_and_reloadable(task):
    require_r_packages()
    _, source, _ = task
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    first, a = execute_task(task)
    assert first["status"] == "succeeded", first
    assert json.loads((a / "status.json").read_text())["capability_id"] == "ml_regression"
    provenance = json.loads((a / "provenance.json").read_text())
    assert provenance["capability_id"] == "ml_regression"
    assert "catalog/schemas/ml-regression-task.schema.json" in provenance["source_sha256"]
    second, b = execute_task(task)
    assert second["status"] == "succeeded", second
    for name in ("candidates.csv", "predictions.csv", "permutation-importance.csv", "pdp.csv"):
        assert (a / name).read_bytes() == (b / name).read_bytes()
    prep = json.loads((a / "preprocessing.json").read_text())
    expected = sorted(i / 5 for i in range(60) if i != 3)[29]
    assert prep["preprocessing"]["numeric_fill"]["x"] == pytest.approx(expected)
    assert (a / "importance.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert mlr3_workflow.validate_outputs(a)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row["split"] == "test":
            row["y"] = float(row["y"]) + 500
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    third, c = execute_task(task)
    assert third["status"] == "succeeded", third
    for name in ("candidates.csv", "permutation-importance.csv", "pdp.csv"):
        assert (a / name).read_bytes() == (c / name).read_bytes()


def test_mcp_can_preview_but_cannot_self_authorize_execution(task, monkeypatch):
    from runtime.services.mcp_gateway import MCPGateway
    roots, source, cfg = task
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("MCP escalated execution"))
    arguments = {"parameters": {"input_csv": str(source), "task_config": str(cfg)},
                 "project_id": "synthetic_regression", "stage": STAGE}
    gateway = MCPGateway()
    exposed = {item["name"] for item in gateway.tools()}
    assert TOOL in exposed
    assert "mlr3_regression_workflow" not in exposed
    result, error = gateway.call(TOOL, arguments)
    assert not error and result["mode"] == "preview"
    assert result["result"]["can_execute"]
    result, error = gateway.call(TOOL, {**arguments, "dry_run": False})
    assert error and result == {"error": "execution_not_authorized"}
    assert not (roots["AIRMOSAIC_ASSETS_DIR"] / "results").exists()


@pytest.mark.parametrize("kind,code", [("duplicate", "invalid_sample_keys"),
                                       ("label", "unknown_split_labels"),
                                       ("category", "unseen_categorical_level")])
def test_bad_inputs_stop_before_model_building(task, kind, code):
    require_r_packages()
    _, source, _ = task
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if kind == "duplicate":
        rows[1]["id"] = rows[0]["id"]
    elif kind == "label":
        rows[0]["split"] = "unexpected"
    else:
        rows[-1]["category"] = "unseen"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    record, output = execute_task(task)
    assert record["status"] == "failed"
    status = json.loads((output / "status.json").read_text())
    assert status["error_code"] == code
    assert not (output / "model.rds").exists()


def test_explicit_unseen_mapping_and_nested_output_keep_provenance(task):
    require_r_packages()
    roots, source, cfg_file = task
    cfg = configuration()
    cfg["unseen_categories"] = "train_mode"
    cfg_file.write_text(json.dumps(cfg), encoding="utf-8")
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows[-1]["category"] = "previously_unseen"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    run_id = "e" * 32
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_regression" / "custom_experiment" / "nested"
    result = ToolRunnerService().run(TOOL, {"out_dir": str(output), "task_config": str(cfg_file), "input_csv": str(source)},
                                     project_id="synthetic_regression", stage=STAGE, run_id=run_id, timeout=120)
    assert result["status"] == "succeeded", result
    assert (output / "provenance.json").is_file()
    assert not (output.parent / "provenance.json").exists()
    preprocessing = json.loads((output / "preprocessing.json").read_text())["preprocessing"]
    assert preprocessing["unseen_category_counts"]["test"]["category"] == 1
    assert preprocessing["unseen_categories"] == "train_mode"
