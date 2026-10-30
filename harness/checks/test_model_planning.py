"""Scientific plan gates use synthetic fixtures; no records attest a real approval."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from test_ml_regression_workflow import configuration, REPO

SPEC = importlib.util.spec_from_file_location("tested_model_plan",
    REPO / "skills/model/shared/machine_learning_model/scripts/common/review_plan.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def stamp():
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def records(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text("id,x,y\ns1,1,2\n", encoding="utf-8")
    cfg = configuration()
    cfg["analysis"] = "prediction"
    cfg["feature_selection"] = {"mode": "manual"}
    note = {"choice": "An explicit test-only scientific choice.",
            "reason": "Synthetic contract coverage, not scientific authorization.",
            "evidence": ["synthetic_test_fixture"], "alternatives": ["another reviewed test choice"],
            "uncertainty": "Test-only content does not identify a real effect."}
    space = {}
    for model in cfg["models"]:
        ranges = space.setdefault(model["learner"], {})
        for name, value in model["parameters"].items():
            ranges.setdefault(name, []).append(value)
    plan = {"schema_version": 1, "plan_id": "synthetic_plan", "mode": "build",
        "created_at": stamp(), "question": "A synthetic plan gate boundary check.",
        "data": {"asset_id": "synthetic_fixture", "input_sha256": gate.digest(source),
                 "dictionary_sha256": "a" * 64, "development_profile_sha256": "b" * 64},
        "task": cfg, "decisions": {key: deepcopy(note) for key in
            ("target", "variables", "parameters", "split", "preprocessing", "evaluation", "interpretation")},
        "variables": [{"column": name, "physical_meaning": "Synthetic numeric or category fixture.",
                       "unit": "synthetic", "role": "predictor", "reason": note["reason"],
                       "evidence": note["evidence"], "uncertainty": note["uncertainty"]} for name in cfg["features"]],
        "parameter_space": space, "issues": [], "review_policy": "human_by_default"}
    review = {"schema_version": 1, "plan_sha256": gate.plan_hash(plan), "reviewer": "human",
        "decision": "approved", "reviewed_at": stamp(), "stages": ["generate", "execute"],
        "evidence": {"reference": "synthetic_test_fixture", "statement": "Simulated approval in a unit test only."},
        "basis": "Synthetic test exercises the declared review boundary."}
    delegation = {"schema_version": 1, "plan_sha256": gate.plan_hash(plan), "source": "user",
        "permissions": ["review", "generate", "execute"], "recorded_at": review["reviewed_at"],
        "evidence": {"reference": "synthetic_test_fixture", "statement": "Simulated delegation in a unit test only."}}
    code = tmp_path / "candidate.py"
    code.write_text("print('synthetic candidate')\n", encoding="utf-8")
    audit = {"schema_version": 1, "plan_sha256": gate.plan_hash(plan), "code_sha256": gate.digest(code),
        "checked_at": stamp(), "reviewer": "agent", "checks": {key: True for key in gate.CHECKS},
        "basis": "Synthetic code-review fixture; no production authorization."}
    return plan, review, delegation, source, code, audit


def test_missing_review_does_not_allow_generation(records):
    plan, _, _, source, _, _ = records
    result = gate.assess(plan, REPO, input_csv=source)
    assert result["status"] == "pending_human_review"
    assert not result["can_generate"] and not result["can_execute"]


def test_human_plan_approval_allows_generation_but_is_not_execution_check(records):
    plan, review, _, source, _, _ = records
    assert gate.require(plan, REPO, review=review, input_csv=source)["can_generate"]
    with pytest.raises(gate.PlanError, match="generated_code_check_required"):
        gate.require(plan, REPO, phase="execute", review=review, input_csv=source, task=plan["task"])


def test_agent_cannot_approve_itself_without_user_delegation(records):
    plan, review, grant, source, _, _ = records
    review["reviewer"] = "agent"
    with pytest.raises(gate.PlanError, match="requires_user_delegation"):
        gate.require(plan, REPO, review=review, input_csv=source)
    assert gate.require(plan, REPO, review=review, delegation=grant, input_csv=source)["can_generate"]


@pytest.mark.parametrize("change", ["features", "range", "split", "preprocessing", "input", "reason"])
def test_review_does_not_survive_changed_plan(records, change):
    plan, review, _, source, _, _ = records
    if change == "features":
        plan["variables"][0]["physical_meaning"] = "A changed scientific interpretation."
    elif change == "range":
        plan["parameter_space"]["regr.rpart"]["maxdepth"].append(4)
    elif change == "split":
        plan["decisions"]["split"]["choice"] = "A revised independent split design."
    elif change == "preprocessing":
        plan["task"]["missing"]["policy"] = "drop"
    elif change == "input":
        plan["data"]["asset_id"] = "different_version"
    else:
        plan["decisions"]["parameters"]["reason"] = "A changed parameter-selection rationale."
    with pytest.raises(gate.PlanError, match="reviewed_plan_changed"):
        gate.require(plan, REPO, review=review, input_csv=source)


def test_changed_input_fails_before_generation(records):
    plan, review, _, source, _, _ = records
    source.write_text("changed\n")
    with pytest.raises(gate.PlanError, match="planned_input_changed"):
        gate.require(plan, REPO, review=review, input_csv=source)


@pytest.mark.parametrize("failure", ["code", "task", "check", "scope", "issue"])
def test_execution_boundaries(records, failure):
    plan, review, _, source, code, audit = records
    task = deepcopy(plan["task"])
    if failure == "code":
        code.write_text("changed\n")
    elif failure == "task":
        task["models"][0]["parameters"]["maxdepth"] = 4
    elif failure == "check":
        audit["checks"]["synthetic_tests"] = False
    elif failure == "scope":
        review["stages"] = ["generate"]
    else:
        plan["issues"] = [{"id": "missing_design", "blocking": True,
                          "description": "Unresolved scientific design prevents execution."}]
    with pytest.raises(gate.PlanError):
        gate.require(plan, REPO, phase="execute", review=review, input_csv=source,
                     task=task, code=code, code_check=audit)


def test_approved_and_checked_execution_retains_scientific_review(records):
    plan, review, _, source, code, audit = records
    result = gate.require(plan, REPO, phase="execute", review=review, input_csv=source,
                          task=plan["task"], code=code, code_check=audit)
    assert result["can_execute"]
    assert result["scientific_acceptance"] == "not_granted"


def test_plan_requires_variable_and_parameter_rationales(records):
    plan, _, _, _, _, _ = records
    plan["variables"].pop()
    with pytest.raises(gate.PlanError, match="variable_rationale"):
        gate.validate_plan(plan, REPO)


def test_plan_parameter_range_must_fit_supported_adapter(records):
    plan, _, _, _, _, _ = records
    plan["parameter_space"]["regr.rpart"]["maxdepth"] = [31]
    with pytest.raises(gate.PlanError, match="unsupported"):
        gate.validate_plan(plan, REPO)


def test_review_evidence_and_timezone_are_required(records):
    plan, review, _, source, _, _ = records
    review["evidence"] = {}
    with pytest.raises(gate.PlanError, match="missing_user_evidence"):
        gate.require(plan, REPO, review=review, input_csv=source)
    review["evidence"] = {"reference": "synthetic_test_fixture", "statement": "Simulated approval in a unit test only."}
    review["reviewed_at"] = "2026-10-29T00:00:00"
    with pytest.raises(gate.PlanError, match="timestamp"):
        gate.require(plan, REPO, review=review, input_csv=source)

def load_controller():
    spec = importlib.util.spec_from_file_location("tested_planned_controller",
        REPO / "workflows/ml_regression/examples/planned_regression.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_controller_waits_before_writing_experiment_code(records, tmp_path, monkeypatch, capsys):
    import sys
    plan, _, _, source, _, _ = records
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")
    output = tmp_path / "not_created"
    monkeypatch.setattr(sys, "argv", ["planned_regression", "--repo", str(REPO),
        "--plan", str(plan_file), "--input-csv", str(source), "--project-id", "test_plan",
        "--out-dir", str(output), "--generate"])
    assert load_controller().main() == 3
    assert json.loads(capsys.readouterr().out)["status"] == "pending_human_review"
    assert not output.exists()


def test_empty_or_incomplete_reasons_do_not_validate(records):
    plan, _, _, _, _, _ = records
    plan["decisions"]["parameters"]["evidence"] = []
    with pytest.raises(gate.PlanError, match="invalid_model_plan"):
        gate.validate_plan(plan, REPO)


@pytest.mark.parametrize("reviewer", ["human", "agent"])
def test_execute_only_approval_does_not_grant_generation(records, reviewer):
    plan, review, grant, source, code, audit = records
    review["reviewer"] = reviewer
    review["stages"] = ["execute"]
    grant["permissions"] = ["review", "execute"]
    result = gate.require(plan, REPO, phase="execute", review=review,
        delegation=grant if reviewer == "agent" else None, input_csv=source,
        task=plan["task"], code=code, code_check=audit)
    assert result["can_execute"] and not result["can_generate"]


@pytest.mark.parametrize("relative", ["runner_record.json", "RUNNER_PREFLIGHT.json", "gen_script/status.json"])
def test_scientific_artifacts_cannot_overwrite_workflow_control(records, relative):
    plan, _, _, _, _, _ = records
    cfg = deepcopy(plan["task"])
    cfg["output_files"] = {"status": relative}
    normalized = gate.validate_configuration(cfg, REPO)
    with pytest.raises(ValueError, match="workflow_control_artifact_collision"):
        load_controller().check_control_paths(normalized)


def test_custom_scientific_output_subdirectories_remain_supported(records):
    plan, _, _, _, _, _ = records
    cfg = deepcopy(plan["task"])
    cfg["output_files"] = {"metrics": "statistics/metrics.json"}
    load_controller().check_control_paths(gate.validate_configuration(cfg, REPO))
