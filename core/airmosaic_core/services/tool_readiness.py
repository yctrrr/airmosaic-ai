"""Non-executing prerequisite probes; no secret values enter public results."""

from __future__ import annotations

from importlib import metadata
import os
from pathlib import Path
import sys
from typing import Any

from .tool_paths import executable_available, local_path


ROOT_NAMES = ("AIRMOSAIC_LOCAL_WORKSPACE", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR")


def _overlaps(first: Path, second: Path) -> bool:
    return first.is_relative_to(second) or second.is_relative_to(first)


def _inside_git(path: Path) -> bool:
    for ancestor in (path, *path.parents):
        try:
            (ancestor / ".git").lstat()
            return True
        except FileNotFoundError:
            continue
    return False


def _configuration(spec: dict[str, str], repo_root: Path) -> dict[str, str]:
    name, role = spec["name"], spec["role"]
    result = {"name": name, "role": role, "status": "configured"}
    value = os.environ.get(name, "")
    if not value.strip():
        return {**result, "status": "missing_configuration", "reason": "not_set"}
    try:
        path = local_path(value)
        if path.is_relative_to(repo_root) or _inside_git(path):
            return {**result, "status": "invalid_configuration", "reason": "inside_git_checkout"}
        # Other root values are used only for path comparisons; no config/profile
        # files are opened, imported, globbed or walked.
        roots = {key: local_path(os.environ[key]) for key in ROOT_NAMES if os.environ.get(key, "").strip()}
        for key, root in roots.items():
            if name in ROOT_NAMES:
                conflict = key != name and _overlaps(path, root)
            else:
                conflict = key in ROOT_NAMES[1:] and _overlaps(path, root)
            if conflict:
                return {**result, "status": "invalid_configuration", "reason": "overlapping_roots"}
        if role == "output":
            workspace = roots.get("AIRMOSAIC_LOCAL_WORKSPACE")
            if workspace is None:
                return {**result, "status": "missing_configuration", "reason": "workspace_not_set"}
            if not path.is_relative_to(workspace / "output"):
                return {**result, "status": "invalid_configuration", "reason": "output_outside_task_root"}
            if path.exists() and not path.is_dir():
                return {**result, "status": "invalid_configuration", "reason": "output_is_not_directory"}
            existing = next((parent for parent in (path, *path.parents) if parent.exists()), None)
            if existing is None or not existing.is_dir():
                return {**result, "status": "invalid_configuration", "reason": "output_ancestor_is_not_directory"}
        elif not (path.is_file() if spec["kind"] == "file" else path.is_dir()):
            status = "missing_data" if role in {"model", "input"} else "missing_configuration"
            return {**result, "status": status, "reason": "configured_location_missing"}
    except (OSError, ValueError, RuntimeError):
        return {**result, "status": "invalid_configuration", "reason": "path_unavailable_or_invalid"}
    return result


def check_readiness(tool: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Check only declared metadata and local prerequisites, without execution.

    No state is persisted. A profile directory is never used as login evidence.
    R libraries and task-specific data remain explicitly unverified.
    """
    checks: list[dict[str, Any]] = []
    entry = tool["entrypoint"]
    try:
        entry_exists = (repo_root / entry["path"]).is_file()
    except OSError:
        entry_exists = False
    checks.append({"kind": "entrypoint", "name": entry["path"],
                   "status": "available" if entry_exists else "missing_entrypoint"})
    checks.append({"kind": "python", "name": tool["requirements"]["python"],
                   "status": "available" if sys.version_info >= (3, 10) else "missing_dependency"})
    requirements = tool["requirements"]
    for name in requirements["python_packages"]:
        try:
            version = metadata.version(name)
            check = {"kind": "python_package", "name": name, "status": "available", "version": version}
        except metadata.PackageNotFoundError:
            check = {"kind": "python_package", "name": name, "status": "missing_dependency"}
        except (OSError, ValueError):
            check = {"kind": "python_package", "name": name, "status": "unverified"}
        checks.append(check)
    for name in requirements["executables"]:
        try:
            available = executable_available(name)
        except (OSError, ValueError):
            available = False
        checks.append({"kind": "executable", "name": name,
                       "status": "available" if available else "missing_dependency"})
    checks.extend({"kind": "r_package", "name": name, "status": "unverified"}
                  for name in requirements["r_packages"])
    configuration = [_configuration(spec, repo_root) for spec in requirements["configuration"]]
    checks.extend({"kind": "configuration", **check} for check in configuration)
    configured = {check["name"] for check in configuration if check["status"] == "configured"}
    for resource in requirements["resources"]:
        # Only fixed paths under declared, already checked non-secret roots.
        if resource["root"] not in configured:
            checks.append({"kind": "resource", "name": resource["root"], "status": "unverified"})
            continue
        label = "${" + resource["root"] + "}/" + resource["path"]
        try:
            root = local_path(os.environ[resource["root"]])
            path = local_path(str(root / resource["path"]))
            if not path.is_relative_to(root):
                state = "invalid_configuration"
            else:
                exists = path.is_file() if resource["kind"] == "file" else path.is_dir()
                state = "available" if exists else "missing_data"
        except (OSError, ValueError, RuntimeError):
            state = "invalid_configuration"
        checks.append({"kind": "resource", "name": label, "status": state})
    auth = tool["authentication"]
    authentication = {"method": auth["method"],
                      "status": "not_required" if auth["method"] == "none" else "unverified"}
    if auth["method"] != "none":
        authentication["profile_id"] = auth["profile_id"]
        checks.append({"kind": "authentication", "name": auth["profile_id"], "status": "needs_auth"})
    checks.extend({"kind": "manual", "name": name, "status": "unverified"}
                  for name in requirements["manual_checks"])
    statuses = {check["status"] for check in checks}
    if tool["implementation_status"] != "implemented":
        status = "not_executable"
    else:
        priority = ("missing_entrypoint", "invalid_configuration", "missing_dependency",
                    "missing_configuration", "missing_data", "needs_auth")
        status = next((item for item in priority if item in statuses),
                      "unknown" if "unverified" in statuses else "ready")
    next_steps = {
        "ready": "Prerequisites checked; supply task inputs and validate results before use.",
        "missing_entrypoint": "Restore the declared repository entrypoint.",
        "missing_dependency": "Install declared dependencies in the calling environment.",
        "missing_configuration": "Set declared non-secret path variables and prepare their directories.",
        "invalid_configuration": "Separate data/config/auth roots outside Git; use authorized local paths.",
        "missing_data": "Prepare the declared model/input resources in the authorized data root.",
        "needs_auth": "Verify login in the member's authorized browser; login has not been inspected.",
        "unknown": "Complete listed manual, R-library or task-data checks in an authorized environment.",
        "not_executable": "Read the guide and adapt the template/reference; no executable handler is registered.",
    }
    return {
        "tool_id": tool["tool_id"], "status": status,
        "scope": "static_prerequisites_only", "checks": checks,
        "authentication": authentication, "next_step": next_steps[status],
        "task_inputs_checked": False, "scientific_validation": "not_run",
    }
