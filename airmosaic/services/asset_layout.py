"""Shared data and project-scoped result paths; no files are read or migrated."""

from __future__ import annotations

import re


STAGES = (
    "01_socioeconomic_natural_change",
    "02_emission_inventory",
    "03_atmospheric_transport",
    "04_integrated_impacts",
)


def execution_context(project_id: str | None, stage: str | None) -> tuple[str | None, str | None]:
    """Require explicit project/stage context for every recorded execution."""
    if project_id is None:
        raise ValueError("project_id_required")
    if not isinstance(project_id, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", project_id):
        raise ValueError("invalid_project_id")
    if stage not in STAGES:
        raise ValueError("invalid_research_stage")
    if stage == STAGES[1]:
        raise ValueError("stage_is_methods_only")
    return project_id, stage
