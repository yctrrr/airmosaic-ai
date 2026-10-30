"""Explicit, study-specific launch; this is not a registered generic tool.

Run from the repository root. No settings, credentials or reference results are
auto-loaded. The reviewed launcher reuses core path/process/R helpers.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import time
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from runtime.services.tool_execution_paths import checked_path, separated_roots
from runtime.services.tool_process import child_environment, execute
from runtime.services import tool_r
from runtime.services.tool_readiness import _inside_git, _overlaps


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def load_protocol() -> dict:
    cfg = json.loads((HERE / "prediction.json").read_text(encoding="utf-8"))
    if (cfg["schema_version"] != 1 or cfg["project_id"] != "ozone_environmental_drivers"
            or cfg["learner"] != "regr.ranger" or cfg["selection_metric"] != "mean_fold_rmse"
            or cfg["threads"] != 1 or cfg["missing_policy"] != "complete_case_common_features"
            or cfg["respect_unordered_factors"] != "partition" or cfg["replace"] is not True
            or cfg["climate_levels"] != ["dry", "moist", "wet"]
            or not 2 <= cfg["folds"] <= 10 or not 1 <= cfg["candidate_count"] <= 20
            or not 1 <= cfg["num_trees"] <= 1000 or not 1 <= cfg["seed"] <= 2147450000
            or set(cfg["feature_sets"]) != {"model_1", "model_2"}
            or cfg["expected_counts"] != {"development": 4077, "test": 1009}):
        raise ValueError("invalid_protocol")
    reserved = {cfg["target"], cfg["id_column"], cfg["split_column"], cfg["country_column"]}
    for features in cfg["feature_sets"].values():
        if (not 1 <= len(features) <= 64 or len(set(features)) != len(features)
                or reserved & set(features) or cfg["climate_column"] not in features
                or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]{0,95}", item) for item in features)):
            raise ValueError("invalid_feature_set")
        combinations = len(features) * len(cfg["min_node_sizes"]) * len(cfg["sample_fractions"])
        if cfg["candidate_count"] > combinations:
            raise ValueError("search_budget_exceeds_grid")
    if (not all(isinstance(n, int) and 1 <= n <= 100 for n in cfg["min_node_sizes"])
            or not all(0.1 <= n <= 1 for n in cfg["sample_fractions"])):
        raise ValueError("invalid_search_space")
    return cfg


def verify_output(output: Path, source: Path, cfg: dict) -> dict:
    """Recompute scores without R, then verify source truths and cohort membership."""
    with (output / "test_predictions.csv").open(encoding="utf-8-sig", newline="") as stream:
        predictions = list(csv.DictReader(stream))
    with (output / "development_oof_predictions.csv").open(encoding="utf-8-sig", newline="") as stream:
        development = list(csv.DictReader(stream))
    with (output / "development_folds.csv").open(encoding="utf-8-sig", newline="") as stream:
        folds = list(csv.DictReader(stream))
    if (len(predictions) != 1009 or len(development) != 4077
            or len({r["sample_id"] for r in predictions}) != 1009
            or len({r["sample_id"] for r in development}) != 4077
            or {r["sample_id"] for r in predictions} & {r["sample_id"] for r in development}
            or [r["sample_id"] for r in folds] != [r["sample_id"] for r in development]
            or set(int(r["fold"]) for r in folds) != set(range(1, cfg["folds"] + 1))):
        raise ValueError("invalid_output_cohort")
    # Independent source parsing verifies truths and split membership, not just
    # self-consistency between generated files. Source bytes remain unchanged.
    with source.open(encoding="utf-8", newline="") as stream:
        originals = {r[cfg["id_column"]]: r for r in csv.DictReader(stream)}
    countries = Counter(r[cfg["country_column"]] for r in originals.values())
    numeric_features = {f for fs in cfg["feature_sets"].values() for f in fs} - {cfg["climate_column"]}
    expected = {"development": set(), "test": set()}
    for key, row in originals.items():
        climate = row[cfg["climate_column"]].rsplit("_", 1)[-1]
        if countries[row[cfg["country_column"]]] <= cfg["minimum_country_count_exclusive"] or climate not in cfg["climate_levels"]:
            continue
        values = [float(row[name]) if row[name].strip() else math.nan for name in (*numeric_features, cfg["target"])]
        if any(not math.isfinite(v) or v in cfg["missing_sentinels"] for v in values):
            continue
        scope = "test" if row[cfg["split_column"]] == cfg["test_label"] else "development"
        expected[scope].add(key)
    if (expected["test"] != {r["sample_id"] for r in predictions}
            or expected["development"] != {r["sample_id"] for r in development}):
        raise ValueError("independent_cohort_mismatch")
    for rows, labels in ((predictions, {cfg["test_label"]}), (development, set(cfg["development_labels"]))):
        for row in rows:
            original = originals[row["sample_id"]]
            if (original[cfg["split_column"]] not in labels
                    or float(original[cfg["target"]]) != float(row["truth"])):
                raise ValueError("source_truth_or_split_mismatch")
    r_metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))["metrics"]
    independent = {}
    for scope, rows in (("test", predictions), ("development_oof", development)):
        truth = [float(row["truth"]) for row in rows]
        mean = math.fsum(truth) / len(truth)
        tss = math.fsum((value - mean) ** 2 for value in truth)
        for model in ("baseline", "model_1", "model_2"):
            response = [float(row[model]) for row in rows]
            if not all(math.isfinite(value) for value in (*truth, *response)):
                raise ValueError("nonfinite_prediction")
            error = [y - p for y, p in zip(truth, response)]
            sse = math.fsum(value ** 2 for value in error)
            score = {"rmse": math.sqrt(sse / len(truth)),
                     "mae": math.fsum(abs(value) for value in error) / len(truth),
                     "r_squared": 1 - sse / tss}
            for metric, value in score.items():
                if not math.isclose(value, r_metrics[model][scope][metric], rel_tol=1e-10, abs_tol=1e-10):
                    raise ValueError("independent_metric_mismatch")
            independent.setdefault(model, {})[scope] = {"n": len(truth), **score}
    train_mean = math.fsum(float(r["truth"]) for r in development) / len(development)
    if not all(math.isclose(float(r["baseline"]), train_mean, abs_tol=1e-10) for r in predictions):
        raise ValueError("baseline_training_mean_mismatch")
    # Verify every OOF baseline also excludes that station's complete fold.
    fold_values = [int(r["fold"]) for r in folds]
    sizes = Counter(fold_values)
    if max(sizes.values()) - min(sizes.values()) > 1:
        raise ValueError("unbalanced_fold_sizes")
    for fold in range(1, cfg["folds"] + 1):
        training = [float(r["truth"]) for r, k in zip(development, fold_values) if k != fold]
        expected = math.fsum(training) / len(training)
        if not all(math.isclose(float(r["baseline"]), expected, abs_tol=1e-10)
                   for r, k in zip(development, fold_values) if k == fold):
            raise ValueError("oof_baseline_leakage")
    selections = json.loads((output / "selected_models.json").read_text(encoding="utf-8"))
    if selections["test_used_for_selection"] is not False:
        raise ValueError("invalid_selection_provenance")
    for model in ("model_1", "model_2"):
        with (output / f"{model}_candidates.csv").open(encoding="utf-8-sig", newline="") as stream:
            candidates = list(csv.DictReader(stream))
        with (output / f"{model}_fold_scores.csv").open(encoding="utf-8-sig", newline="") as stream:
            fold_scores = list(csv.DictReader(stream))
        if len(candidates) != cfg["candidate_count"] or len(fold_scores) != cfg["candidate_count"] * cfg["folds"]:
            raise ValueError("incomplete_cv_search")
        for candidate in candidates:
            scores = [float(r["rmse"]) for r in fold_scores if r["candidate_id"] == candidate["candidate_id"]]
            if len(scores) != cfg["folds"] or not math.isclose(math.fsum(scores) / len(scores), float(candidate["mean_fold_rmse"]), abs_tol=1e-10):
                raise ValueError("fold_score_summary_mismatch")
        winner = min(candidates, key=lambda row: float(row["mean_fold_rmse"]))
        if int(winner["candidate_id"]) != selections["models"][model]["candidate_id"]:
            raise ValueError("cv_selection_mismatch")
        for parameter, value in selections["models"][model]["parameters"].items():
            if not math.isclose(float(winner[parameter]), value, abs_tol=1e-12):
                raise ValueError("selected_parameter_mismatch")
    return {"status": "passed", "source_truths_and_split_membership": True,
            "independent_cohort_membership": True, "cv_selection_and_fold_scores": True,
            "disjoint_station_keys": True, "independent_metrics": independent,
            "training_mean_and_oof_baseline": True}


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--execute", action="store_true", help="Without this flag only preflight is performed.")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checks without fitting the real cohort.")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", args.batch_id) or not 1 <= args.timeout <= 3600:
        raise ValueError("invalid_execution_scope")
    cfg = load_protocol()
    roots = separated_roots(REPO)
    assets = roots["AIRMOSAIC_ASSETS_DIR"]
    inputs = {}
    for role in ("input", "dictionary"):
        relative = Path(cfg[role])
        path = checked_path(str(assets / relative))
        if (relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(assets / "data")
                or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024
                or digest(path) != cfg[role + "_sha256"]):
            raise ValueError("input_integrity_mismatch")
        inputs[role] = path
    with inputs["dictionary"].open(encoding="utf-8", newline="") as stream:
        dictionary = {r["column_name"]: r for r in csv.DictReader(stream)}
    requested = {cfg["target"], *(f for fs in cfg["feature_sets"].values() for f in fs)}
    if not requested <= dictionary.keys() or dictionary[cfg["target"]]["unit"] != cfg["target_unit"]:
        raise ValueError("dictionary_contract_mismatch")
    output = checked_path(str(assets / "results" / cfg["project_id"] / args.batch_id))
    if not output.is_relative_to(assets / "results" / cfg["project_id"]) or output.exists() or _inside_git(output):
        raise ValueError("output_not_fresh_or_outside_project")
    executable = tool_r.r_executable()
    library = checked_path(os.environ.get("AIRMOSAIC_R_LIBRARY", ""))
    if (executable is None or not library.is_dir() or _inside_git(library)
            or any(_overlaps(library, other) for other in (roots["AIRMOSAIC_CONFIG_DIR"], roots["AIRMOSAIC_AUTH_DIR"], assets / "data", output))):
        raise ValueError("invalid_explicit_r_runtime")
    if args.execute and args.self_test:
        raise ValueError("select_execution_or_self_test")
    if not args.execute and not args.self_test:
        print(json.dumps({"status": "preflight_passed", "execution": "not_started",
                          "input_hashes": "verified", "target_unit": cfg["target_unit"],
                          "models": list(cfg["feature_sets"]), "cv_fits": cfg["folds"] * cfg["candidate_count"] * 2,
                          "r_packages": "checked_during_execution", "output": "${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<batch_id>/"}))
        return
    output.mkdir(parents=True, exist_ok=False)
    snapshot = output / "source_snapshot"
    snapshot.mkdir()
    sources = {name: HERE / name for name in ("prediction.R", "prediction_checks.R", "run_prediction.py", "prediction.json", "prediction_prompt.md", "prediction_prompt_ZH.md")}
    sources["skill_io.R"] = REPO / "skills/model/shared/machine_learning_model/scripts/r/common/io.R"
    sources["reproduction.R"] = REPO / "skills/model/shared/machine_learning_model/scripts/r/models/reproduction.R"
    sources["regression_skill.md"] = REPO / "skills/model/shared/machine_learning_model/SKILL.md"
    sources["mlr3_skill.md"] = REPO / "skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL.md"
    hashes = {}
    for name, source in sources.items():
        hashes[name] = digest(source)
        shutil.copyfile(source, snapshot / name)
        if digest(snapshot / name) != hashes[name]:
            raise ValueError("snapshot_mismatch")
    temp = output / ".airmosaic"
    temp.mkdir()
    context = SimpleNamespace(assets=assets, output=output, temp=temp)
    entry = snapshot / ("prediction_checks.R" if args.self_test else "prediction.R")
    env = tool_r.environment(child_environment(context, None), entry,
                             ["jsonlite", "mlr3", "mlr3learners", "ranger"], temp, None, library)
    env["AIRMOSAIC_SKILL_IO"] = str(snapshot / "skill_io.R")
    env["AIRMOSAIC_REPRODUCTION_LIB"] = str(snapshot / "reproduction.R")
    record = {"status": "running", "started_at": now(), "experiment_id": cfg["experiment_id"],
              "mode": "synthetic_self_test" if args.self_test else "real_data_experiment",
              "source_sha256": hashes, "input_sha256": cfg["input_sha256"],
              "dictionary_sha256": cfg["dictionary_sha256"], "timeout_seconds": args.timeout,
              "original_code_result_comparison": "awaiting_user_materials"}
    write_json(output / "execution-start.json", record)
    argv = [str(executable), "--vanilla", "-e", tool_r.R_GUARD,
            "--input-csv", str(inputs["input"]), "--protocol", str(snapshot / "prediction.json"), "--out-dir", str(output)]
    started = time.monotonic()
    failure_code = "experiment_process_failed"
    try:
        return_code, reason, stopped, captured = execute(argv, temp, env, args.timeout, True)
        record.update(return_code=return_code, process_reason=reason, process_tree_stopped=stopped)
        # Persist the non-identifying progress protocol, never raw child output.
        progress = [line for line in captured.decode("utf-8", errors="replace").splitlines()
                    if re.fullmatch(r"CV model_[12] candidate [0-9]+/[0-9]+ completed|EXPERIMENT completed", line)]
        (output / "progress.txt").write_text("\n".join(progress) + "\n", encoding="utf-8")
        if return_code != 0 or reason not in (None, "completed"):
            raise ValueError(failure_code)
        failure_code = "source_integrity_failed"
        if any(digest(inputs[role]) != cfg[role + "_sha256"] for role in inputs):
            raise ValueError("source_changed_during_execution")
        record["source_inputs_unchanged"] = True
        if args.self_test:
            record["status"] = "synthetic_checks_passed"
        else:
            failure_code = "output_verification_failed"
            verification = verify_output(output, inputs["input"], cfg)
            write_json(output / "independent-verification.json", verification)
            record["status"] = "completed"
        failure_code = "source_integrity_failed"
        record["source_code_unchanged"] = all(digest(p) == hashes[n] for n, p in sources.items())
        if not record["source_code_unchanged"]:
            raise ValueError("source_code_changed_during_execution")
        record.update(finished_at=now(), elapsed_seconds=round(time.monotonic() - started, 3))
        failure_code = "terminal_receipt_failed"
        if (output / "execution.json").exists():
            raise ValueError(failure_code)
        failure_code = "artifact_sealing_failed"
        if not args.self_test:
            artifact_hashes = {str(p.relative_to(output)).replace("\\", "/"): digest(p)
                               for p in output.rglob("*") if p.is_file() and ".airmosaic" not in p.parts
                               and p.name not in ("execution.json", "artifact-sha256.json")}
            # Seal the intended terminal bytes before publishing success. A seal
            # failure must produce one failed receipt, never success then failure.
            terminal_bytes = (json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
            artifact_hashes["execution.json"] = hashlib.sha256(terminal_bytes).hexdigest()
            write_json(output / "artifact-sha256.json", artifact_hashes)
        failure_code = "terminal_receipt_failed"
        write_json(output / "execution.json", record)
    except Exception as error:
        record.update(status="failed", error=failure_code, finished_at=now(),
                      elapsed_seconds=round(time.monotonic() - started, 3))
        # Exclusive creation preserves any terminal receipt already present.
        if not (output / "execution.json").exists():
            write_json(output / "execution.json", record)
        raise ValueError(failure_code) from error
    if args.self_test:
        print(json.dumps({"status": record["status"], "elapsed_seconds": record["elapsed_seconds"]}))
    else:
        print(json.dumps({"status": "completed", "verification": verification["status"],
                          "elapsed_seconds": record["elapsed_seconds"],
                          "test_metrics": {k: v["test"] for k, v in verification["independent_metrics"].items()}}))



if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Arguments, tracebacks and raw paths never enter public terminal output.
        print(json.dumps({"status": "failed", "error": str(error) if isinstance(error, ValueError) else type(error).__name__}))
        raise SystemExit(1)
