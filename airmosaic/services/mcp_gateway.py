"""Catalog-derived MCP data and policy; transport stays in mcp_server.

This module needs only the core dependencies. No credential store, personal
configuration file, original dataset or unregistered script is opened here.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import PurePosixPath
import re
import threading
from typing import Any

from jsonschema import Draft202012Validator
import yaml

from .data_catalog import DataCatalogService
from .tool_execution_paths import ToolExecutionError
from .tool_registry import ToolRegistryError, ToolRegistryService, repository_path
from .tool_runner import ToolRunnerService, _validate_values
from .asset_layout import STAGES


METADATA_TOOLS = frozenset({
    "airmosaic_list_tools", "airmosaic_describe_tool", "airmosaic_check_tool",
    "airmosaic_list_datasets", "airmosaic_describe_dataset", "airmosaic_search_datasets",
})
MAX_MESSAGE_BYTES = 1024 * 1024
RESULT_SCHEMA = {
    "type": "object",
    "properties": {"tool_id": {"type": "string"}, "mode": {"type": "string"},
                   "result": {}, "error": {"type": "string"}},
    "additionalProperties": False,
}


class MCPGatewayError(ValueError):
    """Fixed public error codes only; never include rejected values."""


@dataclass(frozen=True)
class MCPPolicy:
    """Operator-selected capabilities for this server process, not tool arguments."""

    execution_tools: frozenset[str] = frozenset()
    network_tools: frozenset[str] = frozenset()
    browser_tools: frozenset[str] = frozenset()
    max_timeout: int = 300
    browser_port: int | None = None


class MCPGateway:
    def __init__(self, registry: ToolRegistryService | None = None,
                 policy: MCPPolicy | None = None):
        self.registry = registry or ToolRegistryService()
        self.policy = policy or MCPPolicy()
        self.runner = ToolRunnerService(self.registry)
        self.catalog = DataCatalogService(
            catalog_dir=self.registry.repo_root / "catalog/datasets",
            data_acquisition_dir=self.registry.repo_root / "skills/data_acquisition",
        )
        self.entries = {name: deepcopy(tool) for name, tool in self.registry._tools.items()
                        if tool.get("execution", {}).get("enabled")}
        self._validate_policy()
        self.documents: dict[str, str] = {}
        self.skills = self._skill_index()

    def _validate_policy(self) -> None:
        p = self.policy
        sets = (p.execution_tools, p.network_tools, p.browser_tools)
        valid = (all(isinstance(s, frozenset) for s in sets)
                 and type(p.max_timeout) is int and 1 <= p.max_timeout <= 3600)
        if not valid:
            raise MCPGatewayError("invalid_server_policy")
        runnable = set(self.entries) - METADATA_TOOLS
        if (not p.execution_tools <= runnable or not p.network_tools <= p.execution_tools
                or not p.browser_tools <= p.network_tools):
            raise MCPGatewayError("invalid_server_policy")
        if any(not self.entries[n]["effects"]["network"] for n in p.network_tools):
            raise MCPGatewayError("invalid_server_policy")
        if any(self.entries[n]["authentication"]["method"] != "browser_session" for n in p.browser_tools):
            raise MCPGatewayError("invalid_server_policy")
        if bool(p.browser_tools) != (p.browser_port is not None) or (
                p.browser_port is not None and (type(p.browser_port) is not int or not 1 <= p.browser_port <= 65535)):
            raise MCPGatewayError("invalid_server_policy")

    def parameter_schema(self, tool_id: str) -> dict:
        entry = self.entries[tool_id]
        schema = deepcopy(entry["input_schema"])
        managed = {name for name, role in entry["execution"]["path_parameters"].items()
                   if role.startswith("output_")}
        if entry["authentication"]["method"] == "browser_session":
            managed.add("port")
        defaults = entry["entrypoint"].get("default_arguments", {})
        for name in managed:
            schema["properties"].pop(name, None)
        schema["required"] = [name for name in schema.get("required", [])
                              if name not in managed and name not in defaults]
        return schema

    def input_schema(self, tool_id: str) -> dict:
        parameters = self.parameter_schema(tool_id)
        if tool_id in METADATA_TOOLS:
            return parameters
        return {
            "type": "object", "properties": {
                "parameters": parameters,
                "dry_run": {"type": "boolean", "default": True},
                "timeout": {"type": "integer", "minimum": 1,
                            "maximum": self.policy.max_timeout,
                            "default": min(300, self.policy.max_timeout)},
                "run_id": {"type": "string", "pattern": "^[a-f0-9]{32}$"},
                "project_id": {"type": "string", "pattern": "^[a-z][a-z0-9_-]{0,63}$"},
                "stage": {"type": "string", "enum": list(STAGES)},
            }, "required": ["parameters", "project_id", "stage"], "additionalProperties": False,
        }

    def tools(self) -> list[dict]:
        result = []
        for name, entry in sorted(self.entries.items()):
            metadata = name in METADATA_TOOLS
            note = (" Read-only repository metadata query."
                    if metadata else " Uses a parameters object; dry_run defaults to true. "
                    "Real execution requires operator authorization at server startup.")
            result.append({
                "name": name, "title": entry["title"],
                "description": entry["description"] + note,
                "input_schema": self.input_schema(name), "output_schema": deepcopy(RESULT_SCHEMA),
                "annotations": {"read_only_hint": metadata,
                                "open_world_hint": bool(entry["effects"]["network"]),
                                "destructive_hint": False},
            })
        return result

    def call(self, name: str, arguments: dict | None,
             cancel_event: threading.Event | None = None) -> tuple[dict, bool]:
        # Do not echo unknown tool names, task text, schema failures or exceptions.
        if not isinstance(name, str) or name not in self.entries:
            return {"error": "tool_not_exposed"}, True
        try:
            if cancel_event is not None and cancel_event.is_set():
                raise MCPGatewayError("cancelled")
            arguments = {} if arguments is None else arguments
            if not isinstance(arguments, dict):
                raise MCPGatewayError("invalid_mcp_arguments")
            self.serialize(arguments)
            if not Draft202012Validator(self.input_schema(name)).is_valid(arguments):
                raise MCPGatewayError("invalid_mcp_arguments")
            if name in METADATA_TOOLS:
                _validate_values(arguments, self.parameter_schema(name))
                result, mode, error = self._metadata(name, arguments), "metadata", False
            else:
                parameters = dict(arguments["parameters"])
                _validate_values(parameters, self.parameter_schema(name))
                dry_run = arguments.get("dry_run", True)
                if not dry_run and name not in self.policy.execution_tools:
                    raise MCPGatewayError("execution_not_authorized")
                if name in self.policy.browser_tools:
                    parameters["port"] = self.policy.browser_port
                result = self.runner.run(
                    name, parameters, dry_run=dry_run,
                    allow_network=name in self.policy.network_tools,
                    confirm_browser_session=name in self.policy.browser_tools,
                    timeout=arguments.get("timeout", min(300, self.policy.max_timeout)),
                    run_id=arguments.get("run_id"), cancel_event=cancel_event,
                    project_id=arguments.get("project_id"), stage=arguments.get("stage"),
                )
                mode = "preview" if dry_run else "execution"
                error = result["status"] in {"blocked", "failed"}
            payload = {"tool_id": name, "mode": mode, "result": result}
            self.serialize(payload)
            return payload, error
        except (MCPGatewayError, ToolExecutionError) as error:
            return {"error": str(error)}, True
        except (ToolRegistryError, KeyError):
            return {"error": "catalog_query_failed"}, True
        except Exception:
            return {"error": "mcp_call_failed"}, True

    @staticmethod
    def serialize(value: Any) -> str:
        try:
            text = json.dumps(value, ensure_ascii=False, allow_nan=False)
            if len(text.encode("utf-8")) > MAX_MESSAGE_BYTES:
                raise MCPGatewayError("mcp_payload_too_large")
            return text
        except MCPGatewayError:
            raise
        except (ValueError, TypeError, RecursionError):
            raise MCPGatewayError("invalid_mcp_payload") from None

    def _metadata(self, name: str, args: dict) -> Any:
        if name == "airmosaic_list_tools":
            return self.registry.list_tools(**{k: v for k, v in args.items() if k != "format"})
        if name == "airmosaic_describe_tool":
            return self.registry.describe_tool(args["tool_id"])
        if name == "airmosaic_check_tool":
            return self.registry.check_tool(args["tool_id"])
        if name == "airmosaic_list_datasets":
            return [{key: getattr(item, key) for key in (
                "dataset_id", "name", "domain", "layer", "skill_id", "skill_path",
                "access_mode", "description")}
                for item in self.catalog.list_datasets(**args)]
        if name == "airmosaic_describe_dataset":
            return self.catalog.describe_dataset(args["dataset_id"])
        if name == "airmosaic_search_datasets":
            return [{key: getattr(item, key) for key in (
                "dataset_id", "name", "domain", "layer", "skill_id")}
                for item in self.catalog.search_datasets(args["query"])]
        raise MCPGatewayError("tool_not_exposed")

    def _skill_index(self) -> list[dict]:
        # Follow finite public method/entrypoint references, never rglob personal
        # directories or accept a client-supplied filesystem path.
        index_path = repository_path(self.registry.repo_root, "methods/index.yaml")
        methods = yaml.safe_load(index_path.read_text(encoding="utf-8"))
        candidates = {p for method in methods["methods"] for p in method.get("skills", [])}
        for entry in self.registry._tools.values():
            path = PurePosixPath(entry["entrypoint"]["path"])
            if path.parts[0] != "skills":
                continue
            for parent in path.parents:
                if parent == PurePosixPath("skills"):
                    break
                candidate = (parent / "SKILL.md").as_posix()
                if repository_path(self.registry.repo_root, candidate).is_file():
                    candidates.add(candidate)
                    break
        result, seen = [], set()
        for relative in sorted(candidates):
            if not relative.startswith("skills/") or not relative.endswith("/SKILL.md"):
                raise MCPGatewayError("invalid_skill_reference")
            body = self._public_text(relative)
            if not body.startswith("---"):
                raise MCPGatewayError("invalid_skill_reference")
            front = yaml.safe_load(body.split("---", 2)[1])
            name = front.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name) or name in seen:
                raise MCPGatewayError("invalid_skill_reference")
            if not isinstance(front.get("description"), str):
                raise MCPGatewayError("invalid_skill_reference")
            seen.add(name)
            locations = {}
            for language, path in (("en", relative), ("zh", relative.replace("SKILL.md", "SKILL_ZH.md"))):
                if repository_path(self.registry.repo_root, path).is_file():
                    uri = f"airmosaic://skills/{name}/{language}"
                    self.documents[uri] = path
                    locations[language] = uri
            result.append({"name": name, "description": front["description"],
                           "path": relative, "resources": locations})
        return result

    def _public_text(self, relative: str) -> str:
        path = repository_path(self.registry.repo_root, relative)
        if path.stat().st_size > MAX_MESSAGE_BYTES:
            raise MCPGatewayError("mcp_payload_too_large")
        return path.read_text(encoding="utf-8")

    def resources(self) -> list[dict]:
        return [
            {"uri": f"airmosaic://catalog/{name}", "name": name, "mime_type": "application/json"}
            for name in ("tools", "datasets", "skills")
        ] + [{"uri": uri, "name": uri.removeprefix("airmosaic://"), "mime_type": "text/markdown"}
             for uri in sorted(self.documents)]

    def read_resource(self, uri: str) -> tuple[str, str]:
        if uri == "airmosaic://catalog/tools":
            return self.serialize(self.registry.list_tools()), "application/json"
        if uri == "airmosaic://catalog/datasets":
            return self.serialize(self._metadata("airmosaic_list_datasets", {})), "application/json"
        if uri == "airmosaic://catalog/skills":
            return self.serialize(self.skills), "application/json"
        if uri in self.documents:
            return self._public_text(self.documents[uri]), "text/markdown"
        raise MCPGatewayError("resource_not_exposed")
