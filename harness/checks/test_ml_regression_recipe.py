"""Generated orchestration, fixed synthetic scope and migration checks."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from runtime.services import ToolExecutionError, ToolRunnerService
from runtime.services.ml_execution_paths import MLExecutionPaths, WORKFLOW_RESULTS
from test_ml_regression_workflow import task, REPO, require_r_packages

EXAMPLE = REPO / "workflows/ml_regression/examples/generated_regression.py"
TOY = "assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv"


def load_example():
    spec = importlib.util.spec_from_file_location("generated_regression_example", EXAMPLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checkout(tmp_path):
    repo = tmp_path / "checkout"
    repo.mkdir()
    (repo / ".gitignore").write_text('/' + WORKFLOW_RESULTS + '/\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for name in (TOY, "assets/toy-manifest.json"):
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / name, target)
    return repo


def paths(repo):
    return MLExecutionPaths(repo, "a" * 32, "ml_regression_workflow", None, None, "workflow")


def test_workflow_scope_is_fixed_synthetic_and_ignored(task, tmp_path):
    _, private, _ = task
    repo = checkout(tmp_path)
    selected = paths(repo)
    assert selected.base == repo / WORKFLOW_RESULTS
    assert selected.parameter(str(repo / TOY), "input_file") == repo / TOY
    with pytest.raises(ToolExecutionError, match="workflow_requires_manifest_listed_synthetic_input"):
        selected.parameter(str(private), "input_file")
    with pytest.raises(ToolExecutionError, match="workflow_output_outside_results"):
        selected.parameter(str(repo / "projects/output"), "output_directory")
    assert str(repo) not in json.dumps(selected.public_locations())


def test_workflow_rejects_changed_synthetic_and_missing_ignore(task, tmp_path):
    repo = checkout(tmp_path)
    selected = paths(repo)
    with (repo / TOY).open("a", encoding="utf-8") as stream:
        stream.write("changed\n")
    with pytest.raises(ToolExecutionError, match="workflow_requires_manifest_listed_synthetic_input"):
        selected.parameter(str(repo / TOY), "input_file")
    (repo / ".gitignore").write_text("", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="workflow_results_must_be_git_ignored"):
        paths(repo)


def test_workflow_scope_rejects_project_nested_git_and_reserved(task, tmp_path):
    repo = checkout(tmp_path)
    with pytest.raises(ToolExecutionError, match="project_id_conflicts_with_workflow_scope"):
        MLExecutionPaths(repo, "a" * 32, "ml_regression_workflow", "study", None, "workflow")
    selected = paths(repo)
    with pytest.raises(ToolExecutionError, match="private_output_component"):
        selected.parameter(str(selected.base / "secrets"), "output_directory")
    nested = selected.base / "nested"
    nested.mkdir(parents=True)
    (nested / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="nested_git_in_workflow_results"):
        selected.parameter(str(nested / "output"), "output_directory")


@pytest.mark.parametrize("marker", ["directory", "file"])
@pytest.mark.parametrize("ancestor", ["workflows", "workflows/ml_regression"])
def test_workflow_rejects_nested_repository_above_result_base(task, tmp_path, marker, ancestor):
    repo = checkout(tmp_path)
    nested = repo / ancestor
    nested.mkdir(parents=True)
    if marker == "directory":
        (nested / ".git").mkdir()
    else:
        (nested / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="nested_git_in_workflow_results"):
        paths(repo)


def test_generated_example_preflight_does_not_compute(task, monkeypatch, capsys):
    import sys
    example = load_example()
    monkeypatch.setattr(sys, "argv", [str(EXAMPLE), "--run-id", "b" * 32])
    assert example.main() == 0
    record = json.loads(capsys.readouterr().out)
    assert record["status"] == "dry_run" and record["result_scope"] == "workflow"
    assert not (REPO / WORKFLOW_RESULTS / ("b" * 32)).exists()


def test_workflow_direct_runner_preflight(task):
    record = ToolRunnerService().run("ml_regression_workflow",
        {"input_csv": str(REPO / TOY), "task_config": "config/examples/ml-regression/workflow-synthetic.json"},
        result_scope="workflow", dry_run=True)
    assert record["status"] == "dry_run" and record["can_execute"]


def test_generated_metric_oracle_and_malformed_data():
    module = load_example()
    assert module.scores([1., 2., 3.], [1., 2., 3.]) == {"rmse": 0, "mae": 0, "r_squared": 1}
    assert module.scores([1., 1.], [0., 0.])["r_squared"] is None
    for truth, prediction in (([], []), ([1.], []), ([1.], [float("nan")])):
        with pytest.raises(ValueError, match="invalid_predictions"):
            module.scores(truth, prediction)


def test_generated_verifier_rejects_forged_baseline(tmp_path):
    import csv
    import math
    module = load_example()
    with (REPO / TOY).open(encoding="utf-8", newline="") as stream:
        source = list(csv.DictReader(stream))
    train = [float(row["outcome"]) for row in source if row["dataset"] == "train"]
    mean = math.fsum(train) / len(train)
    predictions = [{"sample_id": row["id"], "split": row["dataset"], "truth": row["outcome"],
                    "response": row["outcome"]} for row in source if row["dataset"] in ("val", "test")]
    with (tmp_path / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader(); writer.writerows(predictions)
    metrics = {"test_used_for_selection": False}
    for split in ("val", "test"):
        truth = [float(row["truth"]) for row in predictions if row["split"] == split]
        metrics[split] = module.scores(truth, truth)
        metrics["baseline_" + split] = module.scores(truth, [mean] * len(truth))
    (tmp_path / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    (tmp_path / "reproduction.json").write_text('{"reload_predictions_equal":true}', encoding="utf-8")
    (tmp_path / "artifacts.json").write_text(json.dumps({"files": {
        "predictions": "predictions.csv", "metrics": "metrics.json", "reproducibility": "reproduction.json"}}))
    assert module.verify(tmp_path)["status"] == "passed"
    metrics["baseline_test"]["rmse"] *= 2
    (tmp_path / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    with pytest.raises(ValueError, match="reported_baseline_mismatch"):
        module.verify(tmp_path)


def test_flattened_project_preserves_executable_references():
    project = REPO / "projects/0001_ozone_environmental_drivers"
    assert not (project / "experiments/paper_prediction").exists()
    cfg = json.loads((project / "project.json").read_text(encoding="utf-8"))
    for key in ("protocol", "agent_prompt", "agent_prompt_zh", "launcher"):
        assert (project / cfg["prediction_experiment"][key]).is_file()
    assert (project / "prediction.R").is_file()
    assert (project / "prediction_checks.R").is_file()
