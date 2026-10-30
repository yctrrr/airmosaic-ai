"""Synthetic checks for preserved R registration and plan-bound Python execution."""
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

from runtime.services import ToolRegistryService, ToolRunnerService, ToolExecutionError
from runtime.services import tool_readiness
from runtime.services.model_plan_gate import ENTRY, python_implementation_hashes, require_python_plan
from runtime.services.python_ml_workflow import validate_configuration, validate_outputs

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "config/examples/machine-learning-model/python/synthetic-regression.json"
TOY = REPO / "assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv"
TOOL = "ml_python_regression_workflow"


def stamp():
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def reviewed(tmp_path, monkeypatch):
    roots = {}
    for variable, name in (("AIRMOSAIC_ASSETS_DIR", "assets"), ("AIRMOSAIC_CONFIG_DIR", "settings"),
                           ("AIRMOSAIC_AUTH_DIR", "auth")):
        root = tmp_path / name
        root.mkdir()
        monkeypatch.setenv(variable, str(root))
        roots[variable] = root
    source = roots["AIRMOSAIC_ASSETS_DIR"] / "data/synthetic.csv"
    source.parent.mkdir()
    source.write_bytes(TOY.read_bytes())
    cfg = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    cfg["execution"]["purpose"] = "new_study"
    cfg["explanation"]["methods"] = []
    cfg["explanation"]["features"] = []
    spec = importlib.util.spec_from_file_location("integration_plan_gate", REPO /
        "skills/model/shared/machine_learning_model/scripts/common/review_plan.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    note = {"choice": "An explicit synthetic check only.", "reason": "Synthetic interface validation, not a study decision.",
            "evidence": ["synthetic_test_fixture"], "alternatives": ["another test-only design"],
            "uncertainty": "No scientific acceptance is established by this fixture."}
    space = {}
    for model in cfg["models"]:
        ranges = space.setdefault(model["learner"], {})
        for key, value in model["parameters"].items():
            ranges.setdefault(key, []).append(value)
    plan = {"schema_version": 1, "plan_id": "synthetic_python_plan", "mode": "build", "created_at": stamp(),
            "question": "Validate Python plan execution with synthetic data only.",
            "data": {"asset_id": "synthetic_fixture", "input_sha256": gate.digest(source),
                     "dictionary_sha256": "a" * 64, "development_profile_sha256": "b" * 64},
            "task": cfg, "decisions": {key: deepcopy(note) for key in
                ("target", "variables", "parameters", "split", "preprocessing", "evaluation", "interpretation")},
            "variables": [{"column": name, "physical_meaning": "Synthetic variable only.", "unit": "synthetic",
                           "role": "predictor", "reason": note["reason"], "evidence": note["evidence"],
                           "uncertainty": note["uncertainty"]} for name in cfg["features"]],
            "parameter_space": space, "issues": [], "review_policy": "human_by_default"}
    identity = gate.plan_hash(plan)
    review = {"schema_version": 1, "plan_sha256": identity, "reviewer": "human", "decision": "approved",
              "reviewed_at": stamp(), "stages": ["generate", "execute"],
              "evidence": {"reference": "synthetic_test_fixture", "statement": "Simulated approval in a unit test only."},
              "basis": "Synthetic review records do not represent a real human approval."}
    generated = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_plan/gen_script"
    generated.mkdir(parents=True)
    code = generated / "caller.py"
    code.write_text("# Synthetic generated-caller fixture, never executed.\n", encoding="utf-8")
    check = {"schema_version": 1, "plan_sha256": identity, "code_sha256": gate.digest(code), "checked_at": stamp(),
             "reviewer": "agent", "checks": {key: True for key in gate.CHECKS},
             "basis": "Simulated code-check evidence for an isolated unit test."}
    bundle = {"plan": plan, "review": review, "delegation": None, "code_check": check, "code_file": str(code),
              "implementation_sha256": python_implementation_hashes(REPO)}
    bundle_file = roots["AIRMOSAIC_CONFIG_DIR"] / "review.json"
    bundle_file.write_text(json.dumps(bundle), encoding="utf-8")
    task_file = roots["AIRMOSAIC_CONFIG_DIR"] / "task.json"
    task_file.write_text(json.dumps(cfg), encoding="utf-8")
    return roots, source, cfg, task_file, bundle, bundle_file, code


