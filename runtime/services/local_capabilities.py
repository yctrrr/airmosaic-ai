"""Explicit local-only capability selection; no network, discovery or code loading."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .tool_paths import local_path


class LocalCapabilityError(ValueError):
    """Value-free error: private filenames and JSON excerpts never leave this layer."""


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    try:
        with path.open("rb") as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError
        value = json.loads(raw, object_pairs_hook=_pairs)
        if not isinstance(value, dict):
            raise ValueError
        return value
    except (OSError, ValueError, RuntimeError):
        raise LocalCapabilityError("invalid_local_capabilities_configuration") from None


class LocalCapabilities:
    """One operator-selected, reviewed extension confined to public reserved slots.

    Paths are supplied only in the selected non-secret configuration file.
    Scripts are never read/imported here. This is not OS isolation.
    """

    def __init__(self, repo: Path, config: str | Path):
        from .tool_registry import repository_path
        self.repo = repo
        try:
            config_path = local_path(str(config))
            if (config_path.is_relative_to(repo) or config_path.suffix != ".json"
                    or any(part.casefold() in {"auth", "credentials", "secrets", ".ssh", ".aws", ".git"}
                           for part in config_path.parts)):
                raise ValueError
            if os.environ.get("AIRMOSAIC_AUTH_DIR") and config_path.is_relative_to(
                    local_path(os.environ["AIRMOSAIC_AUTH_DIR"])):
                raise ValueError
            settings = read_json(config_path)
            if set(settings) != {"schema_version", "root"} or settings["schema_version"] != 1:
                raise ValueError
            if not isinstance(settings["root"], str) or not Path(settings["root"]).is_absolute():
                raise ValueError
            self.root = local_path(settings["root"])
            self.config_path = config_path
            if (not self.root.is_dir() or self.root.is_relative_to(repo)
                    or repo.is_relative_to(self.root) or config_path.is_relative_to(self.root)):
                raise ValueError
            for name in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
                if os.environ.get(name):
                    protected = local_path(os.environ[name])
                    if self.root.is_relative_to(protected) or protected.is_relative_to(self.root):
                        raise ValueError
            allowed = read_json(repository_path(repo, "catalog/local-capabilities.json"))
            actual = read_json(repository_path(self.root, "capabilities.json"))
            if (set(actual) != {"schema_version", "extension_id", "files"}
                    or actual["schema_version"] != 1 or actual["extension_id"] != allowed["extension_id"]
                    or not isinstance(actual["files"], list) or len(actual["files"]) > 256
                    or any(not isinstance(v, str) for v in actual["files"])
                    or len(set(actual["files"])) != len(actual["files"])
                    or set(actual["files"]) != set(allowed["files"])):
                raise ValueError
            self.files = frozenset(actual["files"])
            self.tool_ids = frozenset(allowed["tool_ids"])
            for relative in self.files:
                if any(part.casefold() in {"auth", "secrets", "credentials", ".ssh", ".git"}
                       for part in Path(relative).parts):
                    raise ValueError
                if not repository_path(self.root, relative).is_file():
                    raise ValueError
        except (OSError, ValueError, RuntimeError, KeyError, TypeError):
            raise LocalCapabilityError("invalid_local_capabilities_configuration") from None

    def path(self, relative: str) -> Path:
        from .tool_registry import repository_path
        return repository_path(self.root if relative in self.files else self.repo, relative)
