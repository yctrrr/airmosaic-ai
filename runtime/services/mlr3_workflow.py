"""Strict settings and portable provenance for the bounded regression workflow."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
from pathlib import PurePosixPath

from jsonschema import Draft202012Validator

from .tool_execution_paths import ExecutionPaths, ToolExecutionError, checked_path
from .tool_readiness import _inside_git, _overlaps
from .causal_dag import DAGError, check_adjustment, mermaid


WORKFLOW_ID = "ml_regression"
SKILL = "skills/model/shared/machine_learning_model"


def output_defaults(repo: Path) -> dict:
    return json.loads((repo / SKILL / "contracts/output-files.json").read_text(encoding="utf-8"))


def required_roles(cfg: dict) -> set[str]:
    roles = {"target_contract", "prepared_data", "preprocessing", "feature_selection", "provenance", "reproducibility", "status"}
    if cfg["analysis"] == "causal_plr":
        return roles | {"dag", "dag_plot", "causal_effect", "causal_residuals", "causal_folds", "causal_models"}
    roles |= {"candidates", "model", "predictions", "metrics"}
    methods = cfg["explanation"]["methods"]
    if "permutation" in methods:
        roles |= {"permutation", "importance_plot"}
    if "pdp" in methods or "ice" in methods:
        roles.add("dependence_plot")
    return roles | (set(methods) & {"pdp", "ice", "shap"})


def artifact_name(relative: str) -> PurePosixPath:
    """Validate a portable relative name without treating the repo as output."""
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or "\\" in relative or ":" in relative
            or any(part.casefold() in {"", ".", "..", ".git", ".airmosaic", ".env", "auth", "credentials", "secrets", "records", "temp", "browser_profiles"}
                   for part in relative.split("/"))):
        raise ToolExecutionError("invalid_artifact_relative_path")
    return path


def output_path(output: Path, relative: str) -> Path:
    actual = checked_path(str(output / artifact_name(relative)))
    if not actual.is_relative_to(output):
        raise ToolExecutionError("artifact_outside_output")
    # An explicitly allowed output root may already contain unrelated files.
    # Check each selected artifact's ancestors, without walking the directory;
    # never write into a nested checkout, including its .git-file form.
    for parent in (actual, *actual.parents):
        if not parent.is_relative_to(output):
            break
        if (parent / ".git").exists():
            raise ToolExecutionError("nested_git_in_artifact_output")
    return actual


def validate_configuration(value: dict, repo: Path) -> dict:
    """Accept settings, never expressions, callbacks, commands or remote schemas."""
    try:
        schema = json.loads((repo / "catalog/schemas/ml-regression-task.schema.json").read_text(encoding="utf-8"))
        if not Draft202012Validator(schema).is_valid(value):
            raise ValueError
        cfg = deepcopy(value)
        cfg.setdefault("analysis", "prediction")
        cfg.setdefault("feature_selection", {"mode": "manual"})
        cfg.setdefault("excluded_features", [])
        cfg["seeds"] = {**{key: cfg["seed"] for key in ("sampling", "model", "explanation", "causal")}, **cfg.get("seeds", {})}
        features = cfg["features"]
        if ({cfg["target"], cfg["id_column"], cfg["split"]["column"]} & set(features)
                or len({cfg["target"], cfg["id_column"], cfg["split"]["column"]}) != 3
                or not set(cfg["categorical_features"]) <= set(features)
                or not set(cfg.get("explanation", {}).get("features", [])) <= set(features)
                or set(features) & set(cfg["excluded_features"])
                or len({cfg["split"][k] for k in ("train", "val", "test")}) != 3
                or len({model["id"] for model in cfg["models"]}) != len(cfg["models"])):
            raise ValueError
        for model in cfg["models"]:
            if model["id"] == "baseline" or model["parameters"].get("mtry", 1) > len(features):
                raise ValueError
        if cfg["analysis"] == "prediction":
            cfg["explanation"].setdefault("methods", ["permutation", "pdp", "ice"])
            cfg["explanation"].setdefault("shap_permutations", 8)
            cfg["explanation"].setdefault("shap_rows", 5)
            if (cfg["explanation"]["shap_rows"] * cfg["explanation"]["shap_permutations"] *
                    len(features) * cfg["explanation"]["background_rows"] > 2_000_000):
                raise ValueError
        else:
            causal = cfg["causal"]
            if (set(features) != set(causal["adjustment_set"]) or causal["treatment"] in
                    {cfg["id_column"], cfg["target"], cfg["split"]["column"], *features}
                    or len(cfg["models"]) != 1 or cfg["missing"]["policy"] != "drop"
                    or not cfg.get("target_unit")
                    or cfg["feature_selection"]["mode"] != "manual"
                    or causal["resampling"]["mode"] == "group" and (not causal["resampling"].get("group_column")
                        or causal["resampling"]["group_column"] in {cfg["target"],causal["treatment"],cfg["split"]["column"]})):
                raise ValueError
            check_adjustment(causal["dag"], causal["treatment"], cfg["target"], causal["adjustment_set"])
        original_defaults = output_defaults(repo)
        defaults = {**original_defaults, **cfg.get("output_files", {})}
        if defaults["artifacts"] != "artifacts.json":
            raise ValueError
        for role, relative in defaults.items():
            checked_path(str(repo / artifact_name(relative)))
            if PurePosixPath(relative).suffix != PurePosixPath(original_defaults[role]).suffix:
                raise ValueError
        # Portable output names cannot alias on case-insensitive filesystems.
        paths = [PurePosixPath(value.casefold()) for value in defaults.values()]
        if any(a == b or a in b.parents or b in a.parents for i, a in enumerate(paths) for b in paths[i+1:]):
            raise ValueError
        cfg["output_files"] = defaults
        def clean(item):
            if isinstance(item, str):
                return not any(ord(char) < 32 for char in item)
            if isinstance(item, dict):
                return all(clean(key) and clean(child) for key, child in item.items())
            if isinstance(item, list):
                return all(clean(child) for child in item)
            return True
        if not clean(cfg):
            raise ValueError
        return cfg
    except DAGError as error:
        raise ToolExecutionError(str(error)) from None
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        raise ToolExecutionError("invalid_workflow_configuration") from None


def selected_library(paths: ExecutionPaths) -> Path | None:
    """Only an operator-selected dependency directory; personal libraries stay off."""
    value = os.environ.get("AIRMOSAIC_R_LIBRARY", "")
    if not value.strip():
        return None
    library = checked_path(value)
    forbidden = (paths.repo_root, paths.roots["AIRMOSAIC_CONFIG_DIR"],
                 paths.roots["AIRMOSAIC_AUTH_DIR"], paths.assets / "data", paths.run_root, paths.output)
    if not library.is_dir() or _inside_git(library) or any(_overlaps(library, root) for root in forbidden):
        raise ToolExecutionError("invalid_r_dependency_library")
    return library


def snapshot(cfg: dict, paths: ExecutionPaths, params: dict, repo: Path) -> Path:
    """Freeze validated settings and hash authorized data only during execution."""
    task = paths.temp / "workflow-task.json"
    content = json.dumps(cfg, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with task.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    digest = hashlib.sha256()
    with Path(params["input_csv"]).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    sources = ["catalog/schemas/ml-regression-task.schema.json", SKILL + "/contracts/output-files.json",
               "runtime/services/mlr3_workflow.py", "runtime/services/tool_runner.py",
               "runtime/services/tool_r.py", "runtime/services/causal_dag.py", "runtime/services/ml_execution_paths.py"]
    sources += [path.relative_to(repo).as_posix() for path in sorted((repo / SKILL / "scripts").rglob("*.R"))]
    provenance = {"schema_version": 1, "capability_id": WORKFLOW_ID, "capability_version": "2.0.0",
                  "input_sha256": digest.hexdigest(),
                  "configuration_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                  "configuration": cfg,
                  "source_sha256": {name: hashlib.sha256((repo / name).read_bytes()).hexdigest() for name in sources}}
    output = Path(params["out_dir"])
    for relative in [cfg["output_files"][role] for role in required_roles(cfg) | {"artifacts"}]:
        if output_path(output, relative).exists():
            raise ToolExecutionError("artifact_already_exists")
    destination = output_path(output, cfg["output_files"]["provenance"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(provenance, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    if cfg["analysis"] == "causal_plr":
        causal = cfg["causal"]
        for role, data in (("dag", check_adjustment(causal["dag"], causal["treatment"], cfg["target"], causal["adjustment_set"])),
                           ("dag_plot", mermaid(causal["dag"], causal["treatment"], cfg["target"]))):
            target = output_path(output, cfg["output_files"][role])
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(data if isinstance(data, str) else json.dumps(data, indent=2) + "\n")
    return task


def validate_outputs(output: Path) -> bool:
    """A completed process must satisfy its analysis-specific artifact contract."""
    try:
        # The manifest has a fixed safe discovery name; scientific artifacts can
        # use caller-configured relative names within the chosen output folder.
        manifest = json.loads((output / "artifacts.json").read_text(encoding="utf-8"))
        files = manifest["files"]
        if not isinstance(files, dict) or len(files) > 30:
            return False
        for relative in files.values():
            path = output_path(output, relative)
            if not path.is_file() or path.stat().st_size == 0:
                return False
        status = json.loads(output_path(output, files["status"]).read_text(encoding="utf-8"))
        provenance = json.loads(output_path(output, files["provenance"]).read_text(encoding="utf-8"))
        cfg = provenance["configuration"]
        if set(files) != required_roles(cfg) or any(files[key] != cfg["output_files"][key] for key in files):
            return False
        reproduction = json.loads(output_path(output, files["reproducibility"]).read_text(encoding="utf-8"))
        if status["status"] != "completed" or status["analysis"] != cfg["analysis"]:
            return False
        if manifest["analysis"] == "causal_plr":
            value = json.loads(output_path(output, files["causal_effect"]).read_text(encoding="utf-8"))
            return (all(type(value[key]) in (int, float) and math.isfinite(value[key]) for key in ("coefficient", "std_error"))
                    and value["cross_fitted"] is True and value["assumptions_status"] == "declared_not_verified")
        metrics = json.loads(output_path(output, files["metrics"]).read_text(encoding="utf-8"))
        return (all(type(metrics[split]["rmse"]) in (int, float) and math.isfinite(metrics[split]["rmse"])
                    for split in ("val", "test")) and reproduction["reload_predictions_equal"] is True)
    except (OSError, ValueError, TypeError, KeyError):
        return False
