"""Explicit activity/technology/control accounting; local standard-library CLI only.

No discovery, downloads, credentials or implicit emission-factor lookup. The direct
CLI has its own narrow path checks; it is not a registered run-tool adapter.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import stat
import sys

TOLERANCE = 1e-9
MAX_INPUT_BYTES = 1024 * 1024
MAX_ROWS = 10000
UNITS = {"kg": ("mass", 0.001), "tonne": ("mass", 1.0),
         "GJ": ("energy", 1.0), "TJ": ("energy", 1000.0),
         "MWh": ("energy", 3.6), "unit_product": ("count", 1.0)}
MASS_TO_KG = {"g": 0.001, "kg": 1.0, "tonne": 1000.0}
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")
TABLE_FIELDS = {
    "activities": {"activity_id", "region", "year", "sector", "process", "amount", "unit", "activity_basis", "source_ref"},
    "technologies": {"activity_id", "technology_id", "activity_share", "source_ref"},
    "factors": {"activity_id", "technology_id", "pollutant", "value", "mass_unit", "activity_unit", "activity_basis", "control_basis", "source_ref"},
    "control_routes": {"activity_id", "technology_id", "pollutant", "route_id", "route_share", "operating_fraction", "capture_fraction", "removal_efficiency", "source_ref"},
}


class InventoryError(ValueError):
    """Fixed diagnostic codes avoid echoing paths or input values."""


def fail(code):
    raise InventoryError(code)


def number(value, minimum=0.0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail("invalid_numeric_value")
    if value < minimum or (maximum is not None and value > maximum):
        fail("numeric_value_out_of_range")
    return float(value)


def identifier(value):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        fail("invalid_identifier")
    return value


def provenance(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 400 or any(ord(c) < 32 for c in value):
        fail("missing_or_invalid_source_reference")
    if re.search(r"(?i)(?<![a-z0-9])[a-z]:[\\/]|/(?:Users|home)/|(?:token|password|signature|api_key)=", value):
        fail("private_source_reference")


def rows(payload, table):
    records = payload.get(table)
    if not isinstance(records, list) or not records or len(records) > MAX_ROWS:
        fail("invalid_or_excessive_table")
    for row in records:
        if not isinstance(row, dict) or set(row) != TABLE_FIELDS[table]:
            fail("table_schema_mismatch")
        provenance(row["source_ref"])
        for key in ("activity_id", "technology_id", "pollutant", "route_id"):
            if key in row:
                identifier(row[key])
    return records


def exact_sum(values, code):
    if not math.isclose(math.fsum(values), 1.0, rel_tol=0, abs_tol=TOLERANCE):
        fail(code)


def calculate_inventory(payload):
    """Return pollutant-specific detailed and aggregated kg emissions in memory."""
    required = {"schema_version", "dataset_kind", "inventory_id", "pollutants", *TABLE_FIELDS}
    if not isinstance(payload, dict) or set(payload) != required or type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        fail("inventory_schema_mismatch")
    if payload["dataset_kind"] not in {"synthetic", "prepared_inventory"}:
        fail("invalid_dataset_kind")
    inventory_id = identifier(payload["inventory_id"])
    pollutants = payload["pollutants"]
    if not isinstance(pollutants, list) or not pollutants or len(pollutants) > 32:
        fail("invalid_pollutants")
    if len(set(map(identifier, pollutants))) != len(pollutants):
        fail("duplicate_pollutant")
    activities = {}
    for row in rows(payload, "activities"):
        key = row["activity_id"]
        if key in activities:
            fail("duplicate_activity")
        for label in ("region", "sector", "process", "activity_basis"):
            identifier(row[label])
        if isinstance(row["year"], bool) or not isinstance(row["year"], int) or not 1900 <= row["year"] <= 2200:
            fail("invalid_year")
        number(row["amount"])
        if row["unit"] not in UNITS:
            fail("unsupported_activity_unit")
        activities[key] = row
    technologies = {}
    shares = defaultdict(list)
    for row in rows(payload, "technologies"):
        key = row["activity_id"], row["technology_id"]
        if row["activity_id"] not in activities:
            fail("unknown_activity")
        if key in technologies:
            fail("duplicate_technology")
        shares[key[0]].append(number(row["activity_share"], maximum=1))
        technologies[key] = row
    if set(shares) != set(activities):
        fail("activity_without_technology")
    for values in shares.values():
        exact_sum(values, "technology_shares_must_sum_to_one")
    factors = {}
    for row in rows(payload, "factors"):
        key = row["activity_id"], row["technology_id"], row["pollutant"]
        if key[:2] not in technologies or key[2] not in pollutants:
            fail("unknown_factor_key")
        if key in factors:
            fail("duplicate_factor")
        if row["control_basis"] != "uncontrolled":
            fail("factor_must_be_uncontrolled")
        number(row["value"])
        if row["mass_unit"] not in MASS_TO_KG or row["activity_unit"] not in UNITS:
            fail("unsupported_factor_unit")
        activity = activities[key[0]]
        if UNITS[activity["unit"]][0] != UNITS[row["activity_unit"]][0]:
            fail("activity_factor_dimension_mismatch")
        if row["activity_basis"] != activity["activity_basis"]:
            fail("activity_factor_basis_mismatch")
        factors[key] = row
    expected = {(*key, pollutant) for key in technologies for pollutant in pollutants}
    if set(factors) != expected:
        fail("incomplete_pollutant_factor_coverage")
    routes = defaultdict(list)
    route_keys = set()
    for row in rows(payload, "control_routes"):
        key = row["activity_id"], row["technology_id"], row["pollutant"]
        if key not in expected:
            fail("unknown_control_key")
        if (*key, row["route_id"]) in route_keys:
            fail("duplicate_control_route")
        route_keys.add((*key, row["route_id"]))
        for label in ("route_share", "operating_fraction", "capture_fraction", "removal_efficiency"):
            number(row[label], maximum=1)
        routes[key].append(row)
    if set(routes) != expected:
        fail("incomplete_control_route_coverage")
    for control_rows in routes.values():
        exact_sum([row["route_share"] for row in control_rows], "control_route_shares_must_sum_to_one")
    details, route_details = [], []
    grouped = defaultdict(list)
    for key in sorted(expected):
        activity = activities[key[0]]
        technology = technologies[key[:2]]
        factor = factors[key]
        amount = float(activity["amount"]) * float(technology["activity_share"])
        factor_activity = amount * UNITS[activity["unit"]][1] / UNITS[factor["activity_unit"]][1]
        uncontrolled = factor_activity * float(factor["value"]) * MASS_TO_KG[factor["mass_unit"]]
        if not math.isfinite(uncontrolled):
            fail("nonfinite_calculation")
        route_emissions = []
        for route in routes[key]:
            reduction = float(route["operating_fraction"]) * float(route["capture_fraction"]) * float(route["removal_efficiency"])
            route_uncontrolled = uncontrolled * float(route["route_share"])
            emitted = route_uncontrolled * (1.0 - reduction)
            route_emissions.append(emitted)
            route_details.append({"activity_id": key[0], "technology_id": key[1], "pollutant": key[2],
                "route_id": route["route_id"], "route_share": route["route_share"],
                "operating_fraction": route["operating_fraction"], "capture_fraction": route["capture_fraction"],
                "removal_efficiency": route["removal_efficiency"], "uncontrolled_kg": route_uncontrolled,
                "emitted_kg": emitted, "removed_kg": route_uncontrolled - emitted})
        emitted = math.fsum(route_emissions)
        removed = uncontrolled - emitted
        if emitted < -TOLERANCE or removed < -TOLERANCE or not math.isclose(uncontrolled, emitted + removed, rel_tol=1e-12, abs_tol=TOLERANCE):
            fail("emission_mass_balance_failed")
        detail = {"activity_id": key[0], "region": activity["region"], "year": activity["year"],
            "sector": activity["sector"], "process": activity["process"], "technology_id": key[1],
            "pollutant": key[2], "allocated_activity": amount, "activity_unit": activity["unit"],
            "uncontrolled_kg": uncontrolled, "emitted_kg": emitted, "removed_kg": removed}
        details.append(detail)
        grouped[(activity["region"], activity["year"], activity["sector"], key[2])].append(detail)
    totals = []
    for key, values in sorted(grouped.items()):
        totals.append({"region": key[0], "year": key[1], "sector": key[2], "pollutant": key[3],
            "uncontrolled_kg": math.fsum(row["uncontrolled_kg"] for row in values),
            "emitted_kg": math.fsum(row["emitted_kg"] for row in values),
            "removed_kg": math.fsum(row["removed_kg"] for row in values)})
    for pollutant in pollutants:
        for quantity in ("uncontrolled_kg", "emitted_kg", "removed_kg"):
            if not math.isclose(math.fsum(row[quantity] for row in details if row["pollutant"] == pollutant),
                                math.fsum(row[quantity] for row in totals if row["pollutant"] == pollutant),
                                rel_tol=1e-12, abs_tol=TOLERANCE):
                fail("aggregation_mismatch")
    return {"inventory_id": inventory_id, "dataset_kind": payload["dataset_kind"],
            "details": details, "routes": route_details, "totals": totals,
            "checks": {"technology_shares": "passed", "control_route_shares": "passed",
                       "units_and_activity_basis": "passed", "emission_mass_balance": "passed",
                       "pollutant_specific_aggregation": "passed", "scientific_acceptance": "not_assessed"}}


def checked_path(path):
    path = Path(path).absolute()
    for parent in (path, *path.parents):
        if parent.exists() and (parent.is_symlink() or getattr(parent.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)):
            fail("linked_path_refused")
    if any(part.casefold() in {"auth", "credentials", "secrets", ".ssh", ".aws", ".git"} for part in path.parts):
        fail("private_location_refused")
    return path.resolve()


def duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate_json_key")
        result[key] = value
    return result


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def write_csv(path, values):
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(values[0]))
        writer.writeheader()
        writer.writerows(values)


def run(args):
    root = checked_path(args.input_root)
    if not root.is_dir():
        fail("input_root_unavailable")
    relative = Path(args.input_json)
    if relative.is_absolute() or ".." in relative.parts or "~" in relative.parts or relative.suffix != ".json":
        fail("input_must_be_relative_json")
    source = checked_path(root / relative)
    if not source.is_relative_to(root) or not source.is_file() or source.stat().st_size > MAX_INPUT_BYTES:
        fail("input_unavailable_or_excessive")
    raw = source.read_bytes()
    payload = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=duplicate_keys,
                         parse_constant=lambda _: fail("nonfinite_json_value"))
    calculated = calculate_inventory(payload)
    output_root = checked_path(args.output_root)
    if not output_root.is_dir():
        fail("output_root_unavailable")
    if any((parent / ".git").exists() for parent in (output_root, *output_root.parents)):
        fail("output_inside_git_refused")
    name = args.run_name or datetime.now(timezone.utc).strftime("%Y%m%d%H%M") + "_" + calculated["inventory_id"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name):
        fail("invalid_run_name")
    output = checked_path(output_root / name)
    if not output.is_relative_to(output_root) or output.exists():
        fail("output_exists_or_outside_root")
    if args.dry_run:
        return {"status": "validated", "dataset_kind": calculated["dataset_kind"],
                "output_created": False, "detail_rows": len(calculated["details"]),
                "checks": calculated["checks"]}
    output.mkdir(exist_ok=False)
    write_csv(output / "emissions.csv", calculated["details"])
    write_csv(output / "route_emissions.csv", calculated["routes"])
    write_csv(output / "totals.csv", calculated["totals"])
    write_json(output / "quality.json", calculated["checks"])
    if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(raw).digest():
        fail("input_changed_during_run")
    record = {"schema_version": 1, "inventory_id": calculated["inventory_id"],
        "dataset_kind": calculated["dataset_kind"], "recorded_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": hashlib.sha256(raw).hexdigest(), "input_modified": False,
        "method": "activity_technology_exclusive_control_routes_v1", "python": sys.version.split()[0],
        "network_used": False, "credentials_read": False, "scientific_acceptance": "not_assessed"}
    write_json(output / "record.json", record)
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}
    write_json(output / "artifacts.json", {"status": "succeeded", "files_sha256": files})
    return {"status": "succeeded", "dataset_kind": calculated["dataset_kind"],
            "detail_rows": len(calculated["details"]), "aggregate_rows": len(calculated["totals"]),
            "artifact_index": "artifacts.json", "scientific_acceptance": "not_assessed"}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"status":"failed","reason":"invalid_arguments"}\n')


def main():
    parser = Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-name")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = run(args)
    except InventoryError as error:
        result = {"status": "failed", "reason": str(error)}
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, KeyError, OverflowError, RecursionError):
        result = {"status": "failed", "reason": "invalid_input_or_io_failure"}
    print(json.dumps(result, allow_nan=False))
    return 0 if result["status"] in {"validated", "succeeded"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
