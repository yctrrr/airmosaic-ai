"""Balance explicitly classified economy-boundary material flows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
FLOW_TYPES = (
    "extraction", "import", "export", "environment_output",
    "stock_addition", "balancing_input", "balancing_output",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--require-balanced", action="store_true")
    args = parser.parse_args()
    source = args.input.resolve(strict=True)
    out_dir = args.out_dir.resolve()
    if out_dir.is_relative_to(REPO_ROOT):
        raise ValueError("Output must be outside the repository checkout")
    if out_dir.exists():
        raise FileExistsError(f"Output directory already exists: {out_dir}")

    groups: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["year", "material", "flow_type", "amount_t"]:
            raise ValueError("Expected columns: year,material,flow_type,amount_t")
        for row in reader:
            year, material, kind = (row[key].strip() for key in ("year", "material", "flow_type"))
            if not year.isdigit() or not material or kind not in FLOW_TYPES:
                raise ValueError(f"Invalid year, material or flow type: {row}")
            amount = float(row["amount_t"])
            if not math.isfinite(amount) or amount < 0:
                raise ValueError("Flow amounts must be finite and nonnegative tonnes")
            group = groups[(year, material)]
            if kind in group:
                raise ValueError(f"Duplicate flow type for {(year, material, kind)}")
            group[kind] = amount
    if not groups:
        raise ValueError("Empty input")

    results = []
    for (year, material), flow in sorted(groups.items()):
        missing = set(FLOW_TYPES) - set(flow)
        if missing:
            raise ValueError(f"{year}/{material}: missing explicit flow types {sorted(missing)}")
        incoming = flow["extraction"] + flow["import"] + flow["balancing_input"]
        outgoing = flow["export"] + flow["environment_output"] + flow["stock_addition"] + flow["balancing_output"]
        residual = incoming - outgoing
        tolerance = 1e-9 * max(1.0, incoming, outgoing)
        results.append({
            "year": year, "material": material,
            "domestic_material_consumption_t": flow["extraction"] + flow["import"] - flow["export"],
            "balance_residual_t": residual, "balanced": abs(residual) <= tolerance,
        })
    if args.require_balanced and not all(item["balanced"] for item in results):
        raise ValueError("At least one material balance is open; inspect the source before strict execution")

    out_dir.mkdir(parents=True)
    with (out_dir / "balances.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    summary = {
        "method": "simple_economy_boundary_material_balance", "unit": "tonne",
        "all_balanced": all(item["balanced"] for item in results),
        "max_abs_balance_residual_t": max(abs(item["balance_residual_t"]) for item in results),
        "groups": len(results), "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"groups": len(results), "all_balanced": summary["all_balanced"]}))


if __name__ == "__main__":
    main()
