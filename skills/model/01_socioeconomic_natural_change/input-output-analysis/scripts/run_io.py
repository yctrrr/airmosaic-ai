"""Small, balanced demand-driven IO calculation; not an MRIO database parser."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[5]


def rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(fields):
            raise ValueError(f"{path.name}: expected columns {fields}")
        result = list(reader)
    if not result:
        raise ValueError(f"{path.name}: empty input")
    return result


def number(value: str, label: str, *, positive: bool = False) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0 or (positive and result == 0):
        raise ValueError(f"{label}: expected a finite {'positive' if positive else 'nonnegative'} number")
    return result


def write_csv(path: Path, fields: list[str], data: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    input_dir = args.input_dir.resolve(strict=True)
    out_dir = args.out_dir.resolve()
    if out_dir.is_relative_to(REPO_ROOT):
        raise ValueError("Output must be outside the repository checkout")
    if out_dir.exists():
        raise FileExistsError(f"Output directory already exists: {out_dir}")

    sector_path = input_dir / "sectors.csv"
    transaction_path = input_dir / "transactions.csv"
    sector_rows = rows(sector_path, ("sector", "output", "final_demand", "direct_emission_intensity"))
    names = [row["sector"].strip() for row in sector_rows]
    if any(not name for name in names) or len(names) != len(set(names)):
        raise ValueError("Sector identifiers must be nonempty and unique")
    x = np.array([number(row["output"], "output", positive=True) for row in sector_rows])
    y = np.array([number(row["final_demand"], "final_demand") for row in sector_rows])
    f = np.array([number(row["direct_emission_intensity"], "direct_emission_intensity") for row in sector_rows])
    z = np.zeros((len(names), len(names)))
    index = {name: i for i, name in enumerate(names)}
    observed: set[tuple[str, str]] = set()
    for row in rows(transaction_path, ("from_sector", "to_sector", "value")):
        pair = (row["from_sector"].strip(), row["to_sector"].strip())
        if pair[0] not in index or pair[1] not in index or pair in observed:
            raise ValueError(f"Unknown or duplicate transaction pair: {pair}")
        observed.add(pair)
        z[index[pair[0]], index[pair[1]]] = number(row["value"], "transaction value")
    if len(observed) != len(names) ** 2:
        raise ValueError("Transactions must include every sector pair, including explicit zeros")
    account_residual = x - z.sum(axis=1) - y
    if not np.allclose(account_residual, 0, atol=1e-8, rtol=1e-10):
        raise ValueError(f"Unbalanced sector accounts; maximum residual {np.max(np.abs(account_residual))}")

    a = z / x[np.newaxis, :]
    system = np.eye(len(names)) - a
    condition = float(np.linalg.cond(system))
    if not math.isfinite(condition) or condition > 1e10:
        raise ValueError("I-A is singular or too ill-conditioned for this demonstration")
    x_model = np.linalg.solve(system, y)
    if not np.allclose(x_model, x, atol=1e-8, rtol=1e-10):
        raise ValueError("Leontief solution does not reproduce the supplied benchmark")
    by_final = np.linalg.solve(system, np.diag(y))
    footprints = f @ by_final
    direct = f * x_model
    if not np.isclose(footprints.sum(), direct.sum(), atol=1e-8, rtol=1e-10):
        raise ValueError("Footprint and direct-emission totals do not close")

    out_dir.mkdir(parents=True)
    write_csv(out_dir / "coefficients.csv", ["from_sector", "to_sector", "coefficient"], [
        {"from_sector": names[i], "to_sector": names[j], "coefficient": float(a[i, j])}
        for i in range(len(names)) for j in range(len(names))
    ])
    write_csv(out_dir / "sector_output.csv", ["sector", "observed_output", "model_output", "direct_emissions_kg_co2"], [
        {"sector": name, "observed_output": float(x[i]), "model_output": float(x_model[i]),
         "direct_emissions_kg_co2": float(direct[i])} for i, name in enumerate(names)
    ])
    write_csv(out_dir / "final_demand_footprint.csv", ["final_demand_sector", "final_demand", "footprint_kg_co2"], [
        {"final_demand_sector": name, "final_demand": float(y[i]), "footprint_kg_co2": float(footprints[i])}
        for i, name in enumerate(names)
    ])
    summary = {
        "method": "fixed_coefficient_demand_driven_io",
        "output_unit": "currency_unit", "intensity_unit": "kg_co2/currency_unit",
        "emission_unit": "kg_co2", "total_direct_emissions_kg_co2": float(direct.sum()),
        "total_final_demand_footprint_kg_co2": float(footprints.sum()),
        "max_account_residual": float(np.max(np.abs(account_residual))), "condition_number": condition,
        "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (sector_path, transaction_path)},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total_kg_co2": summary["total_final_demand_footprint_kg_co2"], "sectors": len(names)}))


if __name__ == "__main__":
    main()
