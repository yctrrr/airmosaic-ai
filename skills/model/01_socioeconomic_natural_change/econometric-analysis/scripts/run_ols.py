"""Bounded cross-sectional OLS illustration; coefficients are not causal effects."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[5]


def write_csv(path: Path, fields: list[str], data: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Cross-sectional UTF-8 CSV")
    parser.add_argument("--out-dir", type=Path, required=True, help="Fresh directory outside the repository")
    parser.add_argument("--unit-id", default="unit_id")
    parser.add_argument("--outcome", required=True)
    parser.add_argument("--predictors", nargs="+", required=True)
    args = parser.parse_args()

    input_path = args.input.resolve(strict=True)
    if not input_path.is_file():
        raise ValueError("--input must be a CSV file")
    out_dir = args.out_dir.resolve()
    if out_dir.is_relative_to(REPO_ROOT):
        raise ValueError("Output must be outside the repository checkout")
    if out_dir.exists():
        raise FileExistsError(f"Output directory already exists: {out_dir}")

    selected = [args.unit_id, args.outcome, *args.predictors]
    if any(not name.strip() for name in selected) or len(selected) != len(set(selected)):
        raise ValueError("Unit ID, outcome and predictor names must be nonempty and distinct")
    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV must have a unique header")
        missing = set(selected) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("Input CSV is empty")
    ids = [str(row[args.unit_id]).strip() for row in rows]
    if any(not unit for unit in ids) or len(ids) != len(set(ids)):
        raise ValueError("Cross-sectional unit IDs must be nonempty and unique")

    def values(name: str) -> np.ndarray:
        try:
            result = np.array([float(row[name]) for row in rows], dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name}: all observations must be numeric") from exc
        if not np.isfinite(result).all():
            raise ValueError(f"{name}: all observations must be finite")
        return result

    y = values(args.outcome)
    x = np.column_stack([np.ones(len(rows)), *(values(name) for name in args.predictors)])
    n, k = x.shape
    if n <= k + 1:
        raise ValueError("Need more observations than parameters plus one")
    if np.linalg.matrix_rank(x) != k:
        raise ValueError("Design matrix is rank deficient")
    condition = float(np.linalg.cond(x))
    if condition > 1e10:
        raise ValueError("Design matrix is ill-conditioned; rescale or revise predictors")
    sst = float(((y - y.mean()) ** 2).sum())
    if math.isclose(sst, 0.0, abs_tol=1e-12):
        raise ValueError("Outcome has no variation")

    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    fitted = x @ beta
    residual = y - fitted
    sse = float(residual @ residual)
    inv_xtx = np.linalg.solve(x.T @ x, np.eye(k))
    classical_cov = (sse / (n - k)) * inv_xtx
    hc1_cov = (n / (n - k)) * inv_xtx @ ((x * residual[:, None]).T @ (x * residual[:, None])) @ inv_xtx
    names = ["intercept", *args.predictors]
    coefficient_rows = [
        {
            "term": name,
            "estimate": float(beta[i]),
            "se_classical": float(np.sqrt(max(classical_cov[i, i], 0.0))),
            "se_hc1": float(np.sqrt(max(hc1_cov[i, i], 0.0))),
        }
        for i, name in enumerate(names)
    ]
    prediction_rows = [
        {"unit_id": unit, "observed": float(y[i]), "fitted": float(fitted[i]), "residual": float(residual[i])}
        for i, unit in enumerate(ids)
    ]
    summary = {
        "model": "cross_sectional_ols_with_intercept",
        "interpretation": "descriptive conditional association; no causal effect established",
        "n": n,
        "parameters": k,
        "outcome": args.outcome,
        "predictors": args.predictors,
        "r_squared": 1.0 - sse / sst,
        "residual_sum_squares": sse,
        "design_condition_number": condition,
        "standard_error_scope": "classical assumes homoskedastic independent errors; HC1 permits heteroskedasticity but still assumes independent observations; neither handles clusters, time dependence or design uncertainty",
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
    }
    out_dir.mkdir(parents=True, exist_ok=False)
    write_csv(out_dir / "coefficients.csv", ["term", "estimate", "se_classical", "se_hc1"], coefficient_rows)
    write_csv(out_dir / "fitted.csv", ["unit_id", "observed", "fitted", "residual"], prediction_rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"n": n, "r_squared": summary["r_squared"], "out_dir": str(out_dir)}))


if __name__ == "__main__":
    main()
