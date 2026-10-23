"""Reviewed adapters for the existing CLI and Python scripts.

This is a preflight and privacy layer, not an OS sandbox for untrusted code.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from uuid import uuid4

from jsonschema import Draft202012Validator

from .data_catalog import DataCatalogService
from .tool_execution_paths import ExecutionPaths, ToolExecutionError, checked_path
from .tool_process import child_environment, execute
from .tool_readiness import _configuration, _inside_git, _overlaps
from .tool_registry import ToolRegistryService, repository_path
from .tool_policies import ADAPTERS


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_values(parameters: dict, schema: dict) -> None:
    if not isinstance(parameters, dict) or any(
        not isinstance(key, str) or not isinstance(value, (str, int, float, bool))
        or isinstance(value, str) and (len(value) > 4096 or any(ord(char) < 32 for char in value))
        for key, value in parameters.items()
    ) or not Draft202012Validator(schema).is_valid(parameters):
        raise ToolExecutionError("invalid_tool_parameters")


def _argv(entry: dict, parameters: dict, script: Path) -> list[str]:
    argv = [sys.executable, "-I", "-B", "-X", "utf8"]
    if entry["kind"] == "cli":
        argv += ["-m", "airmosaic_core.cli", entry["subcommand"]]
    else:
        argv += [str(script)]
    positional = {}
    for name, value in parameters.items():
        binding = entry["argument_bindings"][name]
        if binding.startswith("positional:"):
            positional[int(binding.split(":")[1])] = str(value)
        elif isinstance(value, bool):
            if value:
                argv.append(binding.rstrip("="))
        else:
            argv.append(binding.rstrip("=") + "=" + str(value))
    if positional:
        argv += ["--", *(positional[index] for index in sorted(positional))]
    return argv


def _core_summary(tool_id: str, raw: bytes) -> dict:
    try:
        value = json.loads(raw)
        if isinstance(value, list):
            return {"item_count": len(value)}
        if tool_id == "airmosaic_check_availability":
            return {"matched_file_count": len(value["existing_files"])}
        if tool_id == "airmosaic_check_tool":
            states = {"ready", "missing_entrypoint", "missing_dependency", "missing_configuration",
                      "invalid_configuration", "missing_data", "needs_auth", "unknown", "not_executable"}
            return {"status": value["status"] if value["status"] in states else "unknown"}
        if tool_id == "airmosaic_draft_causal_plan":
            return {"template_created": True, "scientific_validation": "not_run"}
        return {"detail_available": isinstance(value, dict)}
    except (ValueError, TypeError, KeyError):
        raise ToolExecutionError("invalid_cli_result") from None


class ToolRunnerService:
    def __init__(self, registry: ToolRegistryService | None = None):
        self.registry = registry or ToolRegistryService()

    def run(self, tool_id: str, parameters: dict | None = None, *, params_file: str | None = None,
            dry_run: bool = False, allow_network: bool = False, confirm_browser_session: bool = False,
            timeout: int = 300, run_id: str | None = None) -> dict[str, Any]:
        if tool_id not in self.registry._tools:
            raise ToolExecutionError("unknown_tool")
        tool = self.registry._tools[tool_id]
        policy = tool.get("execution", {})
        if not policy.get("enabled") or ADAPTERS.get(tool_id) != policy.get("adapter"):
            raise ToolExecutionError("execution_not_supported")
        if type(timeout) is not int or not 1 <= timeout <= 3600:
            raise ToolExecutionError("invalid_timeout")
        if any(type(flag) is not bool for flag in (dry_run, allow_network, confirm_browser_session)):
            raise ToolExecutionError("invalid_permission_flags")
        run_id = run_id if run_id is not None else uuid4().hex
        if not isinstance(run_id, str) or not re.fullmatch("[a-f0-9]{32}", run_id):
            raise ToolExecutionError("invalid_run_id")
        paths = ExecutionPaths(self.registry.repo_root, run_id, tool_id)
        if params_file is not None:
            if parameters is not None:
                raise ToolExecutionError("conflicting_parameter_sources")
            parameters = paths.read_parameters(params_file, self.registry.repo_root)
        if parameters is not None and not isinstance(parameters, dict):
            raise ToolExecutionError("parameters_must_be_object")
        supplied = dict(parameters or {})
        params = {**tool["entrypoint"].get("default_arguments", {}), **supplied}
        for name, role in policy["path_parameters"].items():
            if role.startswith("output_") and name not in params:
                params[name] = str(paths.output / "results.csv" if role == "output_file" else paths.output)
        _validate_values(params, tool["input_schema"])
        for name, role in policy["path_parameters"].items():
            if name in params:
                params[name] = str(paths.parameter(params[name], role))
        blockers: list[str] = []
        if tool["effects"]["network"] and not allow_network:
            blockers.append("network_permission_required")
        if tool["authentication"]["method"] != "none" and not confirm_browser_session:
            blockers.append("browser_session_confirmation_required")
        readiness = self.registry.check_tool(tool_id)
        # Configuration is validated independently; auth is an attestation, never
        # a readiness/login claim. Manual model inputs are checked below.
        for check in readiness["checks"]:
            if check["kind"] in {"entrypoint", "python", "python_package", "executable"} and check["status"] != "available":
                blockers.append("missing_entrypoint" if check["kind"] == "entrypoint" else "missing_dependency")
        model_root = self._adapter_preflight(tool_id, params, paths, blockers)
        entry_path = repository_path(self.registry.repo_root, tool["entrypoint"]["path"])
        record = {
            "schema_version": 1, "run_id": run_id, "tool_id": tool_id,
            "status": "dry_run" if dry_run else "blocked", "created_at": _now(),
            "entrypoint": tool["entrypoint"]["path"], "adapter": policy["adapter"],
            "parameters": {key: tool["input_schema"]["properties"][key]["type"] for key in sorted(params)},
            "permissions": {"network": bool(allow_network), "browser_session_attested": bool(confirm_browser_session)},
            "authentication": "unverified" if tool["authentication"]["method"] != "none" else "not_required",
            "blockers": sorted(set(blockers)), "can_execute": not blockers,
            "locations": {"output": f"${{AIRMOSAIC_LOCAL_WORKSPACE}}/output/{run_id}/{tool_id}",
                          "record": f"${{AIRMOSAIC_LOCAL_WORKSPACE}}/runs/{run_id}/record.json"},
            "scientific_validation": "not_run",
        }
        if dry_run:
            return record
        # These digests are public source, never hashes of private arguments.
        try:
            record["source_sha256"] = hashlib.sha256(entry_path.read_bytes()).hexdigest() if entry_path.is_file() else None
            manifest = repository_path(self.registry.repo_root, tool["manifest"])
            record["manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
            paths.create()
            self._write(paths, record, first=True)
        except (OSError, ValueError):
            raise ToolExecutionError("run_initialization_failed") from None
        if blockers:
            return record
        record["status"], record["started_at"] = "running", _now()
        self._write(paths, record)
        started = time.monotonic()
        try:
            for name, role in policy["path_parameters"].items():
                if role.startswith("output_"):
                    target = checked_path(params[name])
                    (target.parent if role == "output_file" else target).mkdir(parents=True, exist_ok=True)
            code, reason, cleanup, raw = execute(_argv(tool["entrypoint"], params, entry_path), paths.temp,
                                                child_environment(paths, model_root), timeout,
                                                capture=policy["adapter"] == "core_cli")
            record.update(exit_code=code, status="succeeded" if code == 0 and reason is None else "failed")
            if reason:
                record["reason"] = reason
            if cleanup is not None:
                record["process_tree_cleanup_confirmed"] = cleanup
            if record["status"] == "succeeded" and policy["adapter"] == "core_cli":
                record["result_summary"] = _core_summary(tool_id, raw)
        except (OSError, ValueError):
            record.update(status="failed", reason="execution_or_result_error")
        except KeyboardInterrupt:
            record.update(status="failed", reason="interrupted")
        record.update(finished_at=_now(), duration_seconds=round(time.monotonic() - started, 3))
        self._write(paths, record)
        return record

    @staticmethod
    def _write(paths: ExecutionPaths, record: dict, first: bool = False) -> None:
        try:
            destination = checked_path(str(paths.record_dir / "record.json"))
            # The directory is exclusively owned by this invocation; no raw logs.
            temporary = destination if first else checked_path(str(paths.record_dir / ".record.json.tmp"))
            with temporary.open("x", encoding="utf-8") as handle:
                json.dump(record, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            if not first:
                temporary.replace(destination)
        except (OSError, ValueError):
            raise ToolExecutionError("receipt_write_failed") from None

    def _adapter_preflight(self, tool_id: str, params: dict, paths: ExecutionPaths, blockers: list) -> Path | None:
        if tool_id.startswith("gcam_extract_"):
            if any(".." in item for item in params["scenarios"].split(",")):
                raise ToolExecutionError("invalid_scenario_identifier")
            spec = {"name": "GCAM_RELEASE_DIR", "role": "model", "kind": "directory"}
            if _configuration(spec, self.registry.repo_root)["status"] != "configured":
                blockers.append("model_configuration_unavailable")
                return None
            model = checked_path(os.environ["GCAM_RELEASE_DIR"])
            if _overlaps(model, paths.workspace):
                raise ToolExecutionError("model_overlaps_data_workspace")
            jars = checked_path(str(model / "libs" / "jars"))
            candidates = list(jars.glob("BaseX-*.jar")) if jars.is_dir() else []
            if not candidates or any(not checked_path(str(path)).is_file() for path in candidates):
                blockers.append("basex_jar_unavailable")
            for scenario in params["scenarios"].split(","):
                database = checked_path(str(model / "output" / scenario / "database_basexdb"))
                if not database.is_dir() or _inside_git(database):
                    blockers.append("scenario_database_unavailable")
            return model
        if tool_id == "airmosaic_check_availability":
            pattern = params.get("pattern", "*")
            if pattern.startswith(("/", "\\")) or ":" in pattern or "\\" in pattern or ".." in pattern.split("/"):
                raise ToolExecutionError("invalid_cache_pattern")
            catalog = DataCatalogService(catalog_dir=self.registry.repo_root / "catalog/datasets",
                                         data_acquisition_dir=self.registry.repo_root / "skills/data_acquisition")
            try:
                metadata = catalog.describe_dataset(params["dataset_id"])
                root = paths.expand(metadata.get("cache_root") or metadata["default_cache_root"])
                if not root.is_relative_to(paths.workspace / "data_cache") or _inside_git(root):
                    raise ToolExecutionError("cache_outside_data_root")
                # A bounded preflight prevents the legacy glob from following a
                # linked directory/file into another root. No file is opened.
                count = 0
                for directory, subdirs, files in os.walk(root, followlinks=False):
                    if _inside_git(Path(directory)):
                        raise ToolExecutionError("git_directory_in_cache")
                    for name in subdirs + files:
                        checked_path(str(Path(directory) / name))
                        count += 1
                        if count > 10000:
                            raise ToolExecutionError("cache_preflight_limit")
            except (KeyError, OSError):
                raise ToolExecutionError("dataset_cache_unavailable") from None
        return None
