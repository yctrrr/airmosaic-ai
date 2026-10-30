"""Read-only inputs from explicitly authorized, licensed public data snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from .asset_layout import STAGES
from .tool_paths import local_path


def is_public_dataset(path: Path, repo_root: Path) -> bool:
    """Check public metadata and one selected CSV; never scan for data or secrets.

    The reviewed repository manifest supplies the publication authorization and
    license declaration. This check does not determine legal rights by itself.
    """
    try:
        root = local_path(str(repo_root / "assets"))
        if not path.is_relative_to(root):
            return False
        relative = path.relative_to(root)
        if (len(relative.parts) < 5 or relative.parts[0] != "data"
                or relative.parts[1] not in (STAGES[0], STAGES[2], STAGES[3])
                or path.suffix != ".csv" or any(part.casefold() in {
                    "auth", "secrets", "credentials", "browser_profiles", ".git", ".env", "records", "temp",
                } for part in relative.parts)):
            return False
        manifest = local_path(str(root / "public-data-manifest.json"))
        if manifest.stat().st_size > 65536:
            return False
        document = json.loads(manifest.read_text(encoding="utf-8"))
        if (not isinstance(document, dict) or document.get("schema_version") != 1
                or document.get("data_type") != "published_public_datasets"):
            return False
        datasets = document.get("datasets")
        if not isinstance(datasets, list) or len(datasets) > 64:
            return False
        selected = []
        for dataset in datasets:
            if not isinstance(dataset, dict) or not isinstance(dataset.get("files"), dict):
                return False
            entry = dataset["files"].get(relative.as_posix())
            if entry is not None:
                selected.append((dataset, entry))
        if len(selected) != 1:
            return False
        dataset, entry = selected[0]
        license = dataset.get("license")
        if (dataset.get("publication_authorized") is not True
                or not isinstance(license, dict) or license.get("id") not in {"CC-BY-4.0", "CC0-1.0"}
                or not isinstance(dataset.get("attribution"), str) or not dataset["attribution"].strip()
                or not isinstance(dataset.get("source"), str) or not dataset["source"].startswith("https://")
                or not isinstance(entry, dict) or type(entry.get("bytes")) is not int
                or not 0 < entry["bytes"] <= 64 * 1024 * 1024
                or not isinstance(entry.get("sha256"), str) or not re.fullmatch("[a-f0-9]{64}", entry["sha256"])):
            return False
        checked = local_path(str(path))
        for parent in (checked, *checked.parents):
            if not parent.is_relative_to(root):
                break
            if (parent / ".git").exists():
                return False
        if not checked.is_file() or checked.stat().st_size != entry["bytes"]:
            return False
        return hashlib.sha256(checked.read_bytes()).hexdigest() == entry["sha256"]
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        return False
