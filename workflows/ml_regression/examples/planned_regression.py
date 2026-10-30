"""Plan-bound regression orchestration; default checks review without generating code.

--generate saves a reviewed caller after approval. The saved caller requires
independent code/test checks before --execute. Numerical work remains in skills.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
from uuid import uuid4

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = next((p for p in Path(__file__).resolve().parents
                     if (p / "runtime/services").is_dir()), None)


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def check_control_paths(task):
    reserved = [PurePosixPath(name) for name in
                ("gen_script", "runner_preflight.json", "reviewed_runner_preflight.json",
                 "planning-preview.json", "runner_record.json", "events.jsonl")]
    for name in task["output_files"].values():
        path = PurePosixPath(name.casefold())
        if any(path == item or item in path.parents or path in item.parents for item in reserved):
            raise ValueError("workflow_control_artifact_collision")


def main():
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            raise ValueError("invalid_planned_model_arguments")
    parser = Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--delegation", type=Path)
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--out-dir", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--generate", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.repo is None:
        raise ValueError("explicit_runtime_required")
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo))
    from runtime.services import ToolRegistryService, ToolRunnerService
    from runtime.services.ml_execution_paths import MLExecutionPaths
    from runtime.services.tool_execution_paths import checked_path
    spec = importlib.util.spec_from_file_location("regression_plan_gate",
        repo / "skills/model/shared/machine_learning_model/scripts/common/review_plan.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    bundled = HERE.name == "gen_script" and (HERE / "generation.json").is_file()
    plan_path = args.plan or (HERE / "plan.json" if bundled else None)
    if plan_path is None:
        raise ValueError("model_plan_required")
    plan = gate.read_json(plan_path)
    task = gate.validate_configuration(plan["task"], repo)
    check_control_paths(task)
    python_backend = task.get("backend") == "python"
    tool_id = "ml_python_regression_workflow" if python_backend else "ml_regression_workflow"
    if python_backend and task["execution"]["purpose"] != "new_study":
        raise ValueError("planned_python_requires_new_study_purpose")
    review_path = args.review or (HERE / "review.json" if bundled else None)
    grant_path = args.delegation or (HERE / "delegation.json" if bundled and (HERE / "delegation.json").is_file() else None)
    review = gate.read_json(review_path) if review_path else None
    grant = gate.read_json(grant_path) if grant_path else None
    options = {}
    if args.execute:
        if not bundled:
            raise ValueError("execute_saved_reviewed_bundle")
        options = {"phase": "execute", "task": gate.read_json(HERE / "task.json"),
                   "code": Path(__file__), "code_check":
                       gate.read_json(HERE / "code-check.json") if (HERE / "code-check.json").is_file() else None}
    assessment = gate.assess(plan, repo, review=review, delegation=grant,
                             input_csv=args.input_csv, **options)
    if assessment["status"] != "approved" or not (args.generate or args.execute):
        print(json.dumps(assessment))
        return 0 if assessment["status"] == "approved" else 3
    if args.out_dir is None:
        raise ValueError("fresh_result_destination_required")
    metadata = gate.read_json(HERE / "generation.json") if bundled else None
    run_id = metadata["run_id"] if metadata else uuid4().hex
    paths = MLExecutionPaths(repo, run_id, tool_id, args.project_id, None, "project")
    output = paths.parameter(str(args.out_dir.resolve()), "output_directory")
    runner = ToolRunnerService(ToolRegistryService(repo))
    if args.generate:
        # This is the first experiment-code write and occurs after plan approval.
        output.mkdir(parents=True, exist_ok=False)
        generated = output / "gen_script"
        generated.mkdir()
        sources = {"plan.json": plan_path, "review.json": review_path}
        if grant_path:
            sources["delegation.json"] = grant_path
        for name, source in sources.items():
            write_new(generated / name, gate.read_json(source))
        write_new(generated / "task.json", plan["task"])
        source = Path(__file__).read_text(encoding="utf-8")
        ast.parse(source)
        write_new(generated / "run.py", source)
        parameters = {"input_csv": str(args.input_csv.resolve()),
                      "task_config": str(generated / "task.json"), "out_dir": str(output)}
        pending = {"schema_version": 1, "plan_sha256": gate.plan_hash(plan),
            "code_sha256": sha(generated / "run.py"), "checked_at": now(), "reviewer": "agent",
            "checks": {"syntax": True, "scope": True, "task_binding": True,
                       "dry_run": False, "synthetic_tests": False},
            "basis": "Syntax and fixed caller identity checked; independent technical checks remain required."}
        implementation = None
        if python_backend:
            from runtime.services.model_plan_gate import python_implementation_hashes
            implementation = python_implementation_hashes(repo)
            # Pending checks are explicit: static preview does not grant execution.
            preview_bundle = {"plan": plan, "review": review, "delegation": grant,
                "code_check": pending, "code_file": str((generated / "run.py").resolve()),
                "implementation_sha256": implementation}
            preview = output / "planning-preview.json"
            write_new(preview, preview_bundle)
            parameters["review_bundle"] = str(preview)
        preflight = runner.run(tool_id, parameters,
            project_id=args.project_id, run_id=run_id, dry_run=True, timeout=180)
        write_new(output / "runner_preflight.json", preflight)
        materials = {p.name: sha(p) for p in generated.iterdir() if p.is_file()}
        generation = {
            "schema_version": 1, "run_id": run_id, "generated_at": now(),
            "mode": "copied_reviewed_plan_bound_caller", "llm_generation": False,
            "plan_sha256": gate.plan_hash(plan), "materials_sha256": materials}
        if python_backend:
            generation["implementation_sha256"] = implementation
        write_new(generated / "generation.json", generation)
        pending["checks"]["dry_run"] = preflight["can_execute"]
        write_new(generated / "code-check.pending.json", pending)
        write_new(output / "events.jsonl", json.dumps({
            "at": now(), "kind": "generation_completed_after_plan_review",
            "plan_sha256": gate.plan_hash(plan), "reviewer": review["reviewer"]}) + "\n")
        print(json.dumps({"status": "generated_pending_code_check", "plan_sha256": gate.plan_hash(plan),
                          "can_execute": False, "preflight_can_execute": preflight["can_execute"]}))
        return 0 if preflight["can_execute"] else 3
    if not bundled or output != HERE.parent.resolve() or args.plan or args.review or args.delegation:
        raise ValueError("execute_saved_reviewed_bundle")
    expected = {"plan.json", "review.json", "task.json", "run.py"}
    if (set(metadata["materials_sha256"]) not in (expected, expected | {"delegation.json"})
            or any(sha(HERE / name) != value for name, value in metadata["materials_sha256"].items())):
        raise ValueError("generated_material_changed")
    audit = gate.read_json(HERE / "code-check.json")
    gate.require(plan, repo, phase="execute", review=review, delegation=grant,
        input_csv=args.input_csv, task=gate.read_json(HERE / "task.json"),
        code=Path(__file__), code_check=audit)
    # Common imports must come from the selected runtime, never an editable fallback.
    for name, module in tuple(sys.modules.items()):
        path = getattr(module, "__file__", None)
        if (name == "runtime" or name.startswith("runtime.")) and path:
            if not Path(path).resolve().is_relative_to(repo):
                raise ValueError("unexpected_runtime_import")
    parameters = {"input_csv": str(args.input_csv.resolve()),
                  "task_config": str(HERE / "task.json"), "out_dir": str(output)}
    if python_backend:
        # The source inventory was captured at generation and must still match.
        bundle = {"plan": plan, "review": review, "delegation": grant,
                  "code_check": audit, "code_file": str(Path(__file__).resolve()),
                  "implementation_sha256": metadata["implementation_sha256"]}
        bundle_path = HERE / "review-bundle.json"
        write_new(bundle_path, bundle)
        parameters["review_bundle"] = str(bundle_path)
        preflight = runner.run(tool_id, parameters, project_id=args.project_id,
            run_id=run_id, dry_run=True, timeout=180)
        write_new(output / "reviewed_runner_preflight.json", preflight)
        if not preflight["can_execute"]:
            print(json.dumps({"status": "blocked", "reason": "reviewed_model_preflight_blocked"}))
            return 3
    with (output / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": now(), "kind": "execution_started_after_code_check",
                                 "plan_sha256": gate.plan_hash(plan)}) + "\n")
    record = runner.run(tool_id, parameters,
        project_id=args.project_id, run_id=run_id, timeout=180,
        allow_network=False, confirm_browser_session=False)
    write_new(output / "runner_record.json", record)
    with (output / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": now(), "kind": "execution_returned",
                                 "status": record["status"]}) + "\n")
    print(json.dumps({"status": record["status"], "plan_sha256": gate.plan_hash(plan),
                      "scientific_acceptance": "pending_result_review"}))
    return 0 if record["status"] == "succeeded" else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print(json.dumps({"status": "blocked", "error": "planned_regression_rejected",
                          "can_generate": False, "can_execute": False}))
        raise SystemExit(2) from None
