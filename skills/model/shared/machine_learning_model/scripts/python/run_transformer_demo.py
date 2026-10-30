"""CPU-only synthetic input demonstrations; deliberately no external-data option."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib import metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import sys

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[1]
REPO = SKILL.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

CASES = ("tabular", "sequence", "grid", "fusion")
SHAPES = {"static": [4], "history": [8, 3], "grid": [1, 4, 4]}
BRANCHES = {"tabular": ["static"], "sequence": ["history"], "grid": ["grid"], "fusion": ["static", "history", "grid"]}
RESERVED = {".git", ".env", "auth", "secrets", "credentials", "browser_profiles", "records", "temp"}


class DemoError(ValueError):
    """Fixed diagnostic codes, never caller data or locations."""


def validate_configuration(config: dict) -> dict:
    keys = {"schema_version", "purpose", "seed", "samples", "d_model", "heads", "layers", "epochs", "batch_size", "learning_rate", "weight_decay", "dropout"}
    if not isinstance(config, dict) or set(config) != keys:
        raise DemoError("invalid_demo_configuration")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1 or config["purpose"] != "synthetic_software_demo":
        raise DemoError("invalid_demo_purpose")
    bounds = {"seed": (0, 2**31 - 1), "d_model": (8, 64), "heads": (1, 4), "layers": (1, 2), "epochs": (1, 16), "batch_size": (1, 64)}
    for name, (low, high) in bounds.items():
        if type(config[name]) is not int or not low <= config[name] <= high:
            raise DemoError("demo_budget_exceeded")
    if config["d_model"] % config["heads"]:
        raise DemoError("incompatible_demo_dimensions")
    counts = config["samples"]
    if not isinstance(counts, dict) or set(counts) != {"train", "val", "test"} or any(type(v) is not int or not 4 <= v <= 256 for v in counts.values()):
        raise DemoError("invalid_demo_counts")
    for name, low, high in [("learning_rate", 0.00001, 0.1), ("weight_decay", 0, 0.1), ("dropout", 0, 0.3)]:
        value = config[name]
        if type(value) not in (float, int) or not math.isfinite(value) or not low <= value <= high:
            raise DemoError("invalid_demo_training_parameter")
    return config


def prepare(config_file: str, out_dir: str, case: str):
    if case not in CASES:
        raise DemoError("unsupported_demo_case")
    roots = separated_roots()
    try:
        assets = roots["AIRMOSAIC_ASSETS_DIR"]
        value = config_file.replace("${AIRMOSAIC_ASSETS_DIR}", str(assets))
        if not Path(value).is_absolute():
            if not value.replace("\\", "/").startswith("config/examples/"):
                raise DemoError("demo_configuration_root")
            value = str(REPO / value)
        config_path = checked_path(value)
        examples = REPO / "config/examples"
        selected_root = next((root for root in (examples, roots["AIRMOSAIC_CONFIG_DIR"]) if config_path.is_relative_to(root)), None)
        if selected_root is None or config_path.suffix.lower() != ".json" or not config_path.is_file():
            raise DemoError("demo_configuration_root")
        if any(part.casefold() in RESERVED for part in config_path.relative_to(selected_root).parts):
            raise DemoError("demo_private_configuration")
        if selected_root != examples and _inside_git(config_path):
            raise DemoError("demo_configuration_inside_git")
        if selected_root == examples and any((ancestor / ".git").exists() for ancestor in (config_path.parent, *config_path.parents) if ancestor != REPO and ancestor.is_relative_to(REPO)):
            raise DemoError("demo_nested_repository")
        if config_path.stat().st_size > 65536:
            raise DemoError("demo_configuration_too_large")
        def unique(pairs):
            values = {}
            for key, value in pairs:
                if key in values:
                    raise DemoError("duplicate_demo_configuration")
                values[key] = value
            return values
        def invalid_constant(_):
            raise DemoError("invalid_demo_configuration")
        config = validate_configuration(json.loads(config_path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique, parse_constant=invalid_constant))
        output = validated_output(out_dir, roots)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise DemoError("demo_configuration_or_output_unavailable") from None
    return config, output


def checked_path(value: str) -> Path:
    # Load this fixed stdlib-only repository utility without importing the SDK's
    # package initializers. No caller-selected module path or callback exists.
    spec = importlib.util.spec_from_file_location("_transformer_local_paths", REPO / "runtime/services/tool_paths.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = Path(value)
    for part in path.parts[1:]:
        if ":" in part or part.endswith((".", " ")) or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", part, re.I):
            raise DemoError("invalid_demo_local_path")
    try:
        return module.local_path(value)
    except (OSError, ValueError, RuntimeError):
        raise DemoError("invalid_demo_local_path") from None


def _inside_git(path: Path) -> bool:
    return any((parent / ".git").exists() or (parent / ".git").is_symlink() for parent in (path, *path.parents))


def separated_roots() -> dict[str, Path]:
    roots = {}
    for name in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
        value = os.environ.get(name, "")
        if not value.strip():
            raise DemoError("missing_separated_roots")
        root = checked_path(value)
        if not root.is_dir() or _inside_git(root) or root.is_relative_to(REPO) or REPO.is_relative_to(root):
            raise DemoError("invalid_separated_roots")
        if any(root.is_relative_to(other) or other.is_relative_to(root) for other in roots.values()):
            raise DemoError("overlapping_roots")
        roots[name] = root
    return roots


def validated_output(value: str, roots: dict[str, Path]) -> Path:
    assets = roots["AIRMOSAIC_ASSETS_DIR"]
    output = checked_path(value.replace("${AIRMOSAIC_ASSETS_DIR}", str(assets)))
    base = assets / "results"
    if not output.is_relative_to(base) or len(output.relative_to(base).parts) < 2:
        raise DemoError("demo_output_outside_results")
    if any(part.casefold() in RESERVED for part in output.relative_to(base).parts) or _inside_git(output):
        raise DemoError("demo_unsafe_output")
    if output.exists():
        raise DemoError("demo_output_exists")
    return output


def dependency_blockers() -> list[str]:
    blockers = []
    if sys.version_info < (3, 11):
        blockers.append("python_3_11_required")
    try:
        version = metadata.version("torch")
        parts = re.match(r"(\d+)\.(\d+)", version)
        if not parts or tuple(map(int, parts.groups())) < (2, 6):
            blockers.append("torch_2_6_required")
    except metadata.PackageNotFoundError:
        blockers.append("missing_torch")
    return blockers


def synthetic_split(config: dict, split: str, case: str):
    import torch
    count = config["samples"][split]
    offset = {"train": 101, "val": 202, "test": 303}[split]
    generator = torch.Generator(device="cpu").manual_seed(config["seed"] + offset)
    values = {name: torch.randn(count, *shape, generator=generator) for name, shape in SHAPES.items()}
    # Identical complete labels across cases; single-input cases see only their
    # declared branch. This is a known synthetic signal, not atmospheric data.
    target = (0.5 * values["static"][:, 0] + 0.4 * values["history"][:, -1, 0]
              + 0.3 * values["grid"].mean((1, 2, 3))
              + 0.01 * torch.randn(count, generator=generator))
    return {name: values[name] for name in BRANCHES[case]}, target


def fit_preprocessing(train: dict) -> dict:
    return {name: {"mean": values.mean(0), "scale": values.std(0, unbiased=False).clamp_min(1e-6)} for name, values in train.items()}


def transform(values: dict, state: dict) -> dict:
    return {name: (tensor - state[name]["mean"]) / state[name]["scale"] for name, tensor in values.items()}


def execute(config: dict, output: Path, case: str) -> dict:
    validate_configuration(config)
    if case not in CASES:
        raise DemoError("unsupported_demo_case")
    output = validated_output(str(output), separated_roots())
    if dependency_blockers():
        raise DemoError("demo_dependency_unavailable")
    import torch
    from models.transformer_demo import SyntheticTransformer
    from common.artifacts import digest, metrics, write_csv, write_json
    torch.set_num_threads(1)
    torch.manual_seed(config["seed"])
    torch.use_deterministic_algorithms(True)
    # Recheck immediately before exclusive creation. This guards mistakes, not
    # malicious concurrent filesystem mutation or untrusted dependency code.
    output = validated_output(str(output), separated_roots())
    output.mkdir(parents=True, exist_ok=False)
    event_path = output / "events.jsonl"
    event_path.touch(exist_ok=False)
    event_index = 0

    def event(kind, **values):
        nonlocal event_index
        event_index += 1
        with event_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"sequence": event_index, "time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": kind, **values}, allow_nan=False) + "\n")

    write_json(output / "configuration.json", {"case": case, **config})
    event("synthetic_generation", case=case)
    raw_train, y_train = synthetic_split(config, "train", case)
    raw_val, y_val = synthetic_split(config, "val", case)
    state = fit_preprocessing(raw_train)
    train, val = transform(raw_train, state), transform(raw_val, state)
    model = SyntheticTransformer(case, config).to("cpu")
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["learning_rate"], weight_decay=config["weight_decay"])
    generator = torch.Generator(device="cpu").manual_seed(config["seed"] + 17)
    best_loss, best_state, best_epoch = math.inf, None, None
    nonzero_gradient = False
    for epoch in range(1, config["epochs"] + 1):
        model.train()
        order = torch.randperm(len(y_train), generator=generator)
        for indices in order.split(config["batch_size"]):
            optimizer.zero_grad(set_to_none=True)
            prediction = model({name: values[indices] for name, values in train.items()})
            loss = torch.mean((prediction - y_train[indices]) ** 2)
            if not torch.isfinite(loss):
                raise DemoError("nonfinite_demo_loss")
            loss.backward()
            gradients = [p.grad for p in model.parameters() if p.grad is not None]
            if not gradients or not all(torch.isfinite(g).all() for g in gradients):
                raise DemoError("invalid_demo_gradient")
            nonzero_gradient |= any(bool(g.abs().sum() > 0) for g in gradients)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        model.eval()
        with torch.no_grad():
            val_loss = float(torch.mean((model(val) - y_val) ** 2))
        if not math.isfinite(val_loss):
            raise DemoError("nonfinite_demo_validation")
        if val_loss < best_loss:
            best_loss, best_epoch = val_loss, epoch
            best_state = {name: tensor.detach().clone() for name, tensor in model.state_dict().items()}
        event("epoch_completed", epoch=epoch, validation_mse=val_loss)
    if not nonzero_gradient:
        raise DemoError("zero_demo_gradient")
    model.load_state_dict(best_state)
    model.eval()
    event("checkpoint_selected", epoch=best_epoch, criterion="validation_mse")
    torch.save({"model": best_state, "preprocessing": state}, output / "checkpoint.pt")
    # Test generation/evaluation occurs only after checkpoint selection.
    raw_test, y_test = synthetic_split(config, "test", case)
    test = transform(raw_test, state)
    with torch.no_grad():
        prediction = model(test)
    if not torch.isfinite(prediction).all():
        raise DemoError("nonfinite_demo_prediction")
    scores = metrics(y_test.tolist(), prediction.tolist())
    reference = metrics(y_test.tolist(), [float(y_train.mean())] * len(y_test))
    tensor_rmse = float(torch.mean((prediction - y_test) ** 2).sqrt())
    tensor_mae = float(torch.mean((prediction - y_test).abs()))
    if not math.isclose(scores["rmse"], tensor_rmse, rel_tol=1e-5, abs_tol=1e-6) or not math.isclose(scores["mae"], tensor_mae, rel_tol=1e-5, abs_tol=1e-6):
        raise DemoError("demo_metric_mismatch")
    total = float(torch.sum((y_test.double() - y_test.double().mean()) ** 2))
    tensor_r2 = 1 - float(torch.sum((prediction.double() - y_test.double()) ** 2)) / total if total else None
    if (scores["r2"] is None) != (tensor_r2 is None) or (tensor_r2 is not None and not math.isclose(scores["r2"], tensor_r2, rel_tol=1e-5, abs_tol=1e-6)):
        raise DemoError("demo_metric_mismatch")
    # Deserialize only the checkpoint freshly written by this execution.
    restored = torch.load(output / "checkpoint.pt", map_location="cpu", weights_only=True)
    reloaded = SyntheticTransformer(case, config).to("cpu")
    reloaded.load_state_dict(restored["model"])
    reloaded.eval()
    with torch.no_grad():
        again = reloaded(transform(raw_test, restored["preprocessing"]))
    if not torch.allclose(prediction, again, rtol=1e-6, atol=1e-7):
        raise DemoError("demo_reload_mismatch")
    event("test_evaluated", retained_rows=len(y_test))
    write_csv(output / "predictions.csv", [{"sample_id": f"test_{i:06d}", "observed": float(y), "predicted": float(p)} for i, (y, p) in enumerate(zip(y_test, prediction))])
    write_json(output / "metrics.json", {"network": scores, "training_mean_reference": reference, "validation_mse": best_loss, "best_epoch": best_epoch, "target_unit": "synthetic_unit"})
    write_json(output / "input-contract.json", {"source": "internal_synthetic_generator_v1", "input_shapes_without_batch": {name: SHAPES[name] for name in BRANCHES[case]}, "samples": config["samples"], "preprocessing_fit": "train_only", "test_generated_after_checkpoint_selection": True})
    checks = {"nonzero_finite_gradients": nonzero_gradient, "independent_metrics": True, "reload_equal": True, "scientific_acceptance": False}
    write_json(output / "checks.json", checks)
    event("engineering_checks_passed")
    write_json(output / "status.json", {"status": "succeeded", "purpose": config["purpose"], "python": platform.python_version(), "torch": torch.__version__, "device": "cpu", "source_sha256": {"entry": digest(Path(__file__)), "model": digest(HERE / "models/transformer_demo.py"), "metrics": digest(HERE / "common/artifacts.py"), "paths": digest(REPO / "runtime/services/tool_paths.py")}})
    names = ["configuration.json", "input-contract.json", "metrics.json", "predictions.csv", "checkpoint.pt", "events.jsonl", "checks.json", "status.json"]
    write_json(output / "artifacts.json", {"purpose": config["purpose"], "files": {name: {"path": name, "sha256": digest(output / name)} for name in names}})
    return {"status": "succeeded", "case": case, "artifacts": "${AIRMOSAIC_ASSETS_DIR}/results/<task-output>/artifacts.json", "scientific_acceptance": False}


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "invalid_demo_arguments\n")


def main(argv=None):
    parser = SafeParser(description=__doc__)
    parser.add_argument("--case", required=True, choices=CASES)
    parser.add_argument("--config-file", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config, output = prepare(args.config_file, args.out_dir, args.case)
        blockers = dependency_blockers()
        if args.dry_run:
            print(json.dumps({"case": args.case, "can_execute": not blockers, "blockers": blockers, "external_input_supported": False, "output_created": False}))
            return 0
        if blockers:
            raise DemoError("demo_dependency_unavailable")
        print(json.dumps(execute(config, output, args.case)))
        return 0
    except DemoError as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
    except Exception:
        print(json.dumps({"status": "failed", "error": "transformer_demo_failed"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
