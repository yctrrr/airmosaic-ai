"""Synthetic metadata fixtures; no data, configuration or skill script execution."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime.services.capability_catalog import (
    CapabilityCatalogError, CapabilityCatalogService, MAX_DOCUMENT_BYTES,
)


@pytest.fixture
def registry(tmp_path):
    paths = {
        "methods/method.md": "# Method\n## Assumptions\nDeclared in prose only.\n",
        "methods/index.yaml": yaml.safe_dump({"schema_version": 2, "methods": [{
            "method_id": "example", "title": "Example", "document": "method.md",
            "skills": ["skills/model/shared/example/SKILL.md"], "tool_ids": ["example_tool"],
            "evidence": "synthetic_fixture_declaration", "assumptions": ["fixed boundary"]}]}),
        "catalog/skills.yaml": "schema_version: 1\npurpose: Public references\nskills: []\n",
        "skills/model/shared/example/SKILL.md": "---\nname: example\ndescription: Example fixture\n"
            "metadata:\n  version: '1.0'\n---\n# Example\n## Validation\nUse `scripts/helper.py`.\n",
        "skills/model/shared/example/scripts/helper.py": "raise RuntimeError('must never run')\n",
    }
    for relative, body in paths.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return SimpleNamespace(repo_root=tmp_path, _tools={"example_tool": {
        "tool_id": "example_tool", "version": "1.2", "implementation_status": "implemented",
        "entrypoint": {"path": "skills/model/shared/example/scripts/helper.py", "kind": "python_script"},
        "execution": {"enabled": True}}})


def test_metadata_projection_does_not_promote_evidence_or_execute(registry, monkeypatch):
    original = Path.open
    def restricted(path, *args, **kwargs):
        assert path.suffix != ".py", "discovery opened a script"
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", restricted)
    catalog = CapabilityCatalogService(registry)
    skill = catalog.describe("skill", "example")
    method = catalog.describe("method", "example")
    assert skill["version"] == "1.0" and len(skill["content_sha256"]) == 64
    assert skill["method_ids"] == ["example"]
    assert skill["registration_status"] == "registered_tools_present"
    assert skill["execution_readiness"] == "not_checked"
    assert skill["declarations"]["scientific_evidence"]["status"] == "not_declared"
    assert skill["documented_scripts"][0]["execution_tool_ids"] == ["example_tool"]
    assert method["declarations"]["assumptions"]["status"] == "declared"
    assert method["evidence_claim"]["status"] == "declared"
    assert method["scientific_acceptance"] == "not_assessed"
    assert catalog.validate()["scope"] == "metadata_consistency_only"
    assert str(registry.repo_root) not in json.dumps(catalog.snapshot())
    skill["name"] = "changed"
    assert catalog.describe("skill", "example")["name"] == "example"


@pytest.mark.parametrize("relative", [
    "../private-marker.md", "C:/private-marker.md", "//private-marker/a", "skills/../../private-marker",
    "skills/./example.md", "skills/a\\private-marker.md", "catalog/tools/example.yaml",
    "assets/private-marker.csv", "config/private-marker.yaml",
])
def test_public_reads_reject_private_or_noncanonical_paths(registry, relative):
    catalog = CapabilityCatalogService(registry)
    with pytest.raises(CapabilityCatalogError) as error:
        catalog.public_text(relative)
    assert "private-marker" not in str(error.value)


def test_nested_git_rejected_on_each_read(registry):
    catalog = CapabilityCatalogService(registry)
    (registry.repo_root / "methods/.git").write_text("gitdir: synthetic-location", encoding="utf-8")
    with pytest.raises(CapabilityCatalogError, match="nested_repository_reference"):
        catalog.public_text("methods/method.md")


def test_support_documents_require_an_explicit_skill_link(registry):
    directory = registry.repo_root / "skills/model/shared/example"
    (directory / "references").mkdir()
    (directory / "references/operations.md").write_text("# Public operations\n", encoding="utf-8")
    (directory / "references/unlisted.md").write_text("# Not indexed\n", encoding="utf-8")
    skill = directory / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") +
                     "[Operations](references/operations.md)\n", encoding="utf-8")
    catalog = CapabilityCatalogService(registry)
    support = catalog.describe("skill", "example")["supporting_documents"]
    assert [item["path"] for item in support] == [
        "skills/model/shared/example/references/operations.md"]
    assert catalog.public_text(catalog.documents[support[0]["uri"]]).splitlines() == ["# Public operations"]
    assert not any("unlisted" in path for path in catalog.documents.values())


@pytest.mark.parametrize("private", ["auth", "credentials", "secrets", ".ssh", ".aws"])
def test_protected_document_directories_never_read(registry, private):
    path = registry.repo_root / "skills/model/shared/example" / private / "private.md"
    path.parent.mkdir()
    path.write_text("private-marker", encoding="utf-8")
    catalog = CapabilityCatalogService(registry)
    with pytest.raises(CapabilityCatalogError, match="invalid_public_reference"):
        catalog.public_text(path.relative_to(registry.repo_root).as_posix())


def test_method_translation_is_exposed_only_when_explicitly_indexed(registry):
    translated = registry.repo_root / "methods/method_ZH.md"
    translated.write_text("# Synthetic translated method\n", encoding="utf-8")
    initial = CapabilityCatalogService(registry)
    assert "zh" not in initial.describe("method", "example")["resources"]
    index_path = registry.repo_root / "methods/index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    index["methods"][0]["supporting_documents"] = ["method_ZH.md"]
    index_path.write_text(yaml.safe_dump(index), encoding="utf-8")
    registered = CapabilityCatalogService(registry)
    uri = registered.describe("method", "example")["resources"]["zh"]
    assert uri == "airmosaic://methods/example/zh"
    assert registered.documents[uri] == "methods/method_ZH.md"


def test_symlink_rejected_without_reading_target(registry):
    catalog = CapabilityCatalogService(registry)
    link = registry.repo_root / "methods/link.md"
    try:
        link.symlink_to(registry.repo_root / "methods/method.md")
    except OSError:
        pytest.skip("host does not permit synthetic symlinks")
    with pytest.raises(CapabilityCatalogError):
        catalog.public_text("methods/link.md")


def test_oversized_document_rejected(registry):
    (registry.repo_root / "methods/method.md").write_bytes(b"x" * (MAX_DOCUMENT_BYTES + 1))
    with pytest.raises(CapabilityCatalogError, match="public_document_unavailable"):
        CapabilityCatalogService(registry)


@pytest.mark.parametrize("mutation", ["duplicate_method", "duplicate_skill", "duplicate_yaml", "missing_tool", "missing_skill", "traversal"])
def test_invalid_registration_fails_closed(registry, mutation):
    path = registry.repo_root / "methods/index.yaml"
    index = yaml.safe_load(path.read_text(encoding="utf-8"))
    if mutation == "duplicate_method":
        index["methods"].append(index["methods"][0].copy())
    elif mutation == "duplicate_skill":
        extra = registry.repo_root / "skills/model/shared/second/SKILL.md"
        extra.parent.mkdir()
        extra.write_text((registry.repo_root / "skills/model/shared/example/SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
        index["methods"][0]["skills"].append(extra.relative_to(registry.repo_root).as_posix())
    elif mutation == "duplicate_yaml":
        path.write_text("schema_version: 2\nschema_version: 2\nmethods: []\n", encoding="utf-8")
    elif mutation == "missing_tool":
        index["methods"][0]["tool_ids"] = ["unknown"]
    elif mutation == "missing_skill":
        index["methods"][0]["skills"] = ["skills/missing/SKILL.md"]
    else:
        index["methods"][0]["document"] = "../private-marker.md"
    if mutation != "duplicate_yaml":
        path.write_text(yaml.safe_dump(index), encoding="utf-8")
    with pytest.raises(CapabilityCatalogError) as error:
        CapabilityCatalogService(registry)
    assert "private-marker" not in str(error.value)


def test_direct_script_presence_does_not_enable_execution(registry):
    registry._tools.clear()
    path = registry.repo_root / "methods/index.yaml"
    index = yaml.safe_load(path.read_text(encoding="utf-8"))
    index["methods"][0]["tool_ids"] = []
    path.write_text(yaml.safe_dump(index), encoding="utf-8")
    skill = CapabilityCatalogService(registry).skills[0]
    assert skill["registration_status"] == "documentation_only"
    assert skill["tools"] == []
    assert skill["documented_scripts"][0]["exists"]
    assert skill["documented_scripts"][0]["execution_tool_ids"] == []


def test_fresh_snapshot_reads_current_document(registry):
    first = CapabilityCatalogService(registry).skills[0]
    path = registry.repo_root / first["path"]
    path.write_text(path.read_text(encoding="utf-8").replace("'1.0'", "'2.0'"), encoding="utf-8")
    second = CapabilityCatalogService(registry).skills[0]
    assert second["version"] == "2.0" and first["content_sha256"] != second["content_sha256"]
