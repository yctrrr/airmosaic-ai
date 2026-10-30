"""Reviewed adapters for the existing CLI, Python and R scripts.

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
import threading
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
from . import tool_r
from . import mlr3_workflow
from . import python_ml_workflow
from .ml_execution_paths import MLExecutionPaths


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
        argv += ["-m", "runtime.cli", entry["subcommand"]]
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
            timeout: int = 300, run_id: str | None = None,
            project_id: str | None = None, stage: str | None = None,
            result_scope: str = "auto",
            cancel_event: threading.Event | None = None) -> dict[str, Any]:
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
        if cancel_event is not None and not isinstance(cancel_event, threading.Event):
            raise ToolExecutionError("invalid_cancellation_signal")
        run_id = run_id if run_id is not None else uuid4().hex
        if not isinstance(run_id, str) or not re.fullmatch("[a-f0-9]{32}", run_id):
            raise ToolExecutionError("invalid_run_id")
        if policy["adapter"] in {"mlr3_regression", "ml_python_regression"}:
            paths = MLExecutionPaths(self.registry.repo_root, run_id, tool_id, project_id, stage, result_scope)
        else:
            if result_scope != "auto":
                raise ToolExecutionError("result_scope_not_supported_by_adapter")
            paths = ExecutionPaths(self.registry.repo_root, run_id, tool_id, project_id, stage)
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
        workflow_task, r_library = None, None
        if policy["adapter"] == "mlr3_regression":
            workflow_task = mlr3_workflow.validate_configuration(
                paths.read_parameters(params["task_config"], self.registry.repo_root), self.registry.repo_root)
            for role in mlr3_workflow.required_roles(workflow_task) | {"artifacts"}:
                mlr3_workflow.output_path(Path(params["out_dir"]), workflow_task["output_files"][role])
            r_library = mlr3_workflow.selected_library(paths)
            if Path(params["input_csv"]).stat().st_size > 64 * 1024 * 1024:
                raise ToolExecutionError("workflow_input_too_large")
        if policy["adapter"] == "ml_python_regression":
            try:
                workflow_task = python_ml_workflow.validate_configuration(
                    paths.read_parameters(params["task_config"], self.registry.repo_root), self.registry.repo_root)
            except (ValueError, TypeError, KeyError):
                raise ToolExecutionError("invalid_python_ml_configuration") from None
            for relative in python_ml_workflow.supported_outputs(workflow_task).values():
                mlr3_workflow.output_path(Path(params["out_dir"]), relative)
            mlr3_workflow.output_path(Path(params["out_dir"]), "artifacts.json")
            if Path(params["input_csv"]).stat().st_size > 64 * 1024 * 1024:
                raise ToolExecutionError("workflow_input_too_large")
            if workflow_task["execution"]["purpose"] == "engineering_replay":
                from .toy_assets import is_public_toy
                if not is_public_toy(Path(params["input_csv"]), self.registry.repo_root):
                    raise ToolExecutionError("engineering_replay_requires_manifest_synthetic_input")
                if "review_bundle" in params:
                    raise ToolExecutionError("review_bundle_conflicts_with_engineering_replay")
            else:
                from .model_plan_gate import inspect_python_review
                inspect_python_review(workflow_task, self.registry.repo_root, params.get("review_bundle"))
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
        is_r = policy["adapter"] in tool_r.R_ADAPTERS
        rscript = tool_r.r_executable() if is_r else None
        if is_r and rscript is None:
            blockers.append("missing_dependency")
        entry_path = repository_path(self.registry.repo_root, tool["entrypoint"]["path"])
        record = {
            "schema_version": 1, "run_id": run_id, "tool_id": tool_id,
            "status": "dry_run" if dry_run else "blocked", "created_at": _now(),
            "entrypoint": tool["entrypoint"]["path"], "adapter": policy["adapter"],
            "parameters": {key: tool["input_schema"]["properties"][key]["type"] for key in sorted(params)},
            "permissions": {"network": bool(allow_network), "browser_session_attested": bool(confirm_browser_session)},
            "authentication": "unverified" if tool["authentication"]["method"] != "none" else "not_required",
            "blockers": sorted(set(blockers)), "can_execute": not blockers,
            "locations": paths.public_locations(),
            "layout": "assets-v1",
            "research_stage": stage,
            "scientific_validation": "not_run",
        }
        if policy["adapter"] in {"mlr3_regression", "ml_python_regression"}:
            record.update(layout="ml-flex-v1", result_scope=paths.scope)
        if policy["adapter"] == "ml_python_regression":
            record["python_ml_dependencies"] = {"status": "unverified", "optional_shap":
                "requested" if "shap" in workflow_task["explanation"]["methods"] else "not_requested"}
            record["model_plan"] = ("engineering_replay_only" if workflow_task["execution"]["purpose"] ==
                                    "engineering_replay" else "control_records_checked_data_binding_pending")
        if is_r:
            record["r_dependencies"] = {"packages": tool["requirements"]["r_packages"],
                                        "status": "unverified"}
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
            env = child_environment(paths, model_root)
            if workflow_task is not None and policy["adapter"] == "mlr3_regression":
                params["task_config"] = str(mlr3_workflow.snapshot(
                    workflow_task, paths, params, self.registry.repo_root))
            if workflow_task is not None and policy["adapter"] == "ml_python_regression":
                for relative in [*python_ml_workflow.supported_outputs(workflow_task).values(), "artifacts.json"]:
                    if mlr3_workflow.output_path(Path(params["out_dir"]), relative).exists():
                        raise ToolExecutionError("artifact_already_exists")
                if workflow_task["execution"]["purpose"] == "new_study":
                    from .model_plan_gate import require_python_plan
                    record["model_review"] = require_python_plan(workflow_task, Path(params["input_csv"]),
                        entry_path, review_bundle=params.get("review_bundle"))
                    for name in ("AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
                        env[name] = str(paths.roots[name])
                frozen = paths.temp / "python-workflow-task.json"
                with frozen.open("x", encoding="utf-8", newline="\n") as handle:
                    json.dump(workflow_task, handle, ensure_ascii=False, indent=2, allow_nan=False)
                params["task_config"] = str(frozen)
                for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
                    env[name] = "1"
            if is_r:
                argv = tool_r.command(tool["entrypoint"], params, rscript)
                options = {"library": r_library} if r_library is not None else {}
                env = tool_r.environment(env, entry_path, tool["requirements"]["r_packages"],
                                         paths.temp, params.get("out_dir"), **options)
            else:
                argv = _argv(tool["entrypoint"], params, entry_path)
            cancellation = {"cancel_event": cancel_event} if cancel_event is not None else {}
            code, reason, cleanup, raw = execute(argv, paths.temp, env, timeout,
                                                capture=policy["adapter"] == "core_cli", **cancellation)
            record.update(exit_code=code, status="succeeded" if code == 0 and reason is None else "failed")
            if reason:
                record["reason"] = reason
            if cleanup is not None:
                record["process_tree_cleanup_confirmed"] = cleanup
            if record["status"] == "succeeded" and policy["adapter"] == "core_cli":
                record["result_summary"] = _core_summary(tool_id, raw)
            if policy["adapter"] == "ml_python_regression":
                if code == 0 and reason is None:
                    record["python_ml_dependencies"]["status"] = "available"
                    if not python_ml_workflow.validate_outputs(Path(params["out_dir"])):
                        record.update(status="failed", reason="workflow_output_contract_failed")
                elif code == 71 and reason is None:
                    record["reason"] = "python_regression_failed"
            if is_r and reason is None:
                if code == 70:
                    record["r_dependencies"]["status"] = "unavailable"
                    record["reason"] = "r_dependency_unavailable"
                elif code in (0, 71):
                    record["r_dependencies"]["status"] = "available"
                    if code == 71:
                        record["reason"] = "r_script_failed"
                if code == 0 and not tool_r.outputs_complete(
                        policy["adapter"], Path(params.get("output_dir", params.get("out_dir")))):
                    record.update(status="failed", reason="expected_outputs_missing")
                if code == 0 and workflow_task is not None and not mlr3_workflow.validate_outputs(Path(params["out_dir"])):
                    record.update(status="failed", reason="workflow_output_contract_failed")
        except ToolExecutionError as error:
            record.update(status="failed", reason=str(error))
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
        if tool_id == "gcam_plot_sector_change" and "," in params["input_csv"]:
            # The existing R parser splits every argument on commas, including
            # this filename. Reject ambiguity without changing its computation.
            raise ToolExecutionError("r_input_path_contains_comma")
        if tool_id == "gcam_inspect_output_structure":
            spec = {"name": "GCAM_RELEASE_DIR", "role": "model", "kind": "directory"}
            if _configuration(spec, self.registry.repo_root)["status"] != "configured":
                blockers.append("model_configuration_unavailable")
                return None
            model = checked_path(os.environ["GCAM_RELEASE_DIR"])
            if _overlaps(model, paths.assets):
                raise ToolExecutionError("model_overlaps_data_workspace")
            for relative, kind in (("output/database_basexdb", "directory"),
                                   ("database_R/Prov_code_china.csv", "file")):
                resource = checked_path(str(model / relative))
                if _inside_git(resource) or not (resource.is_dir() if kind == "directory" else resource.is_file()):
                    blockers.append("model_resource_unavailable")
            return model
        if tool_id.startswith("gcam_extract_"):
            if any(".." in item for item in params["scenarios"].split(",")):
                raise ToolExecutionError("invalid_scenario_identifier")
            spec = {"name": "GCAM_RELEASE_DIR", "role": "model", "kind": "directory"}
            if _configuration(spec, self.registry.repo_root)["status"] != "configured":
                blockers.append("model_configuration_unavailable")
                return None
            model = checked_path(os.environ["GCAM_RELEASE_DIR"])
            if _overlaps(model, paths.assets):
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
                if not root.is_relative_to(paths.assets / "data") or _inside_git(root):
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
