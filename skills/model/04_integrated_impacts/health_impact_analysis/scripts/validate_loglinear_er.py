"""Read-only structural/provenance validation; never computes mortality or approves a model."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
from urllib.parse import urlsplit


class RedactedArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "ER validation failed (InvalidArguments). Check the documented invocation.\n")


def linked(path):
    """Reject POSIX links and Windows reparse points, including junctions on Python 3.10+."""
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except FileNotFoundError:
        return False


def validate(dataset, assets_dir):
    if not assets_dir:
        raise ValueError("Explicit assets root required")
    assets_path = Path(assets_dir).absolute()
    dataset_path = Path(dataset).absolute()
    for candidate in (assets_path, dataset_path):
        for ancestor in (candidate, *candidate.parents):
            if linked(ancestor):
                raise ValueError("Linked paths are unsupported")
            if (ancestor / ".git").exists():
                raise ValueError("Repository paths are unsupported")
    assets_root = assets_path.resolve(strict=True)
    root = dataset_path.resolve(strict=True)
    stage = assets_root / "data" / "04_integrated_impacts" / "ExposureResponse"
    if root.parent != stage or not root.is_dir():
        raise ValueError("Expected a direct ER version directory under the external assets root")
    for boundary in ("AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
        configured = os.environ.get(boundary)
        if configured:
            boundary_path = Path(configured).resolve()
            if root == boundary_path or boundary_path in root.parents:
                raise ValueError("Configuration/authentication directories are unsupported")
    provenance = root / "provenance.json"
    if linked(provenance):
        raise ValueError("Linked provenance is unsupported")
    meta = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
    if not isinstance(meta, dict):
        raise ValueError("Provenance must be an object")
    for key in ("dataset_id", "source_version", "license_status", "parameter_file", "files", "counterfactual"):
        if not meta.get(key):
            raise ValueError("Missing provenance field: " + key)
    if not isinstance(meta["files"], dict) or not isinstance(meta["counterfactual"], dict):
        raise ValueError("Invalid metadata object types")
    name = meta["parameter_file"]
    if not isinstance(name, str):
        raise ValueError("Invalid parameter filename type")
    if Path(name).name != name or not name.endswith(".csv"):
        raise ValueError("parameter_file must be a local CSV basename")
    for filename, expected in meta["files"].items():
        if not isinstance(filename, str) or not isinstance(expected, str):
            raise ValueError("Invalid manifest types")
        if Path(filename).name != filename:
            raise ValueError("Manifest paths must be basenames")
        path = root / filename
        if linked(path) or path.resolve().parent != root:
            raise ValueError("Manifest path escapes dataset")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Source hash mismatch")
    if name not in meta["files"]:
        raise ValueError("Parameter CSV lacks hash")
    with (root / name).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames
        if not headers or any(not key for key in headers) or len(headers) != len(set(headers)):
            raise ValueError("Empty or duplicate parameter column names")
        rows = list(reader)
    if not rows:
        raise ValueError("Empty parameter file")
    required = {"parameter_id", "pollutant", "exposure_metric", "concentration_unit", "endpoint",
                "age_min_years", "age_max_years", "sex", "function_type", "rr", "rr_lower",
                "rr_upper", "ci_level", "increment", "source_url", "source_version", "source_locator"}
    keys = set()
    pending = []
    for row in rows:
        if None in row:
            raise ValueError("Unexpected unnamed parameter values")
        if not required.issubset(row):
            raise ValueError("Missing required columns")
        blank_allowed = {"age_min_years", "age_max_years"}
        if any(not row[k] for k in required - blank_allowed):
            raise ValueError("Blank required parameter metadata")
        key = row["parameter_id"]
        if key in keys:
            raise ValueError("Duplicate parameter_id")
        keys.add(key)
        if row["function_type"] != "log_linear":
            raise ValueError("Only log-linear coefficient records supported")
        if (row["pollutant"], row["exposure_metric"], row["concentration_unit"]) != ("PM2.5", "annual_mean", "ug/m3"):
            raise ValueError("Expected long-term annual PM2.5 in ug/m3")
        if row["endpoint"] != "natural_cause_mortality" or row["sex"] != "all":
            raise ValueError("This bounded contract supports pooled natural-cause records only")
        url = urlsplit(row["source_url"])
        if (row["source_version"] != meta["source_version"] or url.scheme != "https"
                or not url.hostname or url.username or url.password or url.query or url.fragment):
            raise ValueError("Use a stable public HTTPS source URL without credentials or query tokens")
        nums = {k: float(row[k]) for k in ("rr", "rr_lower", "rr_upper", "ci_level", "increment")}
        if not all(math.isfinite(v) for v in nums.values()):
            raise ValueError("Nonfinite parameter")
        if not 0 < nums["rr_lower"] <= nums["rr"] <= nums["rr_upper"] or nums["increment"] <= 0 or not 0 < nums["ci_level"] < 1:
            raise ValueError("Invalid RR, CI or concentration increment")
        if row["age_min_years"]:
            lo = float(row["age_min_years"])
            hi = float(row["age_max_years"]) if row["age_max_years"] else None
            if not math.isfinite(lo) or lo < 0 or (hi is not None and (not math.isfinite(hi) or hi <= lo)):
                raise ValueError("Invalid age bounds")
        elif row["age_max_years"]:
            raise ValueError("Upper age bound without lower bound")
        elif row.get("age_rule") == "adult_task_selection_required":
            pending.append("Adult minimum age requires task selection")
        else:
            raise ValueError("Missing age eligibility")
    cf = meta["counterfactual"]
    if isinstance(cf.get("value"), bool):
        raise ValueError("Reference exposure must be numeric, not boolean")
    if cf.get("unit") != "ug/m3" or not cf.get("meaning"):
        raise ValueError("Counterfactual metadata missing")
    if cf.get("value") is None:
        if cf.get("status") != "task_selection_required":
            raise ValueError("Unresolved reference must be explicit")
        pending.append("Reference exposure and below-reference rule require task selection")
    elif not math.isfinite(float(cf["value"])) or float(cf["value"]) < 0:
        raise ValueError("Invalid reference exposure")
    return {"parameter_rows": len(rows), "integrity_valid": True,
            "scientifically_approved": False, "health_adapter_executable": False,
            "pending_task_choices": sorted(set(pending))}


def main():
    parser = RedactedArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("dataset", help="External version directory with provenance.json")
    parser.add_argument("--assets-dir", default=os.environ.get("AIRMOSAIC_ASSETS_DIR"), help="Explicit external assets root, or AIRMOSAIC_ASSETS_DIR")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.dataset, args.assets_dir), indent=2))
    except (ValueError, OSError, KeyError, TypeError, AttributeError, csv.Error, UnicodeError) as exc:
        parser.exit(2, "ER validation failed (" + type(exc).__name__ + "). Check the selected source and contract locally.\n")


if __name__ == "__main__":
    main()
