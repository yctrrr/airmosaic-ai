"""Bounded static authoring checks. Never import or execute the inspected skill."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import stat

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
VERSION = re.compile(r"\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?\Z")
MAX_FILE = 256 * 1024


def linked(path: Path) -> bool:
    """Reject symlinks and Windows reparse points, including ancestor links."""
    return any(p.is_symlink() or bool(getattr(p.lstat(), "st_file_attributes", 0)
               & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024))
               for p in (path, *path.parents) if p.exists() or p.is_symlink())


def frontmatter(text: str) -> dict[str, str]:
    """Read the deliberately small scalar frontmatter profile, without YAML tags."""
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("frontmatter")
    header = text.split("\n---\n", 1)[0][4:]
    values: dict[str, str] = {}
    seen: set[str] = set()
    parent = ""
    for line in header.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"(  )?([a-z][a-z0-9_-]*):(?: (.*))?", line)
        if not match:
            raise ValueError("frontmatter-profile")
        indent, key, value = match.groups()
        if indent and parent != "metadata":
            raise ValueError("frontmatter-profile")
        full = f"metadata.{key}" if indent else key
        if full in seen:
            raise ValueError("duplicate-metadata")
        seen.add(full)
        if value is None:
            if key != "metadata" or indent:
                raise ValueError("frontmatter-profile")
            parent = key
            continue
        if not indent:
            parent = ""
        if value.startswith(("!", "&", "*", "{", "[", "|", ">")):
            raise ValueError("frontmatter-profile")
        if value.startswith('"'):
            try:
                scalar = json.loads(value)
            except ValueError:
                raise ValueError("frontmatter-profile") from None
            if not isinstance(scalar, str):
                raise ValueError("frontmatter-profile")
        elif value.startswith("'"):
            if len(value) < 2 or not value.endswith("'") or "'" in value[1:-1].replace("''", ""):
                raise ValueError("frontmatter-profile")
            scalar = value[1:-1].replace("''", "'")
        else:
            if (": " in value or re.search(r"(?:^|\s)#", value)
                    or value.lower() in {"true", "false", "null", "yes", "no", "on", "off", "~"}
                    or re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", value)):
                raise ValueError("frontmatter-profile")
            scalar = value
        if "\n" in scalar or "\r" in scalar:
            raise ValueError("frontmatter-profile")
        values[full] = scalar
    return values


def validate(skill: Path, repo: Path, published_name: str | None = None) -> dict:
    """Return fixed diagnostic codes only; avoid echoing untrusted file text."""
    errors: list[str] = []
    skill, repo = skill.absolute(), repo.absolute()
    if linked(skill) or linked(repo) or not skill.is_dir() or not repo.is_dir():
        return {"valid": False, "errors": ["unsafe-root"]}
    try:
        skill.resolve().relative_to(repo.resolve())
    except ValueError:
        return {"valid": False, "errors": ["outside-repository"]}
    skill, repo = skill.resolve(), repo.resolve()
    for ancestor in (skill, *skill.parents):
        if ancestor == repo:
            break
        if (ancestor / ".git").exists() or (ancestor / ".git").is_symlink():
            return {"valid": False, "errors": ["nested-repository"]}
    canonical = None
    files = []
    # Bounded to the selected skill; no repository-wide discovery.
    for count, path in enumerate(skill.rglob("*"), 1):
        if count > 200:
            errors.append("file-limit")
            break
        if path.name == ".git" or (path.is_dir() and ((path / ".git").exists() or (path / ".git").is_symlink())):
            return {"valid": False, "errors": ["nested-repository"]}
        if linked(path):
            errors.append("linked-resource")
            continue
        if path.is_file():
            files.append(path)
    for entry in ("SKILL.md", "SKILL_ZH.md"):
        path = skill / entry
        if not path.is_file() or linked(path):
            errors.append("missing-or-linked-entry")
            continue
        try:
            if path.stat().st_size > MAX_FILE:
                raise ValueError("size")
            content = path.read_text(encoding="utf-8")
            meta = frontmatter(content)
            name = meta.get("name", "")
            historical = name == published_name and re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,62}", name)
            if (not NAME.fullmatch(name) and not historical) or len(name) > 63:
                errors.append("invalid-name")
            if not 15 <= len(meta.get("description", "")) <= 1024:
                errors.append("invalid-description")
            if not VERSION.fullmatch(meta.get("metadata.version", "")):
                errors.append("invalid-version")
            if not meta.get("compatibility", "").strip():
                errors.append("missing-compatibility")
            if canonical is None:
                canonical = meta
            elif any(meta.get(k) != canonical.get(k) for k in ("name", "metadata.version", "compatibility")):
                errors.append("translation-metadata-mismatch")
            sibling = "SKILL_ZH.md" if entry == "SKILL.md" else "SKILL.md"
            reciprocal = list(re.finditer(r"(?<!!)\[[^\]]*\]\(" + re.escape(sibling) + r"\)", content))
            starts, ends = content.count("README-I18N:START"), content.count("README-I18N:END")
            marked = starts or ends
            balanced = (starts == ends == 1
                        and content.count("<!-- README-I18N:START -->") == 1
                        and content.count("<!-- README-I18N:END -->") == 1
                        and content.index("README-I18N:START") < content.index("README-I18N:END"))
            if (len(reciprocal) != 1 or (marked and not balanced)
                    or (marked and balanced and not (
                        content.index("README-I18N:START") < reciprocal[0].start()
                        < content.index("README-I18N:END")))):
                errors.append("language-selector")
            for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", content):
                if target.startswith(("https://", "http://", "#")):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                if ":" in target or "\\" in target or Path(target).is_absolute():
                    errors.append("unsafe-reference")
                    continue
                reference = path.parent / target
                try:
                    reference.resolve().relative_to(repo.resolve())
                    if linked(reference) or not reference.is_file():
                        errors.append("missing-or-linked-reference")
                except ValueError:
                    errors.append("reference-outside-repository")
        except (OSError, UnicodeError, ValueError):
            errors.append("unreadable-or-invalid-entry")
    for path in files:
        if "scripts" in path.relative_to(skill).parts and path.suffix == ".py":
            try:
                if path.stat().st_size > MAX_FILE:
                    raise ValueError("size")
                ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, SyntaxError, ValueError):
                errors.append("invalid-python-script")
    return {"valid": not errors, "errors": sorted(set(errors)), "files_checked": len(files),
            "scope": "selected-skill-static-only", "execution_verified": False}


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"valid":false,"errors":["invalid-arguments"]}\n')


def main() -> int:
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--skill", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--published-name", help="Explicit already-published identifier to preserve")
    args = parser.parse_args()
    try:
        result = validate(args.skill, args.repo_root, args.published_name)
    except (OSError, ValueError, RuntimeError):
        result = {"valid": False, "errors": ["static-check-failed"]}
    print(json.dumps(result))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
