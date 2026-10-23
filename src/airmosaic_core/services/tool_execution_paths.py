"""Path policy for reviewed tool adapters; no personal files are auto-loaded."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re

from .tool_paths import local_path
from .tool_readiness import ROOT_NAMES, _inside_git, _overlaps


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
    def __init__(self, repo_root: Path, run_id: str, tool_id: str):
        self.roots: dict[str, Path] = {}
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
        self.workspace = self.roots[ROOT_NAMES[0]]
        self.output = checked_path(str(self.workspace / "output" / run_id / tool_id))
        self.record_dir = checked_path(str(self.workspace / "runs" / run_id))
        self.temp = checked_path(str(self.workspace / "temp" / run_id))
        for path in (self.output.parent, self.record_dir, self.temp):
            if path.exists():
                raise ToolExecutionError("run_id_already_exists")

    def expand(self, value: str) -> Path:
        value = value.replace("${AIRMOSAIC_LOCAL_WORKSPACE}", str(self.workspace))
        if "${" in value:
            raise ToolExecutionError("unsupported_path_placeholder")
        return checked_path(value)

    def parameter(self, value: str, role: str) -> Path:
        path = self.expand(value)
        if role == "input_file":
            allowed = any(path.is_relative_to(self.workspace / base) for base in ("data_cache", "output"))
            relative = path.relative_to(self.workspace) if allowed else Path()
            reserved = {"auth", "secrets", "browser_profiles", ".git", ".env", "credentials"}
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
        for path in (self.output, self.record_dir, self.temp):
            checked_path(str(path))
            path.mkdir(parents=True, exist_ok=False)

    def read_parameters(self, value: str, repo_root: Path) -> dict:
        if not Path(value).is_absolute() and "${" not in value:
            if not value.replace("\\", "/").startswith("examples/"):
                raise ToolExecutionError("relative_parameter_file_requires_examples")
            value = str(repo_root / value)
        path = self.expand(value)
        allowed = (self.roots[ROOT_NAMES[1]], self.workspace / "data_cache",
                   self.workspace / "output", repo_root / "examples")
        if not any(path.is_relative_to(root) for root in allowed) or path.suffix.lower() != ".json":
            raise ToolExecutionError("parameter_file_outside_allowed_roots")
        if any(part.casefold() in {"auth", "secrets", "credentials", "browser_profiles", ".git"}
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