def test_existing_tool_id_and_both_entrypoints_are_real():
    registry = ToolRegistryService()
    for name in ("ml_regression_workflow", TOOL):
        tool = registry._tools[name]
        assert tool["skill_id"] == "machine-learning-model"
        assert (REPO / tool["entrypoint"]["path"]).is_file()


def test_declared_python_minimum_is_checked(monkeypatch):
    tool = ToolRegistryService()._tools[TOOL]
    monkeypatch.setattr(tool_readiness.sys, "version_info", (3, 10, 99))
    python = next(x for x in tool_readiness.check_readiness(tool, REPO)["checks"] if x["kind"] == "python")
    assert python["status"] == "missing_dependency"


def test_full_python_plan_binds_task_input_code_and_implementation(reviewed):
    _, source, cfg, _, bundle, bundle_file, _ = reviewed
    result = require_python_plan(validate_configuration(cfg, REPO), source, REPO / ENTRY, review_bundle=bundle_file)
    assert result["scientific_acceptance"] == "not_granted"
    bundle["implementation_sha256"] = {}
    bundle_file.write_text(json.dumps(bundle), encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="implementation_changed"):
        require_python_plan(validate_configuration(cfg, REPO), source, REPO / ENTRY, review_bundle=bundle_file)


@pytest.mark.parametrize("change", ["input", "code", "delegation", "code_check"])
def test_python_execution_refuses_stale_or_unapproved_records(reviewed, change):
    _, source, cfg, _, bundle, bundle_file, code = reviewed
    if change == "input":
        source.write_text("changed synthetic input\n", encoding="utf-8")
    elif change == "code":
        code.write_text("# Changed synthetic code.\n", encoding="utf-8")
    elif change == "delegation":
        bundle["review"]["reviewer"] = "agent"
    else:
        bundle["code_check"]["checks"]["synthetic_tests"] = False
    bundle_file.write_text(json.dumps(bundle), encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="python_model_plan_rejected"):
        require_python_plan(validate_configuration(cfg, REPO), source, REPO / ENTRY, review_bundle=bundle_file)


def test_new_study_preview_does_not_open_input_rows(reviewed, monkeypatch):
    _, source, _, task, _, bundle, _ = reviewed
    original = Path.open
    def guarded(path, *args, **kwargs):
        if path == source:
            pytest.fail("preview read model input contents")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)
    record = ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(task),
        "review_bundle": str(bundle)}, project_id="synthetic_gate", dry_run=True)
    assert record["status"] == "dry_run"
    assert record["model_plan"] == "control_records_checked_data_binding_pending"


def test_engineering_replay_cannot_relabel_arbitrary_external_data(reviewed):
    _, source, cfg, task, _, _, _ = reviewed
    cfg["execution"]["purpose"] = "engineering_replay"
    task.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="requires_manifest_synthetic_input"):
        ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(task)},
                                project_id="synthetic_gate", dry_run=True)


def test_actual_runner_new_study_uses_plan_bound_synthetic_fixture(reviewed):
    pytest.importorskip("sklearn")
    roots, source, _, task, _, bundle, _ = reviewed
    result = ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(task),
        "review_bundle": str(bundle)}, project_id="synthetic_gate", timeout=120)
    assert result["status"] == "succeeded", result
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_gate" / result["run_id"]
    assert validate_outputs(output)
    assert result["model_review"]["scientific_acceptance"] == "not_granted"


