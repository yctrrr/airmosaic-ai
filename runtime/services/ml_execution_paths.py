"""Bounded ML outputs for skills, synthetic workflow checks and projects."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import re
import subprocess

from .asset_layout import STAGES
from .tool_execution_paths import ExecutionPaths, ToolExecutionError, checked_path, separated_roots
from .tool_readiness import _inside_git
from .toy_assets import is_public_toy


SKILL_RESULTS = "skills/model/shared/machine_learning_model/results"
WORKFLOW_RESULTS = "workflows/ml_regression/results"
RESERVED = {".airmosaic", ".git", ".env", "auth", "secrets", "credentials", "records", "temp", "browser_profiles"}


def workflow_result_name(task_name: str, instant: datetime | None = None) -> str:
    """Readable minute label; exclusive creation still rejects collisions."""
    if not isinstance(task_name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", task_name):
        raise ToolExecutionError("invalid_workflow_task_name")
    instant = instant or datetime.now(timezone.utc)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ToolExecutionError("workflow_time_requires_offset")
    return instant.strftime("%Y%m%d%H%M") + "_" + task_name


class MLExecutionPaths(ExecutionPaths):
    """No stage/tool tree is imposed on scientific output. Receipts are internal."""

    def __init__(self, repo_root: Path, run_id: str, tool_id: str,
                 project_id: str | None, stage: str | None, result_scope: str = "auto"):
        self.repo_root = repo_root
        self.roots = separated_roots(repo_root)
        self.assets = self.roots["AIRMOSAIC_ASSETS_DIR"]
        self.skill_results = checked_path(str(repo_root / SKILL_RESULTS))
        self.workflow_results = checked_path(str(repo_root / WORKFLOW_RESULTS))
        if not isinstance(result_scope, str) or result_scope not in {"auto", "skill", "workflow", "project"}:
            raise ToolExecutionError("invalid_result_scope")
        scope = ("project" if project_id is not None else "skill") if result_scope == "auto" else result_scope
        if scope == "project" and (not isinstance(project_id, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", project_id)):
            raise ToolExecutionError("invalid_project_id")
        if scope == "skill" and project_id is not None:
            raise ToolExecutionError("project_id_conflicts_with_skill_scope")
        if scope == "workflow" and project_id is not None:
            raise ToolExecutionError("project_id_conflicts_with_workflow_scope")
        if stage is not None and (stage not in STAGES or stage == STAGES[1]):
            raise ToolExecutionError("invalid_or_methods_only_stage")
        self.scope = scope
        self.base = (checked_path(str(self.assets / "results" / project_id)) if scope == "project"
                     else self.workflow_results if scope == "workflow" else self.skill_results)
        self.run_root = checked_path(str(self.base / ".airmosaic" / run_id))
        label = workflow_result_name("ml_regression") if scope == "workflow" else run_id
        self.output = checked_path(str(self.base / label))
        self.record_dir = self.run_root
        self.temp = checked_path(str(self.run_root / "temp"))
        self._check_storage(self.base)
        if self.run_root.exists():
            raise ToolExecutionError("run_id_already_exists")

    def _check_storage(self, path: Path) -> None:
        checked_path(str(path))
        if self.scope == "project":
            if not path.is_relative_to(self.base) or _inside_git(path):
                raise ToolExecutionError("project_output_outside_project_root")
        elif not path.is_relative_to(self.base):
            raise ToolExecutionError(self.scope + "_output_outside_results")
        else:
            for parent in (path, *path.parents):
                # Check ancestors above the result base too: a nested checkout
                # at workflows/<name> must not borrow the outer ignore rule.
                if parent == self.repo_root or not parent.is_relative_to(self.repo_root):
                    break
                if (parent / ".git").exists():
                    raise ToolExecutionError("nested_git_in_" + self.scope + "_results")
        if self.scope in {"skill", "workflow"} and _inside_git(path):
            # Only this fixed, explicitly ignored skill-owned subtree may hold
            # local real artifacts inside a checkout. Never arbitrary Git paths.
            try:
                relative = WORKFLOW_RESULTS if self.scope == "workflow" else SKILL_RESULTS
                probe = subprocess.run(["git", "check-ignore", "-q", "--", relative + "/"],
                                       cwd=self.repo_root, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL, timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                raise ToolExecutionError(self.scope + "_ignore_check_unavailable") from None
            if probe.returncode != 0:
                raise ToolExecutionError(self.scope + "_results_must_be_git_ignored")

    def expand(self, value: str) -> Path:
        value = value.replace("${ML_SKILL_RESULTS_DIR}", str(self.skill_results))
        value = value.replace("${ML_WORKFLOW_RESULTS_DIR}", str(self.workflow_results))
        if value.replace("\\", "/").startswith(SKILL_RESULTS + "/"):
            value = str(self.repo_root / value)
        if value.replace("\\", "/").startswith(WORKFLOW_RESULTS + "/"):
            value = str(self.repo_root / value)
        return super().expand(value)

    def parameter(self, value: str, role: str) -> Path:
        if role == "configuration_file":
            return self.parameter_file(value, self.repo_root)
        path = self.expand(value)
        if role == "input_file":
            if self.scope == "workflow":
                if not is_public_toy(path, self.repo_root):
                    raise ToolExecutionError("workflow_requires_manifest_listed_synthetic_input")
                return path
            if path.is_relative_to(self.skill_results):
                self._check_skill_input(path)
                return path
            return super().parameter(value, role)
        self._check_storage(path)
        if any(part.casefold() in RESERVED for part in path.relative_to(self.base).parts):
            raise ToolExecutionError("private_output_component")
        if role != "output_directory":
            raise ToolExecutionError("unsupported_ml_output_role")
        self.output = path
        return path

    def _check_skill_input(self, path: Path) -> None:
        # Check only the selected local artifact, never walk private results.
        for parent in path.parents:
            if not parent.is_relative_to(self.skill_results):
                break
            if (parent / ".git").exists():
                raise ToolExecutionError("nested_git_in_skill_results")
        if (any(part.casefold() in RESERVED for part in path.relative_to(self.skill_results).parts)
                or not path.is_file()):
            raise ToolExecutionError("skill_input_unavailable")

    def parameter_file(self, value: str, repo_root: Path) -> Path:
        if not Path(value).is_absolute() and value.replace("\\", "/").startswith("config/examples/"):
            return super().parameter_file(value, repo_root)
        path = self.expand(value)
        if self.scope == "workflow" and path.is_relative_to(self.workflow_results):
            self._check_storage(path)
            if (any(part.casefold() in RESERVED for part in path.relative_to(self.workflow_results).parts)
                    or path.suffix.lower() != ".json" or not path.is_file()):
                raise ToolExecutionError("workflow_configuration_unavailable")
            return path
        if path.is_relative_to(self.skill_results):
            self._check_skill_input(path)
            if path.suffix.lower() != ".json":
                raise ToolExecutionError("parameter_file_unavailable")
            return path
        return super().parameter_file(value, repo_root)

    def public_locations(self) -> dict[str, str]:
        base = ("${ML_SKILL_RESULTS_DIR}" if self.scope == "skill" else
                "${ML_WORKFLOW_RESULTS_DIR}" if self.scope == "workflow" else
                "${AIRMOSAIC_ASSETS_DIR}/results/<project_id>")
        return {"output": base + "/<output_directory>",
                "record": base + "/.airmosaic/" + self.run_root.name + "/record.json"}

    def create(self) -> None:
        self._check_storage(self.output)
        self._check_storage(self.run_root)
        self.run_root.mkdir(parents=True, exist_ok=False)
        self.temp.mkdir(exist_ok=False)
        self.output.mkdir(parents=True, exist_ok=True)
