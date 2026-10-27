"""Path policy for reviewed tool adapters; no personal files are auto-loaded."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re

from .tool_paths import local_path
from .tool_readiness import ROOT_NAMES, _inside_git, _overlaps
from .asset_layout import execution_context
from .toy_assets import is_public_toy


class ToolExecutionError(ValueError):
    """A fixed public error code, never an exception containing task values."""


def checked_path(value: str) -> Path:
    try:
        # Reject alternate data streams and ambiguous Windows component aliases.
        path = Path(value)
        for part in path.parts[1:]:
            if ":" in part or part.endswith((".", " ")) or re.match(
                r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", part, re.I,
            ):
                raise ValueError
        return local_path(value)
    except (OSError, ValueError, RuntimeError):
        raise ToolExecutionError("invalid_local_path") from None


class ExecutionPaths:
    def __init__(self, repo_root: Path, run_id: str, tool_id: str,
                 project_id: str | None = None, stage: str | None = None):
        try:
            project_id, stage = execution_context(project_id, stage)
        except ValueError as error:
            raise ToolExecutionError(str(error)) from None
        self.roots: dict[str, Path] = {}
        self.repo_root = repo_root
        for name in ROOT_NAMES:
            value = os.environ.get(name, "")
            if not value.strip():
                raise ToolExecutionError("missing_separated_roots")
            root = checked_path(value)
            if not root.is_dir() or _inside_git(root) or _overlaps(root, repo_root):
                raise ToolExecutionError("invalid_separated_roots")
            if any(_overlaps(root, other) for other in self.roots.values()):
                raise ToolExecutionError("overlapping_roots")
            self.roots[name] = root
        self.assets = self.roots[ROOT_NAMES[0]]
        self.run_root = checked_path(str(self.assets / "results" / project_id / run_id))
        self.output = checked_path(str(self.run_root / stage / tool_id))
        self.record_dir = checked_path(str(self.run_root / "records" / tool_id))
        self.temp = checked_path(str(self.run_root / "temp" / tool_id))
        if any(_inside_git(path) for path in (self.run_root, self.output, self.record_dir, self.temp)):
            raise ToolExecutionError("generated_paths_inside_git")
        if self.run_root.exists():
            raise ToolExecutionError("run_id_already_exists")

    def public_locations(self) -> dict[str, str]:
        """Use a project placeholder so private project labels stay out of receipts."""
        def public(path: Path) -> str:
            relative = path.relative_to(self.assets).as_posix()
            parts = relative.split("/")
            parts[1] = "<project_id>"
            relative = "/".join(parts)
            return "${AIRMOSAIC_ASSETS_DIR}/" + relative
        return {"output": public(self.output), "record": public(self.record_dir / "record.json")}

    def expand(self, value: str) -> Path:
        value = value.replace("${AIRMOSAIC_ASSETS_DIR}", str(self.assets))
        if "${" in value:
            raise ToolExecutionError("unsupported_path_placeholder")
        if value.startswith("assets/"):
            value = str(self.repo_root / value)
        return checked_path(value)

    def parameter(self, value: str, role: str) -> Path:
        path = self.expand(value)
        if role == "input_file":
            if path.is_relative_to(self.repo_root / "assets"):
                if is_public_toy(path, self.repo_root):
                    return path
                raise ToolExecutionError("unlisted_or_changed_toy_asset")
            allowed = any(path.is_relative_to(self.assets / base) for base in ("data", "results"))
            relative = path.relative_to(self.assets) if allowed else Path()
            reserved = {"auth", "secrets", "browser_profiles", ".git", ".env", "credentials", "records", "temp"}
            if not allowed or any(part.casefold() in reserved for part in relative.parts):
                raise ToolExecutionError("input_outside_data_roots")
            if _inside_git(path) or not path.is_file():
                raise ToolExecutionError("input_file_unavailable")
        else:
            if not path.is_relative_to(self.output) or _inside_git(path):
                raise ToolExecutionError("output_outside_current_task")
            if role == "output_file" and path == self.output:
                raise ToolExecutionError("output_file_required")
        return path

    def create(self) -> None:
        # Recheck ancestors immediately before exclusive creation. This is a
        # preflight against mistakes, not protection from hostile concurrent IO.
        if any(_inside_git(checked_path(str(path))) for path in (self.run_root, self.output, self.record_dir, self.temp)):
            raise ToolExecutionError("generated_paths_inside_git")
        checked_path(str(self.run_root)).mkdir(parents=True, exist_ok=False)
        for path in (self.output, self.record_dir, self.temp):
            checked_path(str(path))
            path.mkdir(parents=True, exist_ok=False)

    def read_parameters(self, value: str, repo_root: Path) -> dict:
        if not Path(value).is_absolute() and "${" not in value:
            if not value.replace("\\", "/").startswith("config/examples/"):
                raise ToolExecutionError("relative_parameter_file_requires_examples")
            value = str(repo_root / value)
        path = self.expand(value)
        allowed = (self.roots[ROOT_NAMES[1]], *(self.assets / base for base in ("data", "results")), repo_root / "config/examples")
        if not any(path.is_relative_to(root) for root in allowed) or path.suffix.lower() != ".json":
            raise ToolExecutionError("parameter_file_outside_allowed_roots")
        if not path.is_relative_to(repo_root / "config/examples") and _inside_git(path):
            raise ToolExecutionError("parameter_file_inside_git")
        if any(part.casefold() in {"auth", "secrets", "credentials", "browser_profiles", ".git", "records", "temp"}
               for part in path.relative_to(next(root for root in allowed if path.is_relative_to(root))).parts):
            raise ToolExecutionError("private_parameter_file")
        try:
            if path.stat().st_size > 1024 * 1024:
                raise ToolExecutionError("parameters_too_large")
            with path.open(encoding="utf-8-sig") as handle:
                return parse_parameters(handle.read(1024 * 1024 + 1))
        except (OSError, UnicodeError):
            raise ToolExecutionError("parameter_file_unavailable") from None


def parse_parameters(value: str) -> dict:
    def unique(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ToolExecutionError("duplicate_parameter")
            result[key] = item
        return result
    if len(value.encode("utf-8")) > 1024 * 1024:
        raise ToolExecutionError("parameters_too_large")
    try:
        result = json.loads(value, object_pairs_hook=unique,
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, RecursionError):
        raise ToolExecutionError("invalid_parameters_json") from None
    if not isinstance(result, dict):
        raise ToolExecutionError("parameters_must_be_object")
    return result
