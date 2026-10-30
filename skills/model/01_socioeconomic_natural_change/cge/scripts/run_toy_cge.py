"""Solve a synthetic two-factor, one-household CGE from a balanced SAM."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import root


REPO_ROOT = Path(__file__).resolve().parents[5]
LABOR = "FACTOR_LABOR"
CAPITAL = "FACTOR_CAPITAL"
HOUSEHOLD = "HOUSEHOLD"


def read_csv(path: Path, expected: list[str] | None = None) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        names = reader.fieldnames
        if names is None or (expected is not None and names != expected):
            raise ValueError(f"{path.name}: invalid header; expected {expected}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name}: no records")
    return names, rows


def number(value: str, label: str, *, strictly_positive: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}: expected a number") from exc
    if not math.isfinite(result) or result < 0 or (strictly_positive and result == 0):
        raise ValueError(f"{label}: expected a finite {'positive' if strictly_positive else 'nonnegative'} number")
    return result


def read_sam(path: Path) -> tuple[list[str], np.ndarray, dict[str, object]]:
    header, rows = read_csv(path)
    if header[0] != "account" or len(header) != len(set(header)) or len(header) < 6:
        raise ValueError("sam.csv: account header must contain unique accounts")
    accounts = header[1:]
    sectors = [name[4:] for name in accounts if name.startswith("ACT_")]
    if len(sectors) < 2 or any(not s or f"COM_{s}" not in accounts for s in sectors):
        raise ValueError("sam.csv: require at least two matched ACT_/COM_ sectors")
    if set(accounts) != {*(f"ACT_{s}" for s in sectors), *(f"COM_{s}" for s in sectors), LABOR, CAPITAL, HOUSEHOLD}:
        raise ValueError("sam.csv: this tutorial supports activities, matching goods, two factors and one household only")
    if [row["account"] for row in rows] != accounts:
        raise ValueError("sam.csv: row accounts must match column accounts in the same order")
    sam = np.array([[number(row[name], f"SAM {row['account']}/{name}") for name in accounts] for row in rows])
    residual = sam.sum(axis=1) - sam.sum(axis=0)
    if not np.allclose(residual, 0, atol=1e-9, rtol=1e-11):
        raise ValueError(f"sam.csv: accounts are unbalanced; max residual {np.max(np.abs(residual))}")
    idx = {name: i for i, name in enumerate(accounts)}
    allowed = np.zeros_like(sam, dtype=bool)
    for s in sectors:
        allowed[idx[f"ACT_{s}"], idx[f"COM_{s}"]] = True
    for s in sectors:
        j = idx[f"ACT_{s}"]
        for good in sectors:
            allowed[idx[f"COM_{good}"], j] = True
        allowed[idx[LABOR], j] = True
        allowed[idx[CAPITAL], j] = True
        allowed[idx[f"COM_{s}"], idx[HOUSEHOLD]] = True
    allowed[idx[HOUSEHOLD], idx[LABOR]] = True
    allowed[idx[HOUSEHOLD], idx[CAPITAL]] = True
    if np.any(sam[~allowed] > 1e-12):
        raise ValueError("sam.csv: unsupported transaction outside the tutorial's account structure")
    n = len(sectors)
    x = np.array([sam[idx[f"ACT_{s}"], idx[f"COM_{s}"]] for s in sectors])
    z = np.array([[sam[idx[f"COM_{i}"], idx[f"ACT_{j}"]] for j in sectors] for i in sectors])
    labor = np.array([sam[idx[LABOR], idx[f"ACT_{s}"]] for s in sectors])
    capital = np.array([sam[idx[CAPITAL], idx[f"ACT_{s}"]] for s in sectors])
    consumption = np.array([sam[idx[f"COM_{s}"], idx[HOUSEHOLD]] for s in sectors])
    endowment = np.array([sam[idx[HOUSEHOLD], idx[LABOR]], sam[idx[HOUSEHOLD], idx[CAPITAL]]])
    if np.any(x <= 0) or np.any(labor <= 0) or np.any(capital <= 0) or np.any(consumption <= 0):
        raise ValueError("sam.csv: output, both factors and household consumption must be positive in each sector")
    if not np.allclose(np.array([labor.sum(), capital.sum()]), endowment, atol=1e-9):
        raise ValueError("sam.csv: household factor income does not match factor payments")
    a = z / x[np.newaxis, :]
    value_added_share = (labor + capital) / x
    if not np.allclose(a.sum(axis=0) + value_added_share, 1, atol=1e-10):
        raise ValueError("sam.csv: production costs do not equal output")
    if not np.allclose(z.sum(axis=1) + consumption, x, atol=1e-9):
        raise ValueError("sam.csv: commodity sales do not equal output")
    alpha = labor / (labor + capital)
    beta = consumption / consumption.sum()
    return sectors, sam, {"x": x, "a": a, "v": value_added_share, "alpha": alpha,
                          "beta": beta, "endowment": endowment, "sam_residual": residual}


def read_scenarios(path: Path, sectors: list[str]) -> dict[str, np.ndarray]:
    _, rows = read_csv(path, ["scenario", "sector", "tfp_multiplier"])
    grouped: dict[str, dict[str, float]] = {}
    for row in rows:
        scenario, sector = row["scenario"].strip(), row["sector"].strip()
        if not scenario or sector not in sectors or sector in grouped.setdefault(scenario, {}):
            raise ValueError("scenarios.csv: empty scenario, unknown sector or duplicate pair")
        grouped[scenario][sector] = number(row["tfp_multiplier"], "tfp_multiplier", strictly_positive=True)
    if "baseline" not in grouped:
        raise ValueError("scenarios.csv: a zero-shock baseline is required")
    if any(set(record) != set(sectors) for record in grouped.values()):
        raise ValueError("scenarios.csv: every scenario must include every sector")
    if any(abs(value - 1) > 1e-12 for value in grouped["baseline"].values()):
        raise ValueError("scenarios.csv: baseline TFP must equal 1 in every sector")
    return {name: np.array([record[s] for s in sectors]) for name, record in grouped.items()}


def read_satellite(path: Path, sectors: list[str]) -> np.ndarray:
    _, rows = read_csv(path, ["sector", "emission_kg_per_output_unit"])
    if len(rows) != len(sectors) or {row["sector"] for row in rows} != set(sectors):
        raise ValueError("satellite.csv: require one distinct emission coefficient per sector")
    lookup = {row["sector"]: number(row["emission_kg_per_output_unit"], "emission coefficient") for row in rows}
    return np.array([lookup[s] for s in sectors])


def solve(params: dict[str, object], tfp: np.ndarray) -> dict[str, np.ndarray | float]:
    x0, a, v, alpha, beta, endowment = (params[k] for k in ("x", "a", "v", "alpha", "beta", "endowment"))
    n = len(x0)
    labor_supply, capital_supply = endowment

    def calculate(log_variables: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray | float]]:
        prices = np.exp(log_variables[:n])
        rental = float(np.exp(log_variables[n]))
        output = np.exp(log_variables[n+1:])
        wages = 1.0  # numeraire; only relative prices are identified
        unit_va_cost = rental ** (1-alpha) / tfp
        income = wages*labor_supply + rental*capital_supply
        household_demand = beta*income/prices
        labor_demand = alpha*v*output*unit_va_cost/wages
        capital_demand = (1-alpha)*v*output*unit_va_cost/rental
        price_residual = prices - a.T@prices - v*unit_va_cost
        goods_residual = output - a@output - household_demand
        labor_residual = np.array([(labor_demand.sum()-labor_supply)/labor_supply])
        residual = np.r_[price_residual, goods_residual/x0, labor_residual]
        values = {"prices": prices, "rental": rental, "output": output,
                  "income": income, "household_demand": household_demand,
                  "labor_demand": labor_demand, "capital_demand": capital_demand,
                  "price_residual": price_residual, "goods_residual": goods_residual,
                  "labor_residual": labor_demand.sum()-labor_supply,
                  "capital_residual": capital_demand.sum()-capital_supply,
                  "household_budget_residual": float(prices@household_demand-income)}
        return residual, values

    initial = np.r_[np.zeros(n+1), np.log(x0)]
    solution = root(lambda q: calculate(q)[0], initial, method="hybr", options={"xtol": 1e-11})
    residual, values = calculate(solution.x)
    if not solution.success and np.max(np.abs(residual)) > 1e-9:
        raise RuntimeError(f"CGE equilibrium solver failed: {solution.message}")
    if np.max(np.abs(residual)) > 1e-8 or abs(values["capital_residual"])/capital_supply > 1e-8:
        raise RuntimeError("CGE market or factor residual exceeds tolerance")
    return values


def write_csv(path: Path, fields: list[str], records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    input_dir = args.input_dir.resolve(strict=True)
    out_dir = args.out_dir.resolve()
    if out_dir.is_relative_to(REPO_ROOT) or any((parent / ".git").exists() for parent in (out_dir, *out_dir.parents)):
        raise ValueError("Output must be outside this and every other Git checkout")
    if out_dir.exists():
        raise FileExistsError(f"Output directory already exists: {out_dir}")

    inputs = [input_dir / name for name in ("sam.csv", "scenarios.csv", "satellite.csv")]
    sectors, _, params = read_sam(inputs[0])
    scenarios = read_scenarios(inputs[1], sectors)
    emission_factor = read_satellite(inputs[2], sectors)
    solutions = {name: solve(params, tfp) for name, tfp in scenarios.items()}
    baseline = solutions["baseline"]
    if not (np.allclose(baseline["prices"], 1, atol=1e-8)
            and np.isclose(baseline["rental"], 1, atol=1e-8)
            and np.allclose(baseline["output"], params["x"], atol=1e-8)
            and np.allclose(baseline["household_demand"], params["x"]-params["a"]@params["x"], atol=1e-8)):
        raise RuntimeError("Zero-shock equilibrium does not reproduce the SAM benchmark")

    calibration = [{"sector": s, "benchmark_output": float(params["x"][i]),
                    "value_added_share": float(params["v"][i]),
                    "labor_share_of_value_added": float(params["alpha"][i]),
                    "household_budget_share": float(params["beta"][i])}
                   for i, s in enumerate(sectors)]
    equilibrium = []
    summary = []
    for name, values in solutions.items():
        for i, s in enumerate(sectors):
            equilibrium.append({"scenario": name, "sector": s, "tfp_multiplier": float(scenarios[name][i]),
                "output_price_index": float(values["prices"][i]), "gross_output_base_quantity": float(values["output"][i]),
                "household_demand_base_quantity": float(values["household_demand"][i]),
                "labor_demand": float(values["labor_demand"][i]),
                "capital_demand": float(values["capital_demand"][i]),
                "direct_emissions_kg": float(emission_factor[i]*values["output"][i])})
        summary.append({"scenario": name, "wage_numeraire": 1.0, "capital_rental_index": float(values["rental"]),
            "household_nominal_income": float(values["income"]),
            "total_direct_emissions_kg": float(emission_factor@values["output"]),
            "max_goods_market_residual": float(np.max(np.abs(values["goods_residual"]))),
            "max_price_residual": float(np.max(np.abs(values["price_residual"]))),
            "labor_market_residual": float(values["labor_residual"]),
            "capital_market_residual": float(values["capital_residual"]),
            "household_budget_residual": float(values["household_budget_residual"])})
    validation = {"model": "synthetic_one_household_two_factor_cge", "solver": "scipy.optimize.root/hybr",
                  "status": "numerical_synthetic_demo", "numeraire": "wage=1",
                  "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                  "sam_max_account_residual": float(np.max(np.abs(params["sam_residual"]))),
                  "baseline_reproduced": True,
                  "scenarios": list(scenarios), "sector_count": len(sectors)}
    out_dir.mkdir(parents=True)
    write_csv(out_dir / "calibration.csv", list(calibration[0]), calibration)
    write_csv(out_dir / "equilibrium.csv", list(equilibrium[0]), equilibrium)
    write_csv(out_dir / "summary.csv", list(summary[0]), summary)
    (out_dir / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "baseline_reproduced": True, "scenarios": list(scenarios)}))


if __name__ == "__main__":
    main()
