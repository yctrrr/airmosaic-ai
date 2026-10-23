"""Validated repository tool declarations and read-only readiness checks."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from jsonschema import Draft202012Validator
import yaml

from .tool_readiness import check_readiness
from .tool_paths import local_path
from .tool_policies import ADAPTERS, PATH_PARAMETERS


CATEGORIES = {"core": "基础工具", "data_acquisition": "数据获取", "model": "模型分析"}
STATUSES = (
    "ready", "missing_entrypoint", "missing_dependency", "missing_configuration",
    "invalid_configuration", "missing_data", "needs_auth", "unknown", "not_executable",
)


class ToolRegistryError(ValueError):
    """A public, value-free error; never includes YAML excerpts or local paths."""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader: yaml.SafeLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str) or key in result:
            raise ToolRegistryError("Registry YAML has duplicate or non-string keys.")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping,
)


def _relative_reference(value: str) -> PurePosixPath:
    relative = PurePosixPath(value)
    if (
        not value or relative.is_absolute() or "\\" in value or ":" in value
        or any(part in {".", "..", ""} for part in value.split("/"))
    ):
        raise ToolRegistryError("Registry paths must be repository-relative.")
    return relative


def repository_path(root: Path, value: str) -> Path:
    """Resolve a public relative reference, rejecting traversal and link escapes."""
    _relative_reference(value)
    try:
        path = local_path(str(root / value))
        if not path.is_relative_to(root):
            raise ToolRegistryError("Registry path leaves the repository.")
    except (OSError, RuntimeError, ValueError):
        raise ToolRegistryError("Registry path is invalid or leaves the repository.") from None
    return path


def _no_schema_references(value: Any) -> None:
    # Embedded interface schemas describe data. They never resolve files or URLs.
    if isinstance(value, dict):
        if any(key in value for key in ("$ref", "$dynamicRef", "$id", "$schema")):
            raise ToolRegistryError("Embedded schemas cannot contain references or IDs.")
        for item in value.values():
            _no_schema_references(item)
    elif isinstance(value, list):
        for item in value:
            _no_schema_references(item)


class ToolRegistryService:
    """Load reviewed manifests; discovery never imports or invokes tools.

    Requires the source checkout (as with the dataset catalog). Personal config
    and authentication stores are never used to discover registrations.
    """

    def __init__(self, repo_root: str | Path | None = None) -> None:
        try:
            self.repo_root = local_path(str(Path(repo_root or Path(__file__).absolute().parents[3]).absolute()))
        except (OSError, ValueError, RuntimeError):
            raise ToolRegistryError("Tool repository requires an accessible local checkout.") from None
        schema_path = repository_path(self.repo_root, "catalog/schemas/tool.schema.json")
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        except Exception:
            raise ToolRegistryError("Tool registry schema is unavailable or invalid.") from None
        validator = Draft202012Validator(schema)
        registry_dir = repository_path(self.repo_root, "catalog/tools")
        try:
            manifests = sorted(registry_dir.glob("*.yaml"))
        except OSError:
            raise ToolRegistryError("Tool registry is unavailable.") from None
        if not manifests:
            raise ToolRegistryError("Tool registry contains no manifests.")
        self._tools: dict[str, dict[str, Any]] = {}
        for manifest in manifests:
            if not re.fullmatch(r"[a-z][a-z0-9_]*\.yaml", manifest.name):
                raise ToolRegistryError("Manifest filenames must use public tool identifiers.")
            source = manifest.relative_to(self.repo_root).as_posix()
            path = repository_path(self.repo_root, source)
            try:
                data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
                validator.validate(data)
                self._validate_interfaces(data)
            except ToolRegistryError as error:
                raise ToolRegistryError(f"{source}: {error}") from None
            except Exception:
                raise ToolRegistryError(f"{source}: Invalid manifest. Check the registry schema.") from None
            tool_id = data["tool_id"]
            if tool_id in self._tools:
                raise ToolRegistryError("Tool registry has duplicate tool IDs.")
            data["manifest"] = source
            self._tools[tool_id] = data

    def _validate_interfaces(self, data: dict[str, Any]) -> None:
        for field in ("input_schema", "output_schema"):
            _no_schema_references(data[field])
            Draft202012Validator.check_schema(data[field])
        defaults = data["entrypoint"].get("default_arguments", {})
        if defaults and data["entrypoint"]["kind"] in {"template", "reference"}:
            raise ToolRegistryError("Non-executable entries cannot supply invocation defaults.")
        for name, value in defaults.items():
            property_schema = data["input_schema"].get("properties", {}).get(name)
            if property_schema is None or not Draft202012Validator(property_schema).is_valid(value):
                raise ToolRegistryError("Default arguments must satisfy the input schema.")
            if not data["entrypoint"]["argument_bindings"].get(name, "").startswith("--"):
                raise ToolRegistryError("Invocation defaults require named options.")
        entry = data["entrypoint"]
        repository_path(self.repo_root, entry["path"])
        documentation = repository_path(self.repo_root, data["documentation"])
        if not documentation.is_file():
            raise ToolRegistryError("Tool documentation is missing.")
        if entry["kind"] in {"python_script", "r_script"}:
            suffix = ".py" if entry["kind"] == "python_script" else ".R"
            if not entry["path"].endswith(suffix):
                raise ToolRegistryError("Script kind and file extension disagree.")
        properties = data["input_schema"].get("properties", {})
        policy = data.get("execution", {"enabled": False})
        if policy["enabled"]:
            adapter = policy["adapter"]
            if (ADAPTERS.get(data["tool_id"]) != adapter
                    or policy["path_parameters"] != PATH_PARAMETERS[adapter]
                    or data["implementation_status"] != "implemented"
                    or entry["kind"] != ("cli" if adapter == "core_cli" else "python_script")
                    or not set(policy["path_parameters"]).issubset(properties)):
                raise ToolRegistryError("Execution policy does not match a reviewed adapter.")
            if adapter == "core_cli" and (entry.get("module") != "airmosaic_core.cli"
                    or entry.get("subcommand") != data["tool_id"].removeprefix("airmosaic_").replace("_", "-")):
                raise ToolRegistryError("CLI execution must match its reviewed subcommand.")
        if not set(data["input_schema"].get("required", [])).issubset(properties):
            raise ToolRegistryError("Required input names must be declared properties.")
        if set(entry["argument_bindings"]) != set(properties):
            raise ToolRegistryError("Argument bindings must match input properties.")
        bindings = list(entry["argument_bindings"].values())
        if len(bindings) != len(set(bindings)):
            raise ToolRegistryError("Argument bindings must be unique.")
        for resource in data["requirements"]["resources"]:
            # Validate lexical form without touching any local root.
            _relative_reference(resource["path"])

    def list_tools(
        self, category: str | None = None, skill: str | None = None,
        status: str | None = None, query: str | None = None,
    ) -> list[dict[str, Any]]:
        if category is not None and category not in CATEGORIES:
            raise ToolRegistryError("Unknown tool category.")
        if status is not None and status not in STATUSES:
            raise ToolRegistryError("Unknown tool status.")
        results = []
        for item in sorted(self._tools.values(), key=lambda x: (list(CATEGORIES).index(x["category"]), x["tool_id"])):
            if category is not None and item["category"] != category:
                continue
            if skill is not None and item["skill_id"] != skill:
                continue
            haystack = " ".join(item[key] for key in ("tool_id", "title", "description", "skill_id")).casefold()
            if query and not all(term.casefold() in haystack for term in query.split()):
                continue
            public = self.describe_tool(item["tool_id"])
            if status is None or public["availability"]["status"] == status:
                results.append(public)
        return results

    def describe_tool(self, tool_id: str) -> dict[str, Any]:
        try:
            result = deepcopy(self._tools[tool_id])
        except KeyError:
            raise ToolRegistryError("Tool not found.") from None
        entry = result["entrypoint"]
        prefixes = {
            "cli": ["python", "-m", "airmosaic_core.cli", entry.get("subcommand", "")],
            "python_script": ["python", entry["path"]],
            "r_script": ["Rscript", entry["path"]],
        }
        tokens = prefixes.get(entry["kind"], [])
        for name, value in entry.get("default_arguments", {}).items():
            binding = entry["argument_bindings"][name]
            tokens.extend([binding + value] if binding.endswith("=") else [binding, value])
        result["invocation"] = {
            "tokens": tokens,
            "working_directory": "repository_root",
            "argument_bindings": entry["argument_bindings"],
            "default_arguments": entry.get("default_arguments", {}),
            "execution_supported": result.get("execution", {}).get("enabled", False),
            "runner_tokens": (["python", "-m", "airmosaic_core.cli", "run-tool", tool_id]
                              if result.get("execution", {}).get("enabled") else []),
        }
        result["availability"] = self.check_tool(tool_id)
        return result

    def check_tool(self, tool_id: str) -> dict[str, Any]:
        if tool_id not in self._tools:
            raise ToolRegistryError("Tool not found.")
        return check_readiness(self._tools[tool_id], self.repo_root)


def format_tool_table(tools: list[dict[str, Any]]) -> str:
    """Compact categorized text; all path strings come from public manifests."""
    lines = []
    for category, title in CATEGORIES.items():
        items = [tool for tool in tools if tool["category"] == category]
        if not items:
            continue
        lines.append(f"[{title} / {category}]")
        for tool in items:
            entry = tool["entrypoint"]
            deps = tool["requirements"]
            dependency_names = ["Python " + deps["python"], *deps["python_packages"], *deps["executables"],
                                *("R:" + name for name in deps["r_packages"])]
            auth = tool["authentication"]
            login = "none" if auth["method"] == "none" else "browser_session (unverified)"
            state = tool["availability"]
            invocation = " ".join(tool["invocation"]["tokens"]) or entry["path"]
            lines.extend([
                f"{tool['tool_id']} | {tool['title']} | {state['status']}",
                f"  entry: {invocation}",
                f"  dependencies: {', '.join(dependency_names)}; login: {login}",
                f"  next: {state['next_step']}",
            ])
            runner = tool["invocation"]["runner_tokens"]
            lines.append("  runner: " + (" ".join(runner) if runner else "unsupported"))
        lines.append("")
    return "\n".join(lines).rstrip() if lines else "No matching tools."
