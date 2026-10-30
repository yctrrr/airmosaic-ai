"""Read-only projection of authoritative method, skill and tool declarations.

Discovery validates public metadata, not scientific results or execution readiness.
Only finite declared documents are read; scripts are never imported or executed.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import posixpath
from pathlib import PurePosixPath
import re
from urllib.parse import unquote

import yaml

from .tool_registry import ToolRegistryError, ToolRegistryService, _UniqueKeyLoader, repository_path


MAX_DOCUMENT_BYTES = 1024 * 1024
MAX_ENTRIES = 1000
MAX_SKILL_SUPPORT_DOCS = 64
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,64}")
DECLARATIONS = ("research_question", "disciplinary_basis", "assumptions", "applicability",
                "implementation", "scientific_evidence")


class CapabilityCatalogError(ValueError):
    """Fixed public codes; rejected values and YAML excerpts are never exposed."""


class CapabilityCatalogService:
    """Build a fresh metadata snapshot from the existing authoritative sources."""

    def __init__(self, registry: ToolRegistryService | None = None):
        self.registry = registry or ToolRegistryService()
        self.root = self.registry.repo_root
        self.documents: dict[str, str] = {}
        self.methods: list[dict] = []
        self.skills: list[dict] = []
        self._load()

    def public_text(self, relative: str) -> str:
        # Only canonical public documentation namespaces, never arbitrary paths.
        if (not isinstance(relative, str) or not relative.startswith(("methods/", "skills/"))
                and relative != "catalog/skills.yaml"):
            raise CapabilityCatalogError("invalid_public_reference")
        if any(part.casefold() in {"auth", "credentials", "secrets", ".ssh", ".aws", ".git"}
               for part in PurePosixPath(relative).parts):
            raise CapabilityCatalogError("invalid_public_reference")
        try:
            path = repository_path(self.root, relative)
            for ancestor in (path, *path.parents):
                if ancestor == self.root:
                    break
                if (ancestor / ".git").exists() or (ancestor / ".git").is_symlink():
                    raise CapabilityCatalogError("nested_repository_reference")
            if not path.is_file() or path.stat().st_size > MAX_DOCUMENT_BYTES:
                raise CapabilityCatalogError("public_document_unavailable")
            # Bounded read also rejects a file enlarged after stat.
            with path.open("rb") as stream:
                raw = stream.read(MAX_DOCUMENT_BYTES + 1)
            if len(raw) > MAX_DOCUMENT_BYTES:
                raise CapabilityCatalogError("public_document_unavailable")
            return raw.decode("utf-8")
        except CapabilityCatalogError:
            raise
        except (OSError, ValueError, RuntimeError, ToolRegistryError):
            raise CapabilityCatalogError("public_document_unavailable") from None

    @staticmethod
    def _yaml(text: str) -> dict:
        try:
            if any(isinstance(token, yaml.tokens.AliasToken) for token in yaml.scan(text)):
                raise ValueError
            value = yaml.load(text, Loader=_UniqueKeyLoader)
            # Reject alias cycles, complex values and excessively expanded metadata.
            if not isinstance(value, dict) or len(json.dumps(value, allow_nan=False)) > MAX_DOCUMENT_BYTES:
                raise ValueError
            return value
        except Exception:
            raise CapabilityCatalogError("invalid_capability_metadata") from None

    @staticmethod
    def _identifier(value) -> str:
        if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
            raise CapabilityCatalogError("invalid_capability_identifier")
        return value

    @staticmethod
    def _references(value) -> list[str]:
        if (not isinstance(value, list) or len(value) > MAX_ENTRIES
                or not all(isinstance(v, str) for v in value) or len(set(value)) != len(value)):
            raise CapabilityCatalogError("invalid_capability_references")
        return value

    @staticmethod
    def _declarations(value: dict) -> dict:
        # Presence is a declaration only. Never turn prose/filenames into verification.
        return {key: {"status": "declared", "value": deepcopy(value[key])}
                if value.get(key) else {"status": "not_declared"}
                for key in DECLARATIONS}

    def _document(self, relative: str, uri: str) -> tuple[str, str]:
        body = self.public_text(relative)
        self.documents[uri] = relative
        return body, hashlib.sha256(body.encode("utf-8")).hexdigest()

    @staticmethod
    def _sections(body: str) -> list[str]:
        return [line.lstrip("# ").strip() for line in body.splitlines()
                if re.match(r"^#{1,6} ", line)]

    def _script_references(self, body: str, directory: str) -> list[dict]:
        # References in documentation are not registrations or verified implementations.
        # Do not enumerate directories or open script contents.
        references = sorted(set(re.findall(r"(?<![\w/])scripts/[A-Za-z0-9_./-]+\.(?:py|R)\b",
                                          body.replace(directory, ""))))
        result = []
        for reference in references:
            relative = directory + reference
            try:
                path = repository_path(self.root, relative)
                for ancestor in (path, *path.parents):
                    if ancestor == self.root:
                        break
                    if (ancestor / ".git").exists() or (ancestor / ".git").is_symlink():
                        raise ValueError
            except (ToolRegistryError, OSError, ValueError):
                raise CapabilityCatalogError("invalid_script_reference") from None
            result.append({"path": relative, "source": "documentation_reference",
                "exists": path.is_file(), "execution_tool_ids": sorted(
                    t["tool_id"] for t in self.registry._tools.values()
                    if t["entrypoint"]["path"] == relative and t.get("execution", {}).get("enabled")),
                "readiness": "not_checked", "scientific_acceptance": "not_assessed"})
        return result

    def _tool_summary(self, tool_id: str) -> dict:
        if tool_id not in self.registry._tools:
            raise CapabilityCatalogError("unknown_mapped_tool")
        item = self.registry._tools[tool_id]
        return {"tool_id": tool_id, "version": item.get("version", "not_declared"),
                "implementation_status": item["implementation_status"],
                "registration_status": item.get("registration_status", "not_declared"),
                "entrypoint": deepcopy(item["entrypoint"]),
                "execution_registered": bool(item.get("execution", {}).get("enabled")),
                "readiness": "not_checked", "scientific_acceptance": "not_assessed"}

    def _skill_support(self, name: str, directory: str, bodies: list[str]) -> list[dict]:
        """Expose explicitly linked Markdown inside this skill, without scanning."""
        selected: set[str] = set()
        for body in bodies:
            for link in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", body):
                target = unquote(link.split("#", 1)[0])
                if (not target or ":" in target or "\\" in target
                        or target.startswith("/") or not target.endswith(".md")):
                    continue
                relative = posixpath.normpath(directory + target)
                if (relative.startswith(directory) and relative not in {
                        directory + "SKILL.md", directory + "SKILL_ZH.md"}):
                    selected.add(relative)
        if len(selected) > MAX_SKILL_SUPPORT_DOCS:
            raise CapabilityCatalogError("too_many_support_documents")
        result = []
        for index, relative in enumerate(sorted(selected)):
            uri = f"airmosaic://skills/{name}/support/{index}"
            _, digest = self._document(relative, uri)
            result.append({"path": relative, "uri": uri, "content_sha256": digest})
        return result

    def _load(self) -> None:
        index = self._yaml(self.public_text("methods/index.yaml"))
        records = index.get("methods")
        if index.get("schema_version") != 2 or not isinstance(records, list) or len(records) > MAX_ENTRIES:
            raise CapabilityCatalogError("invalid_method_index")
        candidates: set[str] = set()
        method_ids: set[str] = set()
        for source in records:
            if not isinstance(source, dict):
                raise CapabilityCatalogError("invalid_method_index")
            name = self._identifier(source.get("method_id"))
            if name in method_ids:
                raise CapabilityCatalogError("duplicate_method_id")
            method_ids.add(name)
            document = source.get("document")
            if not isinstance(document, str) or not document.endswith(".md"):
                raise CapabilityCatalogError("invalid_method_document")
            relative = "methods/" + document
            resources = {"en": f"airmosaic://methods/{name}/en"}
            body, digest = self._document(relative, resources["en"])
            supporting = self._references(source.get("supporting_documents", []))
            for number, support in enumerate(supporting):
                if not support.endswith(".md"):
                    raise CapabilityCatalogError("invalid_method_document")
                uri = f"airmosaic://methods/{name}/support/{number}"
                self._document("methods/" + support, uri)
                resources[f"support_{number}"] = uri
                # Language routing follows an explicit indexed sibling, not a scan.
                if support == document.removesuffix(".md") + "_ZH.md":
                    translated_uri = f"airmosaic://methods/{name}/zh"
                    self.documents[translated_uri] = "methods/" + support
                    resources["zh"] = translated_uri
            skills = self._references(source.get("skills", []))
            tools = self._references(source.get("tool_ids", []))
            candidates.update(skills)
            self.methods.append({"method_id": name, "title": source.get("title"),
                "path": relative, "version": source.get("version", "not_declared"),
                "content_sha256": digest, "declared_status": source.get("status", "not_declared"),
                "evidence_claim": {"status": "declared", "value": deepcopy(source["evidence"])}
                    if source.get("evidence") else {"status": "not_declared"},
                "declarations": self._declarations(source), "skill_paths": skills,
                "document_sections": self._sections(body),
                "tools": [self._tool_summary(t) for t in tools], "resources": resources,
                "scientific_acceptance": "not_assessed"})
        extra = self._yaml(self.public_text("catalog/skills.yaml"))
        if extra.get("schema_version") != 1 or set(extra) != {"schema_version", "purpose", "skills"}:
            raise CapabilityCatalogError("invalid_skill_index")
        candidates.update(self._references(extra.get("skills")))
        # Tool manifests are authoritative for tool-to-skill ownership; no glob/rglob.
        for entry in self.registry._tools.values():
            path = PurePosixPath(entry["entrypoint"]["path"])
            if path.parts[0] != "skills":
                continue
            for parent in path.parents:
                if parent == PurePosixPath("skills"):
                    break
                candidate = (parent / "SKILL.md").as_posix()
                try:
                    if repository_path(self.root, candidate).is_file():
                        candidates.add(candidate)
                        break
                except ToolRegistryError:
                    raise CapabilityCatalogError("invalid_public_reference") from None
        if len(candidates) > MAX_ENTRIES:
            raise CapabilityCatalogError("too_many_capabilities")
        seen: set[str] = set()
        for relative in sorted(candidates):
            if not relative.startswith("skills/") or not relative.endswith("/SKILL.md"):
                raise CapabilityCatalogError("invalid_skill_reference")
            body = self.public_text(relative)
            parts = body.split("---", 2)
            if not body.splitlines() or body.splitlines()[0] != "---" or len(parts) != 3:
                raise CapabilityCatalogError("invalid_skill_frontmatter")
            front = self._yaml(parts[1])
            name = self._identifier(front.get("name"))
            if name in seen:
                raise CapabilityCatalogError("duplicate_skill_id")
            seen.add(name)
            if not isinstance(front.get("description"), str):
                raise CapabilityCatalogError("invalid_skill_frontmatter")
            metadata = front.get("metadata", {})
            if not isinstance(metadata, dict):
                raise CapabilityCatalogError("invalid_skill_frontmatter")
            resources = {"en": f"airmosaic://skills/{name}/en"}
            bodies = [body]
            _, digest = self._document(relative, resources["en"])
            sibling = relative.removesuffix("SKILL.md") + "SKILL_ZH.md"
            if repository_path(self.root, sibling).is_file():
                resources["zh"] = f"airmosaic://skills/{name}/zh"
                translated, _ = self._document(sibling, resources["zh"])
                bodies.append(translated)
            directory = relative.removesuffix("SKILL.md")
            supporting = self._skill_support(name, directory, bodies)
            owned = [t["tool_id"] for t in self.registry._tools.values()
                     if t["entrypoint"]["path"].startswith(directory)]
            self.skills.append({"name": name, "description": front["description"],
                "path": relative, "version": metadata.get("version", "not_declared"),
                "content_sha256": digest, "resources": resources,
                "compatibility": front.get("compatibility", "not_declared"),
                "declarations": self._declarations(metadata),
                "document_sections": self._sections(body),
                "supporting_documents": supporting,
                "documented_scripts": self._script_references(body, directory),
                "method_ids": [m["method_id"] for m in self.methods if relative in m["skill_paths"]],
                "tools": [self._tool_summary(t) for t in sorted(owned)],
                "registration_status": "registered_tools_present" if any(
                    self.registry._tools[t].get("execution", {}).get("enabled") for t in owned)
                    else "catalogued_reference" if owned else "documentation_only",
                "execution_readiness": "not_checked", "scientific_acceptance": "not_assessed"})

    def snapshot(self) -> dict:
        return deepcopy({"schema_version": 1,
            "sources": ["methods/index.yaml", "catalog/skills.yaml", "catalog/tools/*.yaml", "canonical SKILL.md"],
            "validation_scope": "metadata_consistency_only", "scientific_acceptance": "not_assessed",
            "methods": self.methods, "skills": self.skills})

    def describe(self, kind: str, identifier: str) -> dict:
        entries, field = (self.methods, "method_id") if kind == "method" else (self.skills, "name")
        if kind not in {"method", "skill"}:
            raise CapabilityCatalogError("unknown_capability_kind")
        for entry in entries:
            if entry[field] == identifier:
                return deepcopy(entry)
        raise CapabilityCatalogError("capability_not_found")

    def validate(self) -> dict:
        return {"status": "valid", "scope": "metadata_consistency_only",
                "methods": len(self.methods), "skills": len(self.skills),
                "tools": len(self.registry._tools), "scripts_executed": False,
                "dependencies_checked": False, "scientific_acceptance": "not_assessed"}
