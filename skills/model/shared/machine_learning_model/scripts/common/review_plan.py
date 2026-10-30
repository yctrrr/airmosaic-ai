"""Check a modelling plan before experiment-code generation and execution.

Records are attestations supplied by a trusted caller. This helper neither
authenticates a human nor grants permissions to a process or filesystem.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

REPO = next((p for p in Path(__file__).resolve().parents
             if (p / "runtime/services").is_dir()), None)
if REPO is not None:
    sys.path.insert(0, str(REPO))
from jsonschema import Draft202012Validator
from runtime.services.mlr3_workflow import validate_configuration as validate_r_configuration
from runtime.services.tool_execution_paths import ToolExecutionError, checked_path

CHECKS = {"syntax", "scope", "task_binding", "dry_run", "synthetic_tests"}


class PlanError(ValueError):
    """Value-free error suitable for sanitized execution records."""


def validate_configuration(value: dict, repo: Path) -> dict:
    """Select an explicit implemented backend; historical tasks remain R tasks."""
    if isinstance(value, dict) and value.get("backend") == "python":
        from runtime.services.python_ml_workflow import validate_configuration as validate_python
        try:
            return validate_python(value, repo)
        except (ValueError, TypeError, KeyError, OSError):
            raise ToolExecutionError("invalid_python_ml_configuration") from None
    return validate_r_configuration(value, repo)


def canonical(value) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, RecursionError):
        raise PlanError("invalid_plan_json") from None


def plan_hash(plan: dict) -> str:
    return hashlib.sha256(canonical(plan)).hexdigest()


def digest(path: Path) -> str:
    path = checked_path(str(path))
    if any(p.casefold() in {"auth", "credentials", "secrets", ".git"} for p in path.parts):
        raise PlanError("private_plan_input_location")
    if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        raise PlanError("plan_input_unavailable")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    path = checked_path(str(path))
    if path.suffix != ".json" or path.stat().st_size > 1024 * 1024:
        raise PlanError("plan_record_unavailable")
    digest(path)  # Reject private locations before opening contents.
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        raise PlanError("invalid_plan_record") from None
    if not isinstance(value, dict):
        raise PlanError("invalid_plan_record")
    return value


def moment(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None or result > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError
        return result
    except (ValueError, AttributeError, TypeError):
        raise PlanError("invalid_review_timestamp") from None


def validate_plan(plan: dict, repo: Path) -> dict:
    schema = json.loads((repo / "skills/model/shared/machine_learning_model/contracts/model-plan.schema.json").read_text(encoding="utf-8"))
    if not Draft202012Validator(schema).is_valid(plan):
        raise PlanError("invalid_model_plan")
    moment(plan["created_at"])
    try:
        cfg = validate_configuration(plan["task"], repo)
        names = [v["column"] for v in plan["variables"]]
        if len(set(names)) != len(names) or set(names) != set(cfg["features"]):
            raise PlanError("variable_rationale_mismatch")
        if any(v["role"] != ("adjustment" if cfg["analysis"] == "causal_plr" else "predictor")
               for v in plan["variables"]):
            raise PlanError("variable_role_mismatch")
        learners = {m["learner"] for m in cfg["models"]}
        space = plan["parameter_space"]
        if set(space) != learners:
            raise PlanError("parameter_space_mismatch")
        for learner in learners:
            models = [m for m in cfg["models"] if m["learner"] == learner]
            keys = set().union(*(m["parameters"] for m in models))
            if set(space[learner]) != keys:
                raise PlanError("parameter_space_mismatch")
            for parameter, values in space[learner].items():
                # Ranges describe valid supported values, not an implicit search.
                for value in values:
                    trial = deepcopy(plan["task"])
                    target = next(m for m in trial["models"] if m["learner"] == learner)
                    target["parameters"][parameter] = value
                    validate_configuration(trial, repo)
            for model in models:
                for parameter, value in model["parameters"].items():
                    if canonical(value) not in [canonical(v) for v in space[learner][parameter]]:
                        raise PlanError("candidate_outside_reviewed_range")
    except ToolExecutionError:
        raise PlanError("unsupported_planned_task") from None
    return cfg


def evidence(value: dict) -> None:
    if (not isinstance(value, dict) or set(value) != {"reference", "statement"}
            or not all(isinstance(v, str) and 8 <= len(v) <= 4000 for v in value.values())):
        raise PlanError("missing_user_evidence")


def assess(plan: dict, repo: Path, *, phase: str = "generate", review: dict | None = None,
           delegation: dict | None = None, input_csv: Path | None = None,
           task: dict | None = None, code: Path | None = None,
           code_check: dict | None = None) -> dict:
    if phase not in {"generate", "execute"}:
        raise PlanError("invalid_review_phase")
    cfg = validate_plan(plan, repo)
    identity = plan_hash(plan)
    if input_csv is not None and digest(input_csv) != plan["data"]["input_sha256"]:
        raise PlanError("planned_input_changed")
    base = {"plan_id": plan["plan_id"], "plan_sha256": identity, "phase": phase,
            "can_generate": False, "can_execute": False}
    if any(issue["blocking"] for issue in plan["issues"]):
        return {**base, "status": "blocked", "reason": "unresolved_plan_issue"}
    if review is None:
        return {**base, "status": "pending_human_review", "reason": "review_required"}
    expected = {"schema_version", "plan_sha256", "reviewer", "decision",
                "reviewed_at", "stages", "evidence", "basis"}
    if (set(review) != expected or review["schema_version"] != 1
            or review["reviewer"] not in {"human", "agent"}
            or review["decision"] not in {"approved", "changes_requested", "rejected"}
            or not isinstance(review["basis"], str) or len(review["basis"]) < 12):
        raise PlanError("invalid_plan_review")
    if review["plan_sha256"] != identity:
        raise PlanError("reviewed_plan_changed")
    reviewed = moment(review["reviewed_at"])
    if reviewed < moment(plan["created_at"]):
        raise PlanError("review_predates_plan")
    evidence(review["evidence"])
    if (not isinstance(review["stages"], list) or not review["stages"]
            or len(set(review["stages"])) != len(review["stages"])
            or not set(review["stages"]) <= {"generate", "execute"}):
        raise PlanError("invalid_review_scope")
    if review["reviewer"] == "agent":
        fields = {"schema_version", "plan_sha256", "source", "permissions", "recorded_at", "evidence"}
        if (delegation is None or set(delegation) != fields or delegation["schema_version"] != 1
                or delegation["plan_sha256"] != identity or delegation["source"] != "user"
                or not isinstance(delegation["permissions"], list)
                or not {"review", phase} <= set(delegation["permissions"])
                or not set(delegation["permissions"]) <= {"review", "generate", "execute"}):
            raise PlanError("agent_review_requires_user_delegation")
        evidence(delegation["evidence"])
        if moment(delegation["recorded_at"]) > reviewed:
            raise PlanError("delegation_after_agent_review")
    if review["decision"] != "approved":
        return {**base, "status": review["decision"], "reason": "plan_not_approved"}
    if phase not in review["stages"]:
        return {**base, "status": "blocked", "reason": "review_scope_does_not_allow_phase"}
    if input_csv is None:
        raise PlanError("reviewed_input_required")
    if phase == "execute":
        if task is None or canonical(validate_configuration(task, repo)) != canonical(cfg):
            raise PlanError("generated_task_changed")
        fields = {"schema_version", "plan_sha256", "code_sha256", "checked_at", "reviewer", "checks", "basis"}
        if (code is None or code_check is None or set(code_check) != fields
                or code_check["schema_version"] != 1 or code_check["plan_sha256"] != identity
                or code_check["code_sha256"] != digest(code)
                or code_check["reviewer"] not in {"human", "agent"}
                or not isinstance(code_check["basis"], str) or len(code_check["basis"]) < 12
                or set(code_check["checks"]) != CHECKS
                or not all(value is True for value in code_check["checks"].values())):
            raise PlanError("generated_code_check_required")
        if moment(code_check["checked_at"]) < reviewed:
            raise PlanError("code_check_predates_review")
    generation_allowed = ("generate" in review["stages"] and
        (review["reviewer"] == "human" or "generate" in delegation["permissions"]))
    return {**base, "status": "approved", "reviewer": review["reviewer"],
            "can_generate": generation_allowed, "can_execute": phase == "execute",
            "scientific_acceptance": "not_granted", "authorization": "caller_attested_not_authenticated"}


def require(plan: dict, repo: Path, **kwargs) -> dict:
    result = assess(plan, repo, **kwargs)
    if result["status"] != "approved":
        raise PlanError(result["reason"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--delegation", type=Path)
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--phase", choices=("generate", "execute"), default="generate")
    parser.add_argument("--task-config", type=Path)
    parser.add_argument("--code", type=Path)
    parser.add_argument("--code-check", type=Path)
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args()
    result = assess(read_json(args.plan), args.repo, phase=args.phase,
        review=read_json(args.review) if args.review else None,
        delegation=read_json(args.delegation) if args.delegation else None,
        input_csv=args.input_csv,
        task=read_json(args.task_config) if args.task_config else None,
        code=args.code, code_check=read_json(args.code_check) if args.code_check else None)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "approved" else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PlanError, ToolExecutionError, OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"status": "blocked", "error": "model_plan_check_failed",
                          "can_generate": False, "can_execute": False}))
        raise SystemExit(2) from None