def test_input_change_immediately_after_plan_check_cannot_become_new_baseline(reviewed, monkeypatch):
    pytest.importorskip("sklearn")
    from runtime.services import model_plan_gate
    roots, source, cfg, task, _, bundle, _ = reviewed
    script = REPO / ENTRY
    spec = importlib.util.spec_from_file_location("ordering_checked_python_model", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = model_plan_gate.require_python_plan
    def checked_then_changed(*args, **kwargs):
        result = original(*args, **kwargs)
        # Preserve CSV shape while changing one synthetic target after approval.
        import csv
        with source.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        rows[0][cfg["target"]] = str(float(rows[0][cfg["target"]]) + 1)
        with source.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0])
            writer.writeheader()
            writer.writerows(rows)
        return result
    monkeypatch.setattr(model_plan_gate, "require_python_plan", checked_then_changed)
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_gate/changed_after_gate"
    with pytest.raises(ValueError, match="input_changed_during_execution"):
        module.run(source, task, output, review_bundle=bundle)
    assert not (output / "artifacts.json").exists()


def test_planned_python_caller_generates_then_checks_before_execution(reviewed, monkeypatch, capsys):
    pytest.importorskip("sklearn")
    roots, source, _, _, bundle, _, _ = reviewed
    plan = roots["AIRMOSAIC_CONFIG_DIR"] / "plan.json"
    review = roots["AIRMOSAIC_CONFIG_DIR"] / "decision.json"
    plan.write_text(json.dumps(bundle["plan"]), encoding="utf-8")
    review.write_text(json.dumps(bundle["review"]), encoding="utf-8")
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_caller/experiment"
    spec = importlib.util.spec_from_file_location("integration_planned_caller", REPO /
        "workflows/ml_regression/examples/planned_regression.py")
    caller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caller)
    monkeypatch.setattr(sys, "argv", ["planned", "--repo", str(REPO), "--plan", str(plan),
        "--review", str(review), "--input-csv", str(source), "--project-id", "synthetic_caller",
        "--out-dir", str(output), "--generate"])
    assert caller.main() == 0
    assert json.loads(capsys.readouterr().out)["can_execute"] is False
    pending = json.loads((output / "gen_script/code-check.pending.json").read_text(encoding="utf-8"))
    assert pending["checks"]["synthetic_tests"] is False
    command = [sys.executable, "-B", "-X", "utf8", str(output / "gen_script/run.py"),
        "--repo", str(REPO), "--input-csv", str(source), "--project-id", "synthetic_caller",
        "--out-dir", str(output), "--execute"]
    blocked = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert blocked.returncode == 2 and not (output / "artifacts.json").exists()
    # Simulated technical attestation only, after the refusal assertion above.
    pending["checks"] = {key: True for key in pending["checks"]}
    pending["checked_at"] = stamp()
    pending["basis"] = "Synthetic integration fixture checks the protocol, not a real study approval."
    (output / "gen_script/code-check.json").write_text(json.dumps(pending), encoding="utf-8")
    completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
    assert completed.returncode == 0, completed.stdout
    assert validate_outputs(output)
    assert (output / "gen_script/review-bundle.json").is_file()


def test_mcp_python_execution_uses_same_runner_on_manifest_synthetic_input(reviewed):
    pytest.importorskip("sklearn")
    from runtime.services.mcp_gateway import MCPGateway, MCPPolicy
    roots, _, _, _, _, _, _ = reviewed
    gateway = MCPGateway(policy=MCPPolicy(execution_tools=frozenset({TOOL})))
    response, error = gateway.call(TOOL, {"parameters": {"input_csv": str(TOY),
        "task_config": "config/examples/machine-learning-model/python/synthetic-regression.json"},
        "project_id": "synthetic_mcp", "result_scope": "project", "dry_run": False, "timeout": 120})
    assert not error and response["result"]["status"] == "succeeded", response
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_mcp" / response["result"]["run_id"]
    assert validate_outputs(output)
