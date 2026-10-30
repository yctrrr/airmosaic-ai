"""Agent-authored orchestration example from ../prompt.md; no model implementation.

Only the registered synthetic fixture is used. Preflight is the default. Model
operations use the existing runner and skills, with no runtime LLM/API call.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from uuid import uuid4

HERE = Path(__file__).resolve().parent
REPO = next((parent for parent in Path(__file__).resolve().parents
             if (parent / "pyproject.toml").is_file() and (parent / "runtime/services").is_dir()), None)
if REPO is None:
    raise SystemExit("workflow_checkout_required")
sys.path.insert(0, str(REPO))
from runtime.services import ToolRunnerService, ToolExecutionError
from runtime.services.ml_execution_paths import WORKFLOW_RESULTS, MLExecutionPaths, workflow_result_name
from runtime.services.workflow_records import (WorkflowEvents, generation_material, retrospective,
    seal_run, timestamp, utc_offset, check_replay_dependencies, write_new as write_record)
from runtime.services.mlr3_workflow import output_path

INPUT = "assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv"
TASK = "config/examples/ml-regression/workflow-synthetic.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scores(truth: list[float], prediction: list[float]) -> dict:
    """Independent test oracle, rather than reusing the R metrics implementation."""
    if not truth or len(truth) != len(prediction) or not all(map(math.isfinite, truth + prediction)):
        raise ValueError("invalid_predictions")
    sse = math.fsum((y - p) ** 2 for y, p in zip(truth, prediction))
    average = math.fsum(truth) / len(truth)
    sst = math.fsum((y - average) ** 2 for y in truth)
    return {"rmse": math.sqrt(sse / len(truth)),
            "mae": math.fsum(abs(y - p) for y, p in zip(truth, prediction)) / len(truth),
            "r_squared": 1 - sse / sst if sst > 0 else None}


def verify(output: Path) -> dict:
    manifest = json.loads((output / "artifacts.json").read_text(encoding="utf-8"))["files"]
    metrics = json.loads(output_path(output, manifest["metrics"]).read_text(encoding="utf-8"))
    reproduction = json.loads(output_path(output, manifest["reproducibility"]).read_text(encoding="utf-8"))
    with output_path(output, manifest["predictions"]).open(encoding="utf-8", newline="") as stream:
        predictions = list(csv.DictReader(stream))
    with (REPO / INPUT).open(encoding="utf-8", newline="") as stream:
        source = {row["id"]: row for row in csv.DictReader(stream)}
    train_truth = [float(row["outcome"]) for row in source.values() if row["dataset"] == "train"]
    train_mean = math.fsum(train_truth) / len(train_truth)
    evidence = {}
    baselines = {}
    for split in ("val", "test"):
        rows = [row for row in predictions if row["split"] == split]
        ids = [row["sample_id"] for row in rows]
        expected = {key for key, row in source.items() if row["dataset"] == split}
        if len(ids) != len(set(ids)) or set(ids) != expected:
            raise ValueError("cohort_identity_mismatch")
        truth = [float(row["truth"]) for row in rows]
        if any(not math.isclose(y, float(source[row["sample_id"]]["outcome"]), rel_tol=1e-12, abs_tol=1e-12)
               for row, y in zip(rows, truth)):
            raise ValueError("source_truth_mismatch")
        calculated = scores(truth, [float(row["response"]) for row in rows])
        if any(not math.isclose(value, metrics[split][key], rel_tol=1e-10, abs_tol=1e-10)
               for key, value in calculated.items() if value is not None):
            raise ValueError("reported_metric_mismatch")
        baseline = scores(truth, [train_mean] * len(truth))
        if any(not math.isclose(value, metrics["baseline_" + split][key], rel_tol=1e-10, abs_tol=1e-10)
               for key, value in baseline.items() if value is not None):
            raise ValueError("reported_baseline_mismatch")
        baselines[split] = baseline
        evidence[split] = {"n": len(rows), **calculated}
    if (metrics["test_used_for_selection"] is not False
            or reproduction["reload_predictions_equal"] is not True):
        raise ValueError("freeze_or_reload_check_failed")
    # A predeclared fixture-specific smoke criterion, never a scientific acceptance threshold.
    if not evidence["test"]["rmse"] < baselines["test"]["rmse"]:
        raise ValueError("synthetic_baseline_check_failed")
    if len(predictions) != sum(evidence[name]["n"] for name in ("val", "test")):
        raise ValueError("unexpected_prediction_split")
    return {"status": "passed", "synthetic_only": True, "independent_metrics": evidence,
            "independent_mean_baseline": baselines,
            "environment": {"python": sys.version.split()[0], "R": reproduction.get("R"),
                            "packages": reproduction.get("packages", {})},
            "sample_identity_and_truths": "passed", "model_reload": "passed",
            "test_rmse_below_mean_baseline": True, "scientific_review": "not_applicable_to_smoke_check"}


def write_new(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--run-id", help="Optional internal fresh 32-character lowercase hex receipt ID")
    parser.add_argument("--task-name", default="synthetic_regression", help="Public lowercase task slug")
    parser.add_argument("--utc-offset", default="+08:00", help="Explicit time offset, e.g. +08:00 or +00:00")
    args = parser.parse_args()
    zone = utc_offset(args.utc_offset)
    started_at = datetime.now(zone)
    label = workflow_result_name(args.task_name, started_at)
    run_id = args.run_id or uuid4().hex
    context = MLExecutionPaths(REPO, run_id, "ml_regression_workflow", None, None, "workflow")
    output = context.parameter(str(REPO / WORKFLOW_RESULTS / label), "output_directory")
    bundled = HERE.name == "gen_script"
    task_file = HERE / "task.json" if bundled else REPO / TASK
    sources = ["workflows/ml_regression/workflow.yaml", "catalog/tools/ml_regression_workflow.yaml",
               "catalog/schemas/ml-regression-task.schema.json",
               "skills/model/shared/machine_learning_model/contracts/output-files.json"]
    sources += [p.relative_to(REPO).as_posix() for p in sorted(
        (REPO / "skills/model/shared/machine_learning_model/scripts").rglob("*.R"))]
    sources += [p.relative_to(REPO).as_posix() for p in sorted((REPO / "runtime").rglob("*.py"))]
    # A saved program replays only with the same reused dependency identities.
    if bundled:
        check_replay_dependencies(REPO, HERE / "dependencies.json", sources)
    materials = {"run.py": Path(__file__), "task.json": task_file}
    for name in ("prompt.md", "prompt_ZH.md", "request.md", "request_ZH.md"):
        materials[name] = (HERE / name if bundled else REPO / "workflows/ml_regression" /
                           (name if name.startswith("prompt") else "examples/" + name))
    events = WorkflowEvents(zone)
    events.emit("decision", "task_contract", "planned")
    events.emit("action_started", "preflight", "running")
    parameters = {"input_csv": str(REPO / INPUT), "task_config": str(task_file), "out_dir": str(output)}
    runner = ToolRunnerService()
    record = runner.run("ml_regression_workflow", parameters,
                        result_scope="workflow", run_id=run_id, dry_run=True, timeout=180)
    events.emit("observation", "preflight", "dry_run" if record["can_execute"] else "blocked",
                count=len(record["blockers"]))
    if not args.execute:
        print(json.dumps({**record, "result_name": label, "utc_offset": args.utc_offset}))
        return 0
    # Reserve the visible batch exclusively; receipts retain their separate internal ID.
    context.parameter(str(output), "output_directory")
    output.mkdir(parents=True, exist_ok=False)
    events.attach(output)
    write_record(output_path(output, "runner_preflight.json"), record)
    stage, status, evidence = "generation_material", "failed", None
    try:
        events.emit("action_started", stage, "running")
        generation = generation_material(output, REPO, materials, sources, args.task_name, timestamp(zone))
        events.emit("observation", stage, "succeeded", count=len(materials))
        if not record["can_execute"]:
            status, stage = "blocked", "preflight"
            events.emit("stopped", stage, status)
        else:
            stage = "compute"
            events.emit("decision", stage, "planned")
            events.emit("action_started", stage, "running")
            # Execute the preserved task, not a mutable configuration elsewhere.
            parameters["task_config"] = str(output / "gen_script/task.json")
            record = runner.run("ml_regression_workflow", parameters,
                                result_scope="workflow", run_id=run_id, timeout=180)
            write_record(output_path(output, "runner_record.json"), record)
            status = record["status"] if record["status"] in {"succeeded", "blocked"} else "failed"
            events.emit("observation", stage, status)
            if status == "succeeded":
                stage = "verify"
                events.emit("action_started", stage, "running")
                evidence = verify(output)
                if any(digest(REPO / name) != value for name, value in
                       generation["dependencies"]["source_sha256"].items()):
                    raise ValueError("workflow_dependency_changed")
                for name, value in generation["materials_sha256"].items():
                    if digest(materials[name]) != value or digest(output / "gen_script" / name) != value:
                        raise ValueError("workflow_material_changed")
                evidence.update(executed_at=timestamp(zone), run_id=run_id, result_name=label,
                    generation="replay_reviewed_agent_authored_example",
                    generation_replay="saved_source_and_config_with_dependency_identity_checks")
                write_new(output / "verification.json", evidence)
                events.emit("observation", stage, "passed", count=sum(
                    item["n"] for item in evidence["independent_metrics"].values()))
            else:
                events.emit("stopped", stage, status)
    except Exception:
        status = "failed"
        events.emit("stopped", stage, status)
        write_record(output_path(output, "workflow-error.json"),
                     {"status": status, "stage": stage, "error": "workflow_stage_failed"})
    terminal = {"schema_version": 1, "run_id": run_id, "result_name": label, "task_name": args.task_name,
        "started_at": started_at.isoformat(timespec="microseconds"), "finished_at": timestamp(zone),
        "utc_offset": args.utc_offset, "status": status, "last_stage": stage,
        "trace_coverage": "observed_controller_boundaries_not_full_agent_or_R_trace",
        "llm_generation_in_this_run": False, "scientific_review": "not_applicable_to_synthetic_check"}
    try:
        retrospective(output, status, stage, zone, evidence)
        events.emit("action_started", "delivery", "prepared")
        seal_run(output, terminal)
    except Exception:
        status = "failed"
        events.emit("stopped", "delivery", status)
        if not (output / "workflow.json").exists():
            write_record(output / "workflow.json", {**terminal, "status": status,
                "last_stage": "delivery", "error": "workflow_delivery_failed", "finished_at": timestamp(zone)})
    print(json.dumps({"status": "passed" if status == "succeeded" else status, "run_id": run_id,
                      "synthetic_only": True, "output": "${ML_WORKFLOW_RESULTS_DIR}/" + label}))
    return 0 if status == "succeeded" else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ToolExecutionError, ValueError, OSError):
        print(json.dumps({"status": "failed", "error": "workflow_example_rejected"}))
        raise SystemExit(2) from None
