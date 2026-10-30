"""Compare sealed prediction exports without running or deserializing models.

Only explicitly selected local configuration and manifest-declared files are read.
This is a mistake-prevention boundary, not an OS sandbox against concurrent IO.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sys

REPO = Path(__file__).resolve().parents[5]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from runtime.services.tool_execution_paths import (  # noqa: E402
    ToolExecutionError, checked_path, separated_roots, parse_parameters,
)
from runtime.services.tool_readiness import _inside_git  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

MAX_JSON = 4 * 1024 * 1024
MAX_FILE = 256 * 1024 * 1024
MAX_TOTAL = 1024 * 1024 * 1024
MAX_ROWS = 1_000_000
MAX_FILES = 1024
RESERVED = {"auth", "credentials", "secrets", "browser_profiles", ".ssh", ".git", ".env"}
DEFAULT_FILES = {
    "state": "state.json", "artifacts": "artifacts.json", "normalized": "normalized.csv",
    "paired": "paired.csv", "cohort_differences": "cohort-differences.csv",
    "metrics": "metrics.json", "comparison": "comparison.json", "report": "report.md", "report_zh": "report_ZH.md",
    "source_hashes": "source-hashes.json", "output_sha256": "output-sha256.json",
}


def fail(code):
    raise ToolExecutionError(code)


def private_component(part):
    part = part.casefold()
    return (part in RESERVED or part.startswith(".env.") or part.startswith("id_rsa")
            or part.startswith("id_ed25519") or part.endswith((".pem", ".key", ".p12", ".pfx")))


def relative_name(value):
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or value.startswith("/") or any(p in {"", ".", ".."} for p in value.split("/"))
            or any(private_component(p) for p in value.split("/"))):
        fail("invalid_artifact_path")
    if any(p.endswith((".", " ")) or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", p, re.I)
           for p in value.split("/")):
        fail("invalid_artifact_path")
    return PurePosixPath(value)


def secure_path(path, allow_git=False):
    path = checked_path(str(path))
    if any(private_component(p) for p in path.parts):
        fail("private_path_component")
    if not allow_git and _inside_git(path):
        fail("path_inside_git")
    return path


def artifact(root, name):
    return secure_path(root / relative_name(name))


def overlap(a, b):
    return a.is_relative_to(b) or b.is_relative_to(a)


def read_json(path, limit=MAX_JSON):
    if not path.is_file() or path.stat().st_size > limit:
        fail("json_unavailable_or_too_large")
    try:
        # The core parser rejects duplicate keys, non-finite JSON and deep JSON.
        return parse_parameters(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError):
        fail("invalid_json_file")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def expand(value, assets):
    if not isinstance(value, str):
        fail("invalid_path")
    value = value.replace("${AIRMOSAIC_ASSETS_DIR}", str(assets))
    if "${" in value:
        fail("unsupported_path_placeholder")
    return secure_path(Path(value))


def validate_config(cfg, repo=REPO):
    schema = json.loads((repo / "catalog/schemas/model-reproduction-task.schema.json").read_text(encoding="utf-8"))
    if not Draft202012Validator(schema).is_valid(cfg):
        fail("invalid_task_schema")
    ids = []
    for side in ("candidate", "reference"):
        models = cfg[side]["models"]
        current = [m["id"] for m in models]
        if len(set(current)) != len(current):
            fail("duplicate_model_id")
        ids.append(set(current))
        relative_name(cfg[side]["manifest"])
        for model in models:
            if Path(model["predictions"]).suffix.casefold() != ".csv":
                fail("predictions_must_be_csv")
            relative_name(model["predictions"])
            if len({model[k] for k in ("id_column", "truth_column", "prediction_column")}) != 3:
                fail("columns_must_be_distinct")
            if "reported_metrics" in model:
                metrics = model["reported_metrics"]
                relative_name(metrics["file"])
                if Path(metrics["file"]).suffix.casefold() != ".json":
                    fail("reported_metrics_must_be_json")
    if ids[0] != ids[1]:
        fail("model_ids_not_paired")
    outputs = DEFAULT_FILES | cfg.get("output_files", {})
    names = [str(relative_name(n)).casefold() for n in outputs.values()]
    if len(set(names)) != len(names) or any(a.startswith(b + "/") for a in names for b in names if a != b):
        fail("overlapping_output_files")
    return outputs


def prepare(config_path, batch_id, out_dir=None, repo=REPO):
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", batch_id):
        fail("invalid_batch_id")
    roots = separated_roots(repo)
    assets, config = roots["AIRMOSAIC_ASSETS_DIR"], roots["AIRMOSAIC_CONFIG_DIR"]
    raw = Path(config_path)
    if not raw.is_absolute():
        if not str(config_path).replace("\\", "/").startswith("config/examples/"):
            fail("config_outside_allowed_roots")
        raw = repo / raw
    path = checked_path(str(raw))
    example = repo / "config/examples"
    allowed_example = path.is_relative_to(example)
    if not allowed_example and not path.is_relative_to(config):
        fail("config_outside_allowed_roots")
    secure_path(path, allow_git=allowed_example)
    if allowed_example:
        for ancestor in (path.parent, *path.parent.parents):
            if not ancestor.is_relative_to(example):
                break
            if (ancestor / ".git").exists():
                fail("nested_git_in_config_examples")
    if path.suffix.casefold() != ".json":
        fail("config_must_be_json")
    cfg = read_json(path)
    outputs = validate_config(cfg, repo)
    project = secure_path(assets / "results" / cfg["project_id"])
    sides = {}
    for side in ("candidate", "reference"):
        root = expand(cfg[side]["root"], assets)
        if not root.is_relative_to(project) or root == project or not root.is_dir():
            fail("input_outside_project_results")
        sides[side] = root
    if overlap(*sides.values()):
        fail("overlapping_inputs")
    output = expand(out_dir, assets) if out_dir else secure_path(project / batch_id)
    if not output.is_relative_to(project) or output == project or any(overlap(output, r) for r in sides.values()):
        fail("output_overlaps_or_outside_project")
    if output.exists():
        fail("output_must_be_fresh")
    for name in outputs.values():
        artifact(output, name)
    return cfg, sides, output, outputs, assets, path


def manifest_metadata(root, side):
    # Inspect directory metadata only, including unreferenced nested checkouts.
    directory_count = 0
    for directory, children, filenames in os.walk(root, followlinks=False):
        directory_count += 1
        if directory_count > 10000:
            fail("input_directory_limit")
        if ".git" in children or (Path(directory) / ".git").exists():
            fail("nested_git_in_input")
        for child in children + filenames:
            secure_path(Path(directory) / child)
    path = artifact(root, side["manifest"])
    obj = read_json(path)
    files = obj.get("file_sha256", obj)
    if not isinstance(files, dict) or not files or len(files) > MAX_FILES:
        fail("invalid_manifest")
    total = 0
    seen = set()
    for name, sha in files.items():
        target = artifact(root, name)
        alias = name.casefold()
        if alias in seen or name == side["manifest"] or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
            fail("invalid_manifest_entry")
        seen.add(alias)
        if not target.is_file() or target.stat().st_size > MAX_FILE:
            fail("manifest_file_unavailable_or_too_large")
        total += target.stat().st_size
    if total > MAX_TOTAL:
        fail("manifest_total_too_large")
    for model in side["models"]:
        required = [model["predictions"]]
        if "reported_metrics" in model:
            required.append(model["reported_metrics"]["file"])
        if any(name not in files for name in required):
            fail("referenced_file_unsealed")
    return files, digest(path)


def hashes(root, side, files, manifest_hash):
    result = {side["manifest"]: digest(artifact(root, side["manifest"]))}
    if result[side["manifest"]] != manifest_hash:
        fail("manifest_changed")
    for name, expected in files.items():
        result[name] = digest(artifact(root, name))
        if result[name].lower() != expected.lower():
            fail("source_hash_mismatch")
    return result


def predictions(path, model):
    rows = {}
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            if len(header) != len(set(header)) or not header:
                fail("duplicate_or_missing_headers")
            columns = [model[k] for k in ("id_column", "truth_column", "prediction_column")]
            if not all(k in header for k in columns):
                fail("required_column_missing")
            indices = [header.index(k) for k in columns]
            for row in reader:
                if len(rows) >= MAX_ROWS or len(row) != len(header):
                    fail("invalid_csv_shape_or_limit")
                key, truth, pred = (row[i] for i in indices)
                if not key.strip() or key in rows:
                    fail("duplicate_or_empty_id")
                try:
                    truth, pred = float(truth), float(pred)
                except ValueError:
                    fail("non_numeric_prediction")
                if not math.isfinite(truth) or not math.isfinite(pred):
                    fail("nonfinite_prediction")
                rows[key] = (truth, pred)
    except (OSError, UnicodeError, csv.Error):
        fail("invalid_prediction_csv")
    if not rows:
        fail("empty_prediction_csv")
    return rows


def metrics(rows):
    pairs = list(rows)
    n = len(pairs)
    if not n:
        return {"n": 0, "rmse": None, "mae": None, "r_squared": None,
                "pearson_r_squared": None, "adjusted_calibration_r_squared": None}
    y, p = zip(*pairs)
    try:
        mean_y, mean_p = math.fsum(y) / n, math.fsum(p) / n
        sse = math.fsum((a - b) ** 2 for a, b in pairs)
        sst = math.fsum((a - mean_y) ** 2 for a in y)
        spp = math.fsum((b - mean_p) ** 2 for b in p)
        cov = math.fsum((a - mean_y) * (b - mean_p) for a, b in pairs)
        corr2 = max(0.0, min(1.0, cov * cov / sst / spp)) if sst > 0 and spp > 0 else None
        result = {"n": n, "rmse": math.sqrt(sse / n),
                  "mae": math.fsum(abs(a - b) for a, b in pairs) / n,
                  "r_squared": 1 - sse / sst if sst > 0 else None,
                  "pearson_r_squared": corr2,
                  "adjusted_calibration_r_squared": 1 - (1 - corr2) * (n - 1) / (n - 2)
                  if corr2 is not None and n > 2 else None}
    except (OverflowError, ValueError, ZeroDivisionError):
        fail("metric_numeric_overflow")
    if any(isinstance(v, float) and not math.isfinite(v) for v in result.values()):
        fail("metric_numeric_overflow")
    return result


def pointer(obj, value):
    try:
        for token in value.split("/")[1:]:
            token = token.replace("~1", "/").replace("~0", "~")
            obj = obj[int(token)] if isinstance(obj, list) else obj[token]
        if isinstance(obj, bool) or not isinstance(obj, (int, float)) or not math.isfinite(obj):
            fail("invalid_reported_metric")
        return obj
    except (KeyError, IndexError, ValueError, TypeError):
        fail("reported_metric_pointer_unavailable")


def reported_checks(root, model, computed, tolerance):
    if "reported_metrics" not in model:
        return {"status": "unavailable", "checks": {}}
    spec = model["reported_metrics"]
    obj = read_json(artifact(root, spec["file"]))
    checks = {}
    for name, ptr in spec["pointers"].items():
        value = pointer(obj, ptr)
        actual = computed[name]
        checks[name] = {"reported": value, "recomputed": actual,
                        "passed": actual is not None and math.isclose(actual, value,
                            rel_tol=tolerance["metric_relative"], abs_tol=tolerance["metric_abs"])}
    return {"status": "passed" if all(c["passed"] for c in checks.values()) else "failed", "checks": checks}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def run(config_path, batch_id, out_dir=None, execute=False, repo=REPO):
    cfg, sides, output, names, assets, config_path = prepare(config_path, batch_id, out_dir, repo)
    paths = {key: artifact(output, name) for key, name in names.items()}
    stages = []
    created = False
    before = None

    def state(stage, **extra):
        stages.append({"stage": stage, "timestamp_utc": datetime.now(timezone.utc).isoformat()})
        if created:
            write_json(paths["state"], {"status": stage, "stages": stages,
                       "scientific_review": "pending_human_review", **extra})

    try:
        if execute:
            secure_path(output).mkdir(parents=True, exist_ok=False)
            created = True
        state("preflight")
        manifests = {side: manifest_metadata(root, cfg[side]) for side, root in sides.items()}
        audit_path = None
        if "audit_matrix" in cfg:
            value = cfg["audit_matrix"]["path"]
            audit_path = expand(value, assets) if value.startswith("${") or Path(value).is_absolute() else artifact(assets, value)
            project = secure_path(assets / "results" / cfg["project_id"])
            if not audit_path.is_relative_to(project) or audit_path.suffix.lower() != ".json" or not audit_path.is_file():
                fail("invalid_audit_matrix_path")
            for side, root in sides.items():
                if audit_path.is_relative_to(root):
                    if audit_path.relative_to(root).as_posix() not in manifests[side][0]:
                        fail("audit_matrix_unsealed")
            if audit_path.is_relative_to(output):
                fail("audit_matrix_overlaps_output")
        if not execute:
            return {"status": "preflight_passed", "model_count": len(cfg["candidate"]["models"]),
                    "prediction_rows_read": 0, "scientific_review": "pending_human_review"}
        before = {side: hashes(root, cfg[side], *manifests[side]) for side, root in sides.items()}
        write_json(paths["source_hashes"], {"before": before, "after": None, "sources_unchanged": None})
        config_hash = digest(config_path)
        audit_hash = digest(audit_path) if audit_path else None
        if audit_path:
            read_json(audit_path)
        state("sources_verified")
        normalized, paired, differences = [], [], []
        recomputed, comparisons = {}, {}
        tolerance = {"truth_abs": 1e-10, "metric_abs": 1e-9, "metric_relative": 1e-9} | cfg.get("tolerances", {})
        reference = {m["id"]: m for m in cfg["reference"]["models"]}
        all_data = {}
        # Read and align all cohorts before computing any paired metrics.
        for cm in cfg["candidate"]["models"]:
            mid = cm["id"]
            rm = reference[mid]
            c = predictions(artifact(sides["candidate"], cm["predictions"]), cm)
            r = predictions(artifact(sides["reference"], rm["predictions"]), rm)
            common = sorted(c.keys() & r.keys())
            mismatched = [key for key in common if abs(c[key][0] - r[key][0]) > tolerance["truth_abs"]]
            if mismatched:
                write_json(paths["comparison"], {"status": "truth_mismatch", "mismatched_count": len(mismatched),
                           "model_id": mid, "mismatched_ids": mismatched,
                           "paired_metrics_available": False, "scientific_review": "pending_human_review"})
                fail("truth_mismatch")
            all_data[mid] = (cm, rm, c, r, common)
        state("cohorts_aligned")
        for mid, (cm, rm, c, r, common) in all_data.items():
            recomputed[mid] = {}
            for side, model, rows in (("candidate", cm, c), ("reference", rm, r)):
                own = metrics(rows.values())
                recomputed[mid][side] = {"own_cohort": own, "common_cohort": metrics(rows[key] for key in common),
                    "reported_metrics": reported_checks(sides[side], model, own, tolerance)}
                normalized.extend((side, mid, key, *values) for key, values in sorted(rows.items()))
            for key in common:
                paired.append((mid, key, c[key][0], c[key][1], r[key][1], c[key][1] - r[key][1]))
            for side, keys in (("candidate_only", sorted(c.keys() - r.keys())), ("reference_only", sorted(r.keys() - c.keys()))):
                differences.extend((mid, side, key) for key in keys)
            comparisons[mid] = {"candidate_count": len(c), "reference_count": len(r), "common_count": len(common),
                "candidate_only_count": len(c.keys() - r.keys()), "reference_only_count": len(r.keys() - c.keys()),
                "cohort_complete": c.keys() == r.keys(), "paired_metrics_available": bool(common)}
            comparisons[mid]["paired_prediction_delta"] = {
                "mean": math.fsum(c[k][1] - r[k][1] for k in common) / len(common) if common else None,
                "max_absolute": max((abs(c[k][1] - r[k][1]) for k in common), default=None),
                "rmse": metrics((c[k][1], r[k][1]) for k in common)["rmse"],
            }
            comparisons[mid]["common_cohort_rmse_gain_reference_minus_candidate"] = (
                recomputed[mid]["reference"]["common_cohort"]["rmse"] - recomputed[mid]["candidate"]["common_cohort"]["rmse"]
                if common else None)
        state("metrics_recomputed")
        after = {side: hashes(root, cfg[side], *manifests[side]) for side, root in sides.items()}
        if before != after or digest(config_path) != config_hash or (audit_path and digest(audit_path) != audit_hash):
            fail("source_changed_during_execution")
        write_json(paths["source_hashes"], {"before": before, "after": after, "sources_unchanged": True,
                   "task_config_sha256": config_hash, "audit_matrix_sha256": audit_hash})
        write_csv(paths["normalized"], ["side", "model_id", "sample_id", "truth", "prediction"], normalized)
        write_csv(paths["paired"], ["model_id", "sample_id", "truth", "candidate", "reference", "candidate_minus_reference"], paired)
        write_csv(paths["cohort_differences"], ["model_id", "membership", "sample_id"], differences)
        write_json(paths["metrics"], recomputed)
        assertions = [entry[side]["reported_metrics"]["status"] for entry in recomputed.values() for side in sides]
        comparison = {"execution_status": "completed", "target": cfg["target"], "reported_metric_assertions": "failed" if "failed" in assertions else
            ("passed" if all(s == "passed" for s in assertions) else "unavailable_or_partial"),
            "models": comparisons, "prediction_origins": {s: cfg[s]["prediction_origin"] for s in sides},
            "audit_matrix": "agent_supplied_not_automatically_audited" if audit_path else "unavailable",
            "saved_model_provenance": "not_established_by_prediction_or_source_audit",
            "scientific_review": "pending_human_review"}
        write_json(paths["comparison"], comparison)
        report = ("# Existing prediction comparison\n\n"
                  "Execution completed; scientific approval remains pending human review.\n\n"
                  f"Models: {len(comparisons)}. Common model/sample pairs: {len(paired)}. "
                  f"Unmatched model/sample pairs: {len(differences)}.\n\n"
                  f"Reported-metric assertions: {comparison['reported_metric_assertions']}.\n\n"
                  "RMSE, MAE and out-of-sample R² = 1 − SSE/SST are recomputed on each own cohort and the common-ID subset. "
                  "Constant-truth R² is unavailable. Squared Pearson correlation and adjusted calibration R² "
                  "(intercept plus one prediction regressor, n > 2) are separate descriptive quantities.\n\n"
                  "Common-ID truths passed the declared absolute tolerance. Unmatched IDs are retained in the "
                  "cohort-differences artifact; an empty intersection has no paired metrics. RMSE gain is reference "
                  "minus candidate on common IDs; a positive value indicates smaller candidate error on that subset.\n\n"
                  "A supplied audit matrix is agent-authored evidence, not an automatic code audit. "
                  "Prediction agreement or source review alone does not prove saved-model provenance or scientific validity.\n")
        report_zh = ("# 已有预测比较\n\n执行已完成；科学有效性仍待人工审核。\n\n"
                     f"模型数：{len(comparisons)}。共同模型/样本对：{len(paired)}。非共同模型/样本对：{len(differences)}。\n\n"
                     f"已报告指标断言：{comparison['reported_metric_assertions']}。\n\n"
                     "分别在各自样本与共同 ID 子集重算 RMSE、MAE 与样本外 R² = 1 − SSE/SST。"
                     "常数真值的 R² 不可用。相关系数平方与校准回归调整 R²（含截距、一个预测变量、n > 2）单独报告。\n\n"
                     "共同 ID 的真值通过声明的绝对容差检查。非共同 ID 保留在样本差异表中；无交集时无配对指标。"
                     "RMSE 改善为共同 ID 上参考值减候选值；正值仅说明候选在该子集误差较小。\n\n"
                     "审计矩阵是代理提供的证据，不是自动代码审计；预测一致或源码审查不能单独证明已保存模型来源或科学有效性。\n")
        paths["report"].parent.mkdir(parents=True, exist_ok=True)
        detail = "\n## Numeric checks\n\n```json\n" + json.dumps({"models": comparisons, "recomputed": recomputed}, indent=2, ensure_ascii=False) + "\n```\n"
        paths["report"].write_text(report + detail, encoding="utf-8")
        paths["report_zh"].parent.mkdir(parents=True, exist_ok=True)
        paths["report_zh"].write_text(report_zh +
             detail.replace("## Numeric checks", "## 数值检查"), encoding="utf-8")
        write_json(paths["artifacts"], {"files": names, "scientific_review": "pending_human_review"})
        state("completed", execution_status="completed", reported_metric_assertions=comparison["reported_metric_assertions"])
        seal = {name: digest(paths[key]) for key, name in names.items() if key != "output_sha256"}
        write_json(paths["output_sha256"], seal)
        return {"status": "completed", "model_count": len(comparisons), "paired_row_count": len(paired),
                "unmatched_row_count": len(differences), "reported_metric_assertions": comparison["reported_metric_assertions"]}
    except (ToolExecutionError, OSError, ValueError, RecursionError) as error:
        code = str(error) if isinstance(error, ToolExecutionError) else "execution_io_or_data_error"
        if created:
            if before is not None:
                try:
                    post = {side: hashes(root, cfg[side], *manifests[side]) for side, root in sides.items()}
                    write_json(paths["source_hashes"], {"before": before, "after": post, "sources_unchanged": before == post})
                except (ToolExecutionError, OSError, ValueError):
                    write_json(paths["source_hashes"], {"before": before, "after": None,
                               "sources_unchanged": False, "post_verification_status": "failed"})
            state("failed", error_code=code)
        raise ToolExecutionError(code) from None


def main():
    class SanitizedParser(argparse.ArgumentParser):
        def error(self, message):
            self.exit(2, '{"status":"invalid_arguments"}\n')
    parser = SanitizedParser(description=__doc__)
    parser.add_argument("--task-config", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--out-dir")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.task_config, args.batch_id, args.out_dir, args.execute)))
    except (ToolExecutionError, OSError, ValueError):
        print(json.dumps({"status": "failed"}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
