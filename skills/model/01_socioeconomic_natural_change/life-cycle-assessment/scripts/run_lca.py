"""Demonstrate linear single-output LCI and one or more LCIA categories."""

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


def number(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("All numeric values must be finite")
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

    files = {name: input_dir / f"{name}.csv" for name in
             ("processes", "technosphere", "demand", "biosphere", "characterization")}
    process_rows = rows(files["processes"], ("process", "product", "product_unit"))
    processes = [r["process"].strip() for r in process_rows]
    products = [r["product"].strip() for r in process_rows]
    if (any(not p for p in processes + products) or
            len(processes) != len(set(processes)) or len(products) != len(set(products)) or
            any(not r["product_unit"].strip() for r in process_rows)):
        raise ValueError("Unique, nonempty processes/products and product units are required")
    pi = {value: i for i, value in enumerate(products)}
    qi = {value: i for i, value in enumerate(processes)}
    n = len(processes)

    t = np.zeros((n, n))
    seen_t = set()
    for row in rows(files["technosphere"], ("product", "process", "amount")):
        pair = (row["product"].strip(), row["process"].strip())
        if pair[0] not in pi or pair[1] not in qi or pair in seen_t:
            raise ValueError(f"Unknown or duplicate technosphere pair: {pair}")
        seen_t.add(pair)
        t[pi[pair[0]], qi[pair[1]]] = number(row["amount"])
    if len(seen_t) != n * n:
        raise ValueError("Technosphere input must include every product/process pair")
    for j, row in enumerate(process_rows):
        if t[j, j] <= 0 or np.any(np.delete(t[:, j], j) > 0):
            raise ValueError("Single-output convention requires positive reference output and nonpositive other entries")

    demand = np.zeros(n)
    seen_d = set()
    for row in rows(files["demand"], ("product", "amount")):
        product = row["product"].strip()
        if product not in pi or product in seen_d:
            raise ValueError(f"Unknown or duplicate demand product: {product}")
        seen_d.add(product)
        demand[pi[product]] = number(row["amount"])
    if seen_d != set(products) or np.any(demand < 0) or not np.any(demand > 0):
        raise ValueError("Demand must list every product, be nonnegative and include a positive value")
    condition = float(np.linalg.cond(t))
    if not math.isfinite(condition) or condition > 1e10:
        raise ValueError("Technosphere matrix is singular or too ill-conditioned")
    scale = np.linalg.solve(t, demand)
    if np.any(scale < -1e-10):
        raise ValueError("Negative process scale is outside this simple demonstration")
    residual = float(np.max(np.abs(t @ scale - demand)))

    bio_rows = rows(files["biosphere"], ("flow", "process", "amount_kg"))
    flows = list(dict.fromkeys(row["flow"].strip() for row in bio_rows))
    if any(not flow for flow in flows):
        raise ValueError("Biosphere flow identifiers must be nonempty")
    fi = {flow: i for i, flow in enumerate(flows)}
    b = np.zeros((len(flows), n))
    seen_b = set()
    for row in bio_rows:
        pair = (row["flow"].strip(), row["process"].strip())
        if pair[1] not in qi or pair in seen_b:
            raise ValueError(f"Unknown or duplicate biosphere pair: {pair}")
        seen_b.add(pair)
        amount = number(row["amount_kg"])
        if amount < 0:
            raise ValueError("This demonstration accepts nonnegative elementary flows only")
        b[fi[pair[0]], qi[pair[1]]] = amount
    if len(seen_b) != len(flows) * n:
        raise ValueError("Biosphere input must include every flow/process pair")
    inventory = b @ scale

    cf_rows = rows(files["characterization"], ("impact_category", "flow", "factor", "impact_unit"))
    categories = list(dict.fromkeys(row["impact_category"].strip() for row in cf_rows))
    factors: dict[tuple[str, str], float] = {}
    units: dict[str, str] = {}
    for row in cf_rows:
        category, flow, unit = (row[k].strip() for k in ("impact_category", "flow", "impact_unit"))
        if not category or flow not in fi or not unit or (category, flow) in factors:
            raise ValueError("Invalid or duplicate characterization entry")
        if category in units and units[category] != unit:
            raise ValueError("One impact category must have one result unit")
        units[category] = unit
        factors[(category, flow)] = number(row["factor"])
    if set(factors) != {(category, flow) for category in categories for flow in flows}:
        raise ValueError("Every impact category needs an explicit factor for every elementary flow")
    impacts = [
        {"impact_category": category, "impact_unit": units[category],
         "score": float(sum(factors[(category, flow)] * inventory[i] for i, flow in enumerate(flows)))}
        for category in categories
    ]

    out_dir.mkdir(parents=True)
    write_csv(out_dir / "process_scales.csv", ["process", "reference_product", "scale"], [
        {"process": process, "reference_product": products[i], "scale": float(scale[i])}
        for i, process in enumerate(processes)
    ])
    write_csv(out_dir / "inventory.csv", ["flow", "amount_kg"], [
        {"flow": flow, "amount_kg": float(inventory[i])} for i, flow in enumerate(flows)
    ])
    write_csv(out_dir / "impacts.csv", ["impact_category", "impact_unit", "score"], impacts)
    summary = {
        "method": "linear_single_output_lci_lcia_demo", "max_technosphere_residual": residual,
        "condition_number": condition,
        "input_sha256": {name + ".csv": hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"processes": n, "impact_categories": len(impacts), "max_residual": residual}))


if __name__ == "__main__":
    main()
