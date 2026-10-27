"""Read-only access to explicitly published synthetic fixtures, never private links."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .tool_paths import local_path


def is_public_toy(path: Path, repo_root: Path) -> bool:
    """Verify one manifest-listed fixture before allowing a Git-contained input.

    The manifest is public source metadata. Only the selected, size-bounded
    fixture is opened; unlisted files and symlink/reparse ancestors are rejected.
    """
    root = local_path(str(repo_root / "assets"))
    if not path.is_relative_to(root):
        return False
    try:
        manifest = local_path(str(root / "toy-manifest.json"))
        if manifest.stat().st_size > 65536:
            return False
        document = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("schema_version") != 1 or document.get("synthetic") is not True:
            return False
        entries = document.get("files")
        if not isinstance(entries, dict):
            return False
        relative = path.relative_to(root).as_posix()
        parts = Path(relative).parts
        if not parts or parts[0] not in {"data", "results"} or path.suffix != ".csv" or any(
            part.casefold() in {"auth", "secrets", "credentials", "browser_profiles", ".git", "records", "temp"}
            for part in parts
        ):
            return False
        expected = entries.get(relative)
        if not isinstance(expected, str) or len(expected) != 64:
            return False
        checked = local_path(str(path))
        if checked.stat().st_size > 1024 * 1024 or not checked.is_file():
            return False
        return hashlib.sha256(checked.read_bytes()).hexdigest() == expected
    except (OSError, ValueError, TypeError, KeyError):
        return False
