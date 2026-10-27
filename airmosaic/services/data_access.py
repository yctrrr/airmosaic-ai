from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .data_catalog import DataCatalogService
from .tool_paths import local_path
from .tool_readiness import _inside_git, _overlaps, ROOT_NAMES


@dataclass(frozen=True)
class FileAvailability:
    dataset_id: str
    cache_root: Path
    existing_files: list[Path]
    missing_hint: str | None


class DataAccessService:
    """Inspect catalog-defined caches; returned paths are for local use."""

    def __init__(
        self,
        catalog: DataCatalogService | None = None,
        assets_dir: str | Path | None = None,
    ) -> None:
        self.catalog = catalog or DataCatalogService()
        workspace = assets_dir or os.environ.get("AIRMOSAIC_ASSETS_DIR")
        if workspace is None or not str(workspace).strip():
            raise ValueError(
                "Set AIRMOSAIC_ASSETS_DIR or pass assets_dir explicitly."
            )
        try:
            self.assets_dir = local_path(str(workspace))
            if _inside_git(self.assets_dir):
                raise ValueError
            for name in ROOT_NAMES[1:]:
                value = os.environ.get(name, "")
                if value.strip() and _overlaps(self.assets_dir, local_path(value)):
                    raise ValueError
        except (OSError, ValueError, RuntimeError):
            raise ValueError("invalid_private_assets_root") from None

    def check_local_availability(
        self,
        dataset_id: str,
        pattern: str = "*",
    ) -> FileAvailability:
        if not isinstance(pattern, str) or pattern.startswith(("/", "\\")) or any(
            token in pattern for token in (":", "\\")
        ) or ".." in pattern.split("/"):
            raise ValueError("invalid_asset_pattern")
        dataset_id = self.catalog.resolve_dataset_id(dataset_id)
        metadata = self.catalog.describe_dataset(dataset_id)
        cache_root_template = metadata.get("cache_root") or metadata.get("default_cache_root")
        if cache_root_template is None:
            raise KeyError(f"Dataset metadata has no cache_root: {dataset_id}")
        try:
            cache_root = local_path(str(self._resolve_cache_root(cache_root_template)))
            if not cache_root.is_relative_to(self.assets_dir / "data") or _inside_git(cache_root):
                raise ValueError
            count = 0
            for directory, subdirs, filenames in os.walk(cache_root, followlinks=False):
                if _inside_git(Path(directory)):
                    raise ValueError
                for name in subdirs + filenames:
                    local_path(str(Path(directory) / name))
                    count += 1
                    if count > 10000:
                        raise ValueError
        except (OSError, ValueError, RuntimeError):
            raise ValueError("invalid_asset_data_path") from None
        files = (
            sorted(
                path
                for path in cache_root.glob(pattern)
                if path.is_file() and not path.name.startswith(".")
            )
            if cache_root.exists()
            else []
        )
        acquisition_skill = metadata.get("acquisition_skill") or metadata.get("skill_path", "the related acquisition skill")
        missing_hint = None if files else f"No files found under {cache_root}. Use {acquisition_skill}."
        return FileAvailability(
            dataset_id=dataset_id,
            cache_root=cache_root,
            existing_files=files,
            missing_hint=missing_hint,
        )

    def query_files(self, dataset_id: str, pattern: str = "*") -> list[Path]:
        return self.check_local_availability(dataset_id, pattern).existing_files

    def _resolve_cache_root(self, template: str) -> Path:
        value = template.replace("${AIRMOSAIC_ASSETS_DIR}", str(self.assets_dir))
        return Path(value)
