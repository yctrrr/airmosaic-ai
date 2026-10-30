"""Plan-bound Python execution using explicit records, not authenticated identities."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from .tool_execution_paths import ToolExecutionError, checked_path, parse_parameters, separated_roots
from .tool_readiness import _inside_git

SKILL = "skills/model/shared/machine_learning_model"
ENTRY = SKILL + "/scripts/python/run_regression.py"
RESERVED = {"auth", "credentials", "secrets", ".git", ".env", "browser_profiles", "records", "temp"}


def _gate(repo: Path):
    source = repo / SKILL / "scripts/common/review_plan.py"
    spec = importlib.util.spec_from_file_location("airmosaic_shared_model_plan", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def python_implementation_hashes(repo: Path) -> dict[str, str]:
    """Public source identities to record at the actual implementation review."""
    files = [repo / ENTRY, repo / "runtime/services/python_ml_workflow.py",
             repo / "runtime/services/model_plan_gate.py",
             repo / "catalog/schemas/python-ml-regression-task.schema.json",
             repo / SKILL / "scripts/common/review_plan.py",
             repo / SKILL / "contracts/model-plan.schema.json"]
    files += list((repo / SKILL / "scripts/python").glob("*/*.py"))
    if len(files) > 64:
        raise ToolExecutionError("model_source_inventory_limit")
    return {p.relative_to(repo).as_posix(): hashlib.sha256(checked_path(str(p)).read_bytes()).hexdigest()
            for p in sorted(set(files))}


def _record_path(value: str, repo: Path, roots: dict, *, code: bool = False) -> Path:
    if not isinstance(value, str):
        raise ToolExecutionError("invalid_model_review_location")
    path = checked_path(value)
    assets = roots["AIRMOSAIC_ASSETS_DIR"]
    allowed = [assets / "results"] if code else [roots["AIRMOSAIC_CONFIG_DIR"], assets / "results", assets / "data"]
    base = next((base for base in allowed if path.is_relative_to(base)), None)
    if (base is None or _inside_git(path)
            or any(part.casefold() in RESERVED for part in path.relative_to(base).parts)
            or path.suffix.lower() != (".py" if code else ".json")
            or not path.is_file() or path.stat().st_size > 1024 * 1024):
        raise ToolExecutionError("invalid_model_review_location")
    return path


def inspect_python_review(cfg: dict, repo: Path, review_bundle: str | Path | None) -> dict:
    """Validate selected control records without opening input rows during preview."""
    if review_bundle is None:
        raise ToolExecutionError("model_review_bundle_required")
    roots = separated_roots(repo)
    source = _record_path(str(review_bundle), repo, roots)
    try:
        bundle = parse_parameters(source.read_text(encoding="utf-8-sig"))
        if set(bundle) != {"plan", "review", "delegation", "code_check", "code_file", "implementation_sha256"}:
            raise ValueError
        gate = _gate(repo)
        planned = gate.validate_plan(bundle["plan"], repo)
        if gate.canonical(planned) != gate.canonical(cfg):
            raise ToolExecutionError("generated_task_changed")
        identity = gate.plan_hash(bundle["plan"])
        review = bundle["review"]
        if (not isinstance(review, dict) or review.get("plan_sha256") != identity
                or review.get("decision") != "approved" or "execute" not in review.get("stages", [])):
            raise ToolExecutionError("model_plan_review_required")
        if bundle["implementation_sha256"] != python_implementation_hashes(repo):
            raise ToolExecutionError("reviewed_model_implementation_changed")
        _record_path(bundle["code_file"], repo, roots, code=True)
        if not isinstance(bundle["code_check"], dict):
            raise ValueError
        return bundle
    except ToolExecutionError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        raise ToolExecutionError("invalid_model_review_bundle") from None


def require_python_plan(cfg: dict, input_csv: Path, entrypoint: Path, *,
                        review_bundle: str | Path | None = None) -> dict:
    """Check full attested approval, data, task, code and reviewed implementation."""
    repo = next((p for p in entrypoint.parents if (p / "runtime/services").is_dir()), None)
    if repo is None or checked_path(str(entrypoint)) != checked_path(str(repo / ENTRY)):
        raise ToolExecutionError("unrecognized_model_entrypoint")
    bundle = inspect_python_review(cfg, repo, review_bundle)
    roots = separated_roots(repo)
    code = _record_path(bundle["code_file"], repo, roots, code=True)
    try:
        result = _gate(repo).require(bundle["plan"], repo, phase="execute",
            review=bundle["review"], delegation=bundle["delegation"],
            input_csv=input_csv, task=cfg, code=code, code_check=bundle["code_check"])
        return {"plan_sha256": result["plan_sha256"], "reviewer": result["reviewer"],
                "authorization": "caller_attested_not_authenticated", "scientific_acceptance": "not_granted"}
    except (OSError, ValueError, KeyError, TypeError):
        raise ToolExecutionError("python_model_plan_rejected") from None
