"""Create two tiny sealed synthetic prediction snapshots in external assets."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re

from compare_existing import REPO, digest, secure_path, separated_roots


def create(fixture_id: str, execute: bool = False):
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", fixture_id):
        raise ValueError("invalid_fixture_id")
    assets = separated_roots(REPO)["AIRMOSAIC_ASSETS_DIR"]
    root = secure_path(assets / "results" / "model_reproduction_demo" / fixture_id)
    if root.exists():
        raise ValueError("fixture_must_be_fresh")
    if not execute:
        return {"status": "preflight_passed", "synthetic_rows_per_side": 5}
    root.mkdir(parents=True, exist_ok=False)
    for side, offset in (("candidate", 0), ("reference", 1)):
        folder = root / side
        folder.mkdir()
        rows = [(f"sample_{i}", i, i + offset) for i in range(1, 6)]
        if side == "reference":
            rows.reverse()  # Deliberately different file order; compare by key.
        with (folder / "predictions.csv").open("x", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["sample_id", "truth", "response"])
            writer.writerows(rows)
        with (folder / "metrics.json").open("x", encoding="utf-8") as stream:
            json.dump({"forest": {"rmse": offset, "mae": offset, "r_squared": 1 - offset / 2}}, stream, indent=2)
        with (folder / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump({name: digest(folder / name) for name in ("predictions.csv", "metrics.json")}, stream, indent=2)
    return {"status": "created", "synthetic_rows_per_side": 5}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--fixture-id", default="synthetic_v1")
    parser.add_argument("--execute", action="store_true")
    options = parser.parse_args()
    try:
        print(json.dumps(create(options.fixture_id, options.execute)))
    except Exception:
        print(json.dumps({"status": "failed", "error": "synthetic_fixture_rejected"}))
        raise SystemExit(1)
