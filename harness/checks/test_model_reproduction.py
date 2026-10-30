"""Synthetic-only behavioral checks for sealed existing prediction comparison."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "skills/model/shared/model_reproduction/scripts/compare_existing.py"
spec = importlib.util.spec_from_file_location("compare_existing", SCRIPT)
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)
Error = compare.ToolExecutionError


def write_predictions(root, rows, header=("sample_id", "truth", "model_1")):
    with (root / "predictions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def seal(root):
    files = {p.name: compare.digest(p) for p in root.iterdir() if p.is_file() and p.name != "manifest.json"}
    (root / "manifest.json").write_text(json.dumps({"file_sha256": files}), encoding="utf-8")


@pytest.fixture
def task(tmp_path, monkeypatch):
    roots = {name: tmp_path / name for name in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR")}
    for name, path in roots.items():
        path.mkdir()
        monkeypatch.setenv(name, str(path))
    cfg = {"schema_version": 1, "mode": "compare_existing", "project_id": "synthetic_compare",
           "target": {"name": "Synthetic target", "unit": "unit"}}
    side_roots = {}
    for side in ("candidate", "reference"):
        root = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_compare" / side
        root.mkdir(parents=True)
        side_roots[side] = root
        write_predictions(root, [("a", 1, 1), ("b", 2, 2), ("c", 3, 3)])
        seal(root)
        cfg[side] = {"root": "${AIRMOSAIC_ASSETS_DIR}/results/synthetic_compare/" + side,
            "manifest": "manifest.json", "prediction_origin": "stored_predictions",
            "models": [{"id": "model_1", "predictions": "predictions.csv", "id_column": "sample_id",
                        "truth_column": "truth", "prediction_column": "model_1"}]}
    path = roots["AIRMOSAIC_CONFIG_DIR"] / "task.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return cfg, path, side_roots, roots


def save(task):
    task[1].write_text(json.dumps(task[0]), encoding="utf-8")


def output(task, name="batch"):
    return task[3]["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_compare" / name


def test_known_metric_definitions_are_distinct():
    result = compare.metrics([(1, 2), (2, 4), (3, 6)])
    assert result["rmse"] == pytest.approx((14 / 3) ** 0.5)
    assert result["mae"] == 2
    assert result["r_squared"] == -6
    assert result["pearson_r_squared"] == 1
    assert result["adjusted_calibration_r_squared"] == 1
    assert compare.metrics([(3, 4), (3, 5)])["r_squared"] is None
    assert compare.metrics([])["rmse"] is None


def test_shuffled_ids_align_and_output_is_sealed(task):
    write_predictions(task[2]["reference"], [("c", 3, 3.5), ("a", 1, 1.5), ("b", 2, 2.5)])
    seal(task[2]["reference"])
    result = compare.run(str(task[1]), "batch", execute=True)
    assert result["status"] == "completed"
    assert result["paired_row_count"] == 3
    root = output(task)
    paired = list(csv.DictReader((root / "paired.csv").open(encoding="utf-8")))
    assert [r["sample_id"] for r in paired] == ["a", "b", "c"]
    assert all(float(r["candidate_minus_reference"]) == -0.5 for r in paired)
    checks = json.loads((root / "comparison.json").read_text())
    assert checks["scientific_review"] == "pending_human_review"
    assert checks["reported_metric_assertions"] == "unavailable_or_partial"
    assert checks["models"]["model_1"]["common_cohort_rmse_gain_reference_minus_candidate"] == 0.5
    seal_map = json.loads((root / "output-sha256.json").read_text())
    assert all(compare.digest(root / name) == sha for name, sha in seal_map.items())
    assert (root / "report_ZH.md").is_file()
    with pytest.raises(Error, match="fresh"):
        compare.run(str(task[1]), "batch", execute=True)


@pytest.mark.parametrize("rows, common, unmatched", [
    ([("c", 3, 3), ("d", 4, 4)], 1, 3), ([("d", 4, 4)], 0, 4),
])
def test_common_cohort_and_unmatched_are_explicit(task, rows, common, unmatched):
    write_predictions(task[2]["reference"], rows)
    seal(task[2]["reference"])
    result = compare.run(str(task[1]), "batch", execute=True)
    assert result["paired_row_count"] == common
    assert result["unmatched_row_count"] == unmatched
    recomputed = json.loads((output(task) / "metrics.json").read_text())["model_1"]
    assert recomputed["candidate"]["own_cohort"]["n"] == 3
    assert recomputed["candidate"]["common_cohort"]["n"] == common
    assert len(list(csv.DictReader((output(task) / "cohort-differences.csv").open()))) == unmatched


def test_truth_mismatch_fails_without_paired_metrics(task):
    write_predictions(task[2]["reference"], [("a", 9, 1)])
    seal(task[2]["reference"])
    with pytest.raises(Error, match="truth_mismatch"):
        compare.run(str(task[1]), "batch", execute=True)
    root = output(task)
    assert not (root / "metrics.json").exists()
    assert not (root / "paired.csv").exists()
    diagnostic = json.loads((root / "comparison.json").read_text())
    assert diagnostic["mismatched_ids"] == ["a"]
    state = json.loads((root / "state.json").read_text())
    assert state["status"] == "failed"
    assert str(task[3]["AIRMOSAIC_ASSETS_DIR"]) not in (root / "state.json").read_text()


@pytest.mark.parametrize("rows,header,error", [
    ([("a", 1, 1), ("a", 2, 2)], ("sample_id", "truth", "model_1"), "duplicate_or_empty_id"),
    ([("", 1, 1)], ("sample_id", "truth", "model_1"), "duplicate_or_empty_id"),
    ([("a", "NaN", 1)], ("sample_id", "truth", "model_1"), "nonfinite_prediction"),
    ([("a", 1, "inf")], ("sample_id", "truth", "model_1"), "nonfinite_prediction"),
    ([("a", 1, 1)], ("sample_id", "truth", "truth"), "duplicate_or_missing_headers"),
])
def test_invalid_csv_fails_closed(task, rows, header, error):
    write_predictions(task[2]["candidate"], rows, header)
    seal(task[2]["candidate"])
    with pytest.raises(Error, match=error):
        compare.run(str(task[1]), "batch", execute=True)


def test_dry_run_does_not_parse_rows_or_hash_declared_files(task, monkeypatch):
    (task[2]["candidate"] / "predictions.csv").write_bytes(b"invalid csv rows")
    def never(*args):
        pytest.fail("prediction reader invoked during preflight")
    monkeypatch.setattr(compare, "predictions", never)
    original = compare.digest
    def metadata_only(path):
        assert path.name == "manifest.json"
        return original(path)
    monkeypatch.setattr(compare, "digest", metadata_only)
    assert compare.run(str(task[1]), "batch")["prediction_rows_read"] == 0
    assert not output(task).exists()


def test_hash_mismatch_is_execution_failure(task):
    (task[2]["candidate"] / "predictions.csv").write_text("changed")
    with pytest.raises(Error, match="source_hash_mismatch"):
        compare.run(str(task[1]), "batch", execute=True)
    assert json.loads((output(task) / "state.json").read_text())["status"] == "failed"


def test_failed_metric_assertion_is_distinct_from_execution_success(task):
    root = task[2]["candidate"]
    (root / "metrics.json").write_text('{"rmse": 123}', encoding="utf-8")
    task[0]["candidate"]["models"][0]["reported_metrics"] = {"file": "metrics.json", "pointers": {"rmse": "/rmse"}}
    seal(root)
    save(task)
    result = compare.run(str(task[1]), "batch", execute=True)
    assert result["status"] == "completed"
    assert result["reported_metric_assertions"] == "failed"
    checks = json.loads((output(task) / "metrics.json").read_text())
    assert checks["model_1"]["candidate"]["reported_metrics"]["status"] == "failed"


@pytest.mark.parametrize("name", ["../predictions.csv", "folder\\predictions.csv", "foo:bar", "AUTH/p.csv", ".ssh/p.csv", "a./p.csv"])
def test_invalid_manifest_paths_rejected_without_reading_files(task, name):
    (task[2]["candidate"] / "manifest.json").write_text(json.dumps({name: "a" * 64}))
    with pytest.raises(Error, match="invalid_artifact_path"):
        compare.run(str(task[1]), "batch")


def test_unsealed_prediction_file_rejected(task):
    root = task[2]["candidate"]
    (root / "other.json").write_text("{}")
    (root / "manifest.json").write_text(json.dumps({"other.json": compare.digest(root / "other.json")}))
    with pytest.raises(Error, match="unsealed"):
        compare.run(str(task[1]), "batch")


def test_config_outside_explicit_config_root_rejected(task):
    outside = task[2]["candidate"] / "configuration.json"
    outside.write_text(json.dumps(task[0]))
    with pytest.raises(Error, match="config_outside"):
        compare.run(str(outside), "batch")


@pytest.mark.parametrize("relative", ["unreferenced/.git", "nested/.git"])
def test_nested_git_input_rejected(task, relative):
    (task[2]["candidate"] / relative).mkdir(parents=True)
    with pytest.raises(Error):
        compare.run(str(task[1]), "batch")


def test_symlink_input_rejected(task, tmp_path):
    link = task[2]["candidate"] / "linked"
    try:
        link.symlink_to(task[2]["reference"], target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable on host")
    with pytest.raises(Error):
        compare.run(str(task[1]), "batch")


@pytest.mark.parametrize("change", ["overlap", "other_project", "output_overlap", "output_escape", "alias_outputs", "model_pair"])
def test_boundary_and_pairing_failures(task, change):
    out = None
    if change == "overlap":
        task[0]["reference"]["root"] = task[0]["candidate"]["root"]
    elif change == "other_project":
        task[0]["project_id"] = "another_project"
    elif change == "output_overlap":
        out = str(task[2]["candidate"] / "new")
    elif change == "output_escape":
        out = str(task[3]["AIRMOSAIC_ASSETS_DIR"] / "results/other_project/new")
    elif change == "alias_outputs":
        task[0]["output_files"] = {"state": "Same.json", "metrics": "same.json"}
    elif change == "model_pair":
        task[0]["reference"]["models"][0]["id"] = "different_model"
    save(task)
    with pytest.raises(Error):
        compare.run(str(task[1]), "batch", out_dir=out)


def test_direct_manifest_map_and_custom_flat_names(task):
    for root in task[2].values():
        files = json.loads((root / "manifest.json").read_text())["file_sha256"]
        (root / "manifest.json").write_text(json.dumps(files))
    task[0]["output_files"] = {"metrics": "custom-metrics.json"}
    save(task)
    compare.run(str(task[1]), "batch", execute=True)
    assert (output(task) / "custom-metrics.json").is_file()


def test_audit_matrix_in_side_must_be_sealed(task):
    root = task[2]["candidate"]
    (root / "audit.json").write_text("{}")
    task[0]["audit_matrix"] = {"path": "results/synthetic_compare/candidate/audit.json"}
    save(task)
    with pytest.raises(Error, match="audit_matrix_unsealed"):
        compare.run(str(task[1]), "batch")
    seal(root)
    compare.run(str(task[1]), "batch", execute=True)
    obj = json.loads((output(task) / "comparison.json").read_text())
    assert obj["audit_matrix"] == "agent_supplied_not_automatically_audited"


def test_source_mutation_during_execution_is_detected(task, monkeypatch):
    original = compare.predictions
    def mutated(path, model):
        result = original(path, model)
        if path.parent.name == "reference":
            path.write_text("changed during execution")
        return result
    monkeypatch.setattr(compare, "predictions", mutated)
    with pytest.raises(Error, match="source_hash_mismatch"):
        compare.run(str(task[1]), "batch", execute=True)
    assert not (output(task) / "metrics.json").exists()


def test_declared_binary_model_is_hashed_without_deserialization(task):
    root = task[2]["reference"]
    (root / "frozen-model.rds").write_bytes(b"synthetic non-model binary\x00\xff")
    seal(root)
    compare.run(str(task[1]), "batch", execute=True)
    receipt = json.loads((output(task) / "source-hashes.json").read_text())
    assert receipt["before"]["reference"]["frozen-model.rds"] == compare.digest(root / "frozen-model.rds")
    assert receipt["sources_unchanged"]


def test_nested_git_file_and_private_components_are_rejected(task):
    root = task[2]["candidate"]
    nested = root / "nested"
    nested.mkdir()
    (nested / ".git").write_text("gitdir: synthetic")
    with pytest.raises(Error, match="git"):
        compare.run(str(task[1]), "batch")
    (nested / ".git").unlink()
    (nested / "credentials").mkdir()
    with pytest.raises(Error, match="private_path"):
        compare.run(str(task[1]), "batch")


def test_reported_metrics_must_be_manifest_sealed(task):
    task[0]["candidate"]["models"][0]["reported_metrics"] = {"file": "reported.json", "pointers": {"mae": "/mae"}}
    (task[2]["candidate"] / "reported.json").write_text('{"mae": 0}')
    save(task)
    with pytest.raises(Error, match="referenced_file_unsealed"):
        compare.run(str(task[1]), "batch")
