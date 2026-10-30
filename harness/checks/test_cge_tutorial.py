"""Exercise the synthetic CGE equilibrium and input rejection boundaries."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


pytest.importorskip("numpy")
pytest.importorskip("scipy")

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "assets/data/01_socioeconomic_natural_change/SyntheticCGE/v1"
SCRIPT = ROOT / "skills/model/01_socioeconomic_natural_change/cge/scripts/run_toy_cge.py"


def run_model(input_dir: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), "--input-dir", str(input_dir),
                           "--out-dir", str(output_dir)], cwd=ROOT, capture_output=True, text=True)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_synthetic_benchmark_and_shock_solve(tmp_path: Path) -> None:
    manifest = json.loads((ROOT / "assets/toy-manifest.json").read_text(encoding="utf-8"))
    for file in INPUT.glob("*.csv"):
        relative = file.relative_to(ROOT / "assets").as_posix()
        assert hashlib.sha256(file.read_bytes()).hexdigest() == manifest["files"][relative]

    output = tmp_path / "result"
    completed = run_model(INPUT, output)
    assert completed.returncode == 0, completed.stderr
    receipt = json.loads((output / "validation.json").read_text(encoding="utf-8"))
    assert receipt["baseline_reproduced"] is True
    rows = {(r["scenario"], r["sector"]): r for r in csv_rows(output / "equilibrium.csv")}
    for sector in ("food", "manufacturing"):
        baseline = rows[("baseline", sector)]
        assert float(baseline["output_price_index"]) == pytest.approx(1, abs=1e-9)
        assert float(baseline["gross_output_base_quantity"]) == pytest.approx(100, abs=1e-9)
    food = rows[("food_productivity_reduction", "food")]
    manufacturing = rows[("food_productivity_reduction", "manufacturing")]
    assert float(food["output_price_index"]) > 1.08
    assert float(food["gross_output_base_quantity"]) < 95
    assert float(manufacturing["output_price_index"]) > 1
    summary = {r["scenario"]: r for r in csv_rows(output / "summary.csv")}
    assert float(summary["baseline"]["total_direct_emissions_kg"]) == pytest.approx(50)
    assert float(summary["food_productivity_reduction"]["total_direct_emissions_kg"]) < 50
    assert abs(float(summary["food_productivity_reduction"]["capital_market_residual"])) < 1e-8


def test_unbalanced_sam_fails_before_output(tmp_path: Path) -> None:
    source = tmp_path / "bad_input"
    source.mkdir()
    for file in INPUT.glob("*.csv"):
        shutil.copyfile(file, source / file.name)
    sam = source / "sam.csv"
    sam.write_text(sam.read_text(encoding="utf-8").replace("COM_food,10,20,", "COM_food,11,20,"), encoding="utf-8")
    output = tmp_path / "result"
    completed = run_model(source, output)
    assert completed.returncode != 0
    assert "unbalanced" in completed.stderr
    assert not output.exists()


def test_existing_output_is_preserved(tmp_path: Path) -> None:
    output = tmp_path / "result"
    output.mkdir()
    marker = output / "marker.txt"
    marker.write_text("preserve", encoding="utf-8")
    completed = run_model(INPUT, output)
    assert completed.returncode != 0
    assert marker.read_text(encoding="utf-8") == "preserve"
