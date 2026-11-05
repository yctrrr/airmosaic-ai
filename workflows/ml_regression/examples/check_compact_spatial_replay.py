"""Refit a compact synthetic example from its frozen inputs, without network.

No fixture regeneration: reconstruct stored source stencils, repeat skill
handoffs, refit the predeclared families and independently check test metrics.
Use a fresh external output directory; original inputs/results remain intact.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import importlib.util
import importlib.metadata
import json
import shutil
import sys

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, source, out = args.repo.resolve(), args.source.resolve(), args.out.resolve()
    if out.exists() or any((p/".git").exists() for p in (out, *out.parents)):
        raise ValueError("fresh_external_result_directory_required")
    manifest = json.loads((source/"delivery-sha256.json").read_text(encoding="utf-8"))
    for relative, expected in manifest.items():
        path = (source/relative.replace("\\", "/")).resolve()
        if not path.is_relative_to(source) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("source_delivery_hash_mismatch")
    plan = json.loads((source/"gen_script/plan.json").read_text(encoding="utf-8"))
    if plan["data_kind"] != "synthetic_engineering_fixture" or plan["station_count"] != 8:
        raise ValueError("this_example_accepts_its_fixed_synthetic_fixture_only")
    environment = json.loads((source/"gen_script/environment.json").read_text(encoding="utf-8"))
    if sys.version.split()[0] != environment["python"] or any(
        importlib.metadata.version(name) != version for name, version in environment["packages"].items()
    ):
        raise ValueError("frozen_replay_environment_mismatch")
    modules = {}
    for number, (relative, expected) in enumerate(json.loads(
        (source/"gen_script/dependencies.json").read_text(encoding="utf-8")
    ).items()):
        path = repo/relative
        if not path.resolve().is_relative_to(repo) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("skill_source_hash_mismatch")
        spec = importlib.util.spec_from_file_location(f"compact_replay_{number}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[path.stem] = module
    out.mkdir(parents=True)
    (out/"gen_script").mkdir()
    shutil.copyfile(Path(__file__), out/"gen_script/check.py")

    def event(action, **details):
        time = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
        with (out/"events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"time": time, "action": action, **details})+"\n")

    event("source_verified", files=len(manifest), network_used=False)
    space, grid, obs, ml = (modules[name] for name in
        ("bilinear_helpers", "grid_daily", "prepare_hourly", "grouped_tuning"))
    inputs = source/"inputs"
    stations = pd.read_csv(inputs/"stations.synthetic.csv", dtype={"station_id": str})
    saved = pd.read_csv(inputs/"prepared-daily.synthetic.csv.gz", dtype={"station_id": str})
    dates = sorted(saved.date_local.unique().tolist())
    features, target = plan["features"], plan["target"]
    points = stations[["longitude", "latitude"]].to_numpy()
    ids = stations.station_id.tolist()
    rebuilt = pd.DataFrame({"date_local": np.repeat(dates, len(ids)), "station_id": ids*len(dates)})
    with np.load(inputs/"source-stencils.synthetic.npz", allow_pickle=False) as packed:
        x, y, ax, ay = (packed[key] for key in ("x", "y", "aod_x", "aod_y"))
        weights = space.bilinear_weights(x, y, points, ids, "EPSG:4326", "EPSG:4326")
        aweights = space.bilinear_weights(ax, ay, points, ids, "EPSG:4326", "EPSG:4326")
        for actual, name in ((weights, "meteorology-weights.csv"), (aweights, "aod-weights.csv")):
            pd.testing.assert_frame_equal(actual, pd.read_csv(inputs/name), rtol=1e-12, atol=1e-12)
        grid_points = np.array([(gx, gy) for gy in ay for gx in ax])
        grid_ids = [f"G{i}" for i in range(len(grid_points))]
        grid_input = pd.DataFrame({"date_local": np.repeat(dates, len(grid_ids)), "grid_id": grid_ids*len(dates)})
        gw = space.bilinear_weights(x, y, grid_points, grid_ids, "EPSG:4326", "EPSG:4326")
        gaw = space.bilinear_weights(ax, ay, grid_points, grid_ids, "EPSG:4326", "EPSG:4326")
        for name in features:
            is_aod = name == "aod550"
            nodes = packed["aod_nodes" if is_aod else "meteorology_nodes"]
            times = packed["aod_utc" if is_aod else "hourly_utc"]
            shape = (len(times), len(ay if is_aod else y), len(ax if is_aod else x))
            field = np.full(shape, np.nan, dtype=packed[name].dtype)
            field[:, nodes[:, 0]-1, nodes[:, 1]-1] = packed[name]
            daily = grid.daily_grid_mean(field, times, dates, timezone=plan["timezone"],
                sample_interval_hours=3 if is_aod else 1)["values"]
            rebuilt[name] = np.concatenate([space.sample_bilinear(v, aweights if is_aod else weights).value for v in daily])
            grid_input[name] = np.concatenate([space.sample_bilinear(v, gaw if is_aod else gw).value for v in daily])
    event("stencils_replayed", features=features, days=len(dates))
    hourly = pd.read_csv(inputs/"station-hours.synthetic.csv.gz", keep_default_na=False,
        dtype={"station_id": str, "date_raw": str, "hour_raw": str, "value_raw": str})
    _, daily = obs.prepare_daily(hourly, {"status": "reviewed", "timezone": plan["timezone"],
        "hour_label": "start", "evidence": "known_synthetic_generator"}, plan["min_observed_hours"])
    rebuilt = rebuilt.merge(daily, on=["station_id", "date_local"], validate="one_to_one").rename(columns={"pm25_mean": target})
    split = pd.read_csv(inputs/"split-and-folds.csv.gz", dtype={"station_id": str})
    rebuilt = rebuilt.merge(split, on=["station_id", "date_local"], validate="one_to_one")
    pd.testing.assert_frame_equal(rebuilt[saved.columns], saved, rtol=1e-12, atol=1e-10)
    assert len(dates) == 366 and "2024-02-29" in dates and len(rebuilt) == 8*366
    event("prepared_table_reproduced", records=len(rebuilt), incomplete_days=int(rebuilt[target].isna().sum()))
    valid = rebuilt[rebuilt[target].notna()]
    development, test = (valid[valid.split == name].copy() for name in ("development", "test"))
    expected_metrics = json.loads((source/"metrics.json").read_text(encoding="utf-8"))
    selections = json.loads((source/"selection.json").read_text(encoding="utf-8"))
    settings = json.loads((source/"gen_script/search-settings.json").read_text(encoding="utf-8"))
    expected_predictions = pd.read_csv(source/"test-predictions.csv.gz", dtype={"station_id": str})
    expected_grid = pd.read_csv(source/"grid-predictions.synthetic.csv.gz")
    metrics = {}
    for learner in plan["families_frozen_before_test"]:
        event("model_refit_started", learner=learner)
        result = ml.fit_grouped_regression(development, test, features=features, target=target,
            group_column="station_id", fold_id=development.fold_id.astype(int).tolist(), learner=learner,
            seed=selections[learner]["seed"], **settings[learner])
        assert result["selection"]["parameters"] == selections[learner]["parameters"]
        assert result["selection"]["test_used_for_selection"] is False
        expected = expected_predictions[expected_predictions.learner == learner]
        np.testing.assert_allclose(result["predictions"].observed, expected.observed, rtol=0, atol=1e-10)
        np.testing.assert_allclose(result["predictions"].predicted, expected.predicted, rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(result["estimator"].predict(grid_input[features].to_numpy()),
            expected_grid[expected_grid.learner == learner].predicted, rtol=1e-10, atol=1e-10)
        # Independent checks use exported observed/predicted values, not skill metrics.
        observed = expected.observed.to_numpy()
        residual = observed-expected.predicted.to_numpy()
        independent = {"rmse": float(np.sqrt(np.mean(residual**2))), "mae": float(np.abs(residual).mean()),
            "r2": float(1-(residual**2).sum()/((observed-observed.mean())**2).sum())}
        for name, value in independent.items():
            np.testing.assert_allclose(value, expected_metrics[learner][name], rtol=1e-10, atol=1e-10)
            np.testing.assert_allclose(value, result["test_metrics"][name], rtol=1e-10, atol=1e-10)
        metrics[learner] = independent
        event("model_refit_verified", learner=learner, test_records=len(test))
    receipt = {"status": "compact_replay_passed", "data_kind": plan["data_kind"], "network_used": False,
        "source_manifest_sha256": hashlib.sha256((source/"delivery-sha256.json").read_bytes()).hexdigest(),
        "source_files_verified": len(manifest), "station_count": len(ids), "days": len(dates),
        "prepared_rows": len(rebuilt), "development_rows": len(development), "test_rows": len(test),
        "checks": ["source_and_skill_hashes", "frozen_environment", "weights", "stencil_to_daily_features",
            "hourly_completeness", "saved_groups_and_folds", "selected_parameters", "test_and_grid_predictions",
            "independent_rmse_mae_r2"], "metrics": metrics}
    (out/"verification.json").write_text(json.dumps(receipt, indent=2, allow_nan=False), encoding="utf-8")
    (out/"retrospective.md").write_text("# Retrospective\n\nFrozen synthetic inputs reproduced preparation, parameters, test metrics and grid predictions without network or fixture regeneration. This verifies engineering reproducibility, not real-station predictive performance.\n", encoding="utf-8")
    (out/"retrospective_ZH.md").write_text("# 回顾性摘要\n\n仅用保存的合成输入重现了整理表、参数、测试指标和网格预测，未联网或重新生成输入。这验证工程可复现性，不表示真实站点预测精度。\n", encoding="utf-8")
    event("compact_replay_completed", status="passed")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
