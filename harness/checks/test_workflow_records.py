"""Naming, real event coverage, dependency identity and terminal delivery checks."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from runtime.services.ml_execution_paths import workflow_result_name, MLExecutionPaths
from runtime.services.workflow_records import (WorkflowEvents, dependency_evidence,
    check_replay_dependencies, seal_run, utc_offset)
from test_ml_regression_workflow import task, REPO
from test_ml_regression_recipe import load_example


def test_minute_names_are_readable_and_offset_aware():
    stamp = datetime(2026, 10, 28, 18, 30, 12, 123456, tzinfo=utc_offset("+08:00"))
    assert workflow_result_name("synthetic_regression", stamp) == "202610281830_synthetic_regression"
    assert workflow_result_name("synthetic_regression", stamp.replace(second=59, microsecond=999999)) == workflow_result_name("synthetic_regression", stamp)
    assert workflow_result_name("synthetic_regression", stamp.replace(minute=31)) != workflow_result_name("synthetic_regression", stamp)
    with pytest.raises(ValueError):
        workflow_result_name("../private", stamp)
    with pytest.raises(ValueError):
        workflow_result_name("task", stamp.replace(tzinfo=None))


@pytest.mark.parametrize("offset", ["system", "+14:01", "../auth", "+25:00", "+08:99"])
def test_offset_rejects_invalid_settings(offset):
    with pytest.raises(ValueError):
        utc_offset(offset)


def test_event_schema_rejects_raw_text_and_preserves_observed_order(tmp_path):
    events = WorkflowEvents(timezone.utc)
    events.emit("action_started", "preflight", "running")
    events.emit("observation", "preflight", "dry_run", count=0)
    events.attach(tmp_path)
    events.emit("action_started", "compute", "running")
    rows = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert [row["sequence"] for row in rows] == [1, 2, 3]
    assert all(row["record_type"] == "observed_controller_event" for row in rows)
    assert rows[0]["occurred_at"] <= rows[2]["occurred_at"]
    with pytest.raises(ValueError):
        events.emit("private raw output", "compute", "running")
    with pytest.raises(ValueError):
        events.emit("observation", "compute", "private exception path")
    with pytest.raises(ValueError):
        events.emit("observation", "compute", "passed", count=True)


@pytest.mark.parametrize("before_end,after_end", [("\n", "\n"), ("", ""), ("", "\n"), ("\n", "")])
def test_dependency_patch_recovers_modified_and_untracked_public_code(tmp_path, before_end, after_end):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    code = repo / "runtime/example.py"
    code.parent.mkdir()
    code.write_text("value = 1" + before_end, encoding="utf-8")
    subprocess.run(["git", "add", "runtime/example.py"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
                    "commit", "-qm", "synthetic base"], cwd=repo, check=True)
    code.write_text("value = 2" + after_end, encoding="utf-8")
    added = repo / "runtime/added.py"
    added.write_text("other = 3" + after_end, encoding="utf-8")
    empty = repo / "runtime/empty.py"
    empty.write_text("", encoding="utf-8")
    names = ["runtime/example.py", "runtime/added.py", "runtime/empty.py"]
    evidence, patch = dependency_evidence(repo, names)
    declaration = tmp_path / "dependencies.json"
    declaration.write_text(json.dumps(evidence), encoding="utf-8")
    check_replay_dependencies(repo, declaration, names)
    code.write_text("value = 1" + before_end, encoding="utf-8")
    added.unlink()
    empty.unlink()
    patchfile = tmp_path / "changes.patch"
    patchfile.write_text(patch, encoding="utf-8", newline="\n")
    result = subprocess.run(["git", "apply", "--ignore-whitespace", str(patchfile)], cwd=repo, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert all(hashlib.sha256((repo / name).read_text(encoding="utf-8").encode()).hexdigest() == digest
               for name, digest in evidence["source_sha256_lf_utf8"].items())
    evidence["source_sha256"]["../auth/private.json"] = "a" * 64
    declaration.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid_dependency_declaration"):
        check_replay_dependencies(repo, declaration, names)


def test_delivery_seals_terminal_and_refuses_existing_terminal(tmp_path):
    (tmp_path / "events.jsonl").write_text('{"sequence":1}\n', encoding="utf-8")
    seal_run(tmp_path, {"status": "succeeded"})
    seal = json.loads((tmp_path / "delivery-sha256.json").read_text())["file_sha256"]
    assert all(hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == value for name, value in seal.items())
    before = (tmp_path / "workflow.json").read_bytes()
    with pytest.raises(ValueError):
        seal_run(tmp_path, {"status": "failed"})
    assert (tmp_path / "workflow.json").read_bytes() == before


def controller_fixture(task, tmp_path, monkeypatch):
    module = load_example()
    # Keep all workflow writes in a synthetic checkout, never in historical runs.
    repo = tmp_path / "controller"
    repo.mkdir()
    (repo / ".gitignore").write_text('/workflows/ml_regression/results/\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for name in ("config/examples/ml-regression/workflow-synthetic.json", "workflows/ml_regression/workflow.yaml",
                 "catalog/tools/ml_regression_workflow.yaml", "catalog/schemas/ml-regression-task.schema.json",
                 "skills/model/shared/machine_learning_model/contracts/output-files.json"):
        target = repo / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(REPO / name, target)
    for base in ("workflows/ml_regression/prompt.md", "workflows/ml_regression/prompt_ZH.md",
                 "workflows/ml_regression/examples/request.md", "workflows/ml_regression/examples/request_ZH.md"):
        target = repo / base; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(REPO / base, target)
    # A fake validated runner isolates controller bookkeeping from R numerical tests.
    calls = []
    class Runner:
        def run(self, tool, parameters, **options):
            calls.append((parameters.copy(), options.copy()))
            return {"can_execute": True, "blockers": [], "status": "dry_run" if options["dry_run"] else "succeeded"} if "dry_run" in options else {"status": "succeeded"}
    monkeypatch.setattr(module, "REPO", repo)
    monkeypatch.setattr(module, "ToolRunnerService", Runner)
    monkeypatch.setattr(module, "generation_material", lambda *args: {"dependencies": {"source_sha256": {}}, "materials_sha256": {}})
    return module, repo, calls


@pytest.mark.parametrize("failure", ["verification", "compute", "seal", "none"])
def test_controller_keeps_failure_evidence_and_never_reports_false_success(task, tmp_path, monkeypatch, capsys, failure):
    module, repo, calls = controller_fixture(task, tmp_path, monkeypatch)
    def verify(output):
        if failure == "verification":
            raise ValueError("private filesystem information")
        return {"independent_metrics": {"test": {"n": 100, "rmse": 1.0}}}
    monkeypatch.setattr(module, "verify", verify)
    if failure == "compute":
        class BrokenRunner:
            def run(self, tool, params, **options):
                return {"can_execute": True, "blockers": [], "status": "dry_run"} if options.get("dry_run") else {"status": "failed"}
        monkeypatch.setattr(module, "ToolRunnerService", BrokenRunner)
    if failure == "seal":
        def fail_seal(*args):
            raise OSError("private source path")
        monkeypatch.setattr(module, "seal_run", fail_seal)
    monkeypatch.setattr(sys, "argv", ["example", "--execute", "--task-name", "controller_check"])
    code = module.main()
    result = json.loads(capsys.readouterr().out)
    output = repo / "workflows/ml_regression/results" / result["output"].rsplit("/", 1)[-1]
    terminal = json.loads((output / "workflow.json").read_text())
    assert terminal["status"] == ("succeeded" if failure == "none" else "failed")
    assert code == (0 if failure == "none" else 3)
    assert not (output / "source_snapshot").exists()
    assert (output / "retrospective_ZH.md").is_file()
    assert "private" not in (output / "events.jsonl").read_text()
    assert "private" not in (output / "workflow.json").read_text()


def test_same_minute_task_collision_preserves_the_first_result(task, tmp_path, monkeypatch, capsys):
    module, repo, _ = controller_fixture(task, tmp_path, monkeypatch)
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, zone):
            return datetime(2026, 10, 28, 18, 30, 12, 123456, tzinfo=zone)
    monkeypatch.setattr(module, "datetime", FixedDateTime)
    monkeypatch.setattr(module, "verify", lambda output: {"independent_metrics": {"test": {"n": 100, "rmse": 1.0}}})
    monkeypatch.setattr(sys, "argv", ["example", "--execute", "--task-name", "same_minute"])
    assert module.main() == 0
    first = json.loads(capsys.readouterr().out)
    output = repo / "workflows/ml_regression/results/202610281830_same_minute"
    before = (output / "workflow.json").read_bytes()
    with pytest.raises(FileExistsError):
        module.main()
    assert first["status"] == "passed"
    assert (output / "workflow.json").read_bytes() == before
