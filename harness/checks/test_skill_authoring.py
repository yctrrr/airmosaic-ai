"""Static validator checks against synthetic skill folders only."""
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py"
spec = importlib.util.spec_from_file_location("skill_authoring_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def create_skill(tmp_path):
    skill = tmp_path / "published_folder"
    skill.mkdir()
    for filename, sibling in (("SKILL.md", "SKILL_ZH.md"), ("SKILL_ZH.md", "SKILL.md")):
        (skill / filename).write_text('---\nname: synthetic-check\ndescription: Validate a synthetic skill example.\ncompatibility: Python 3.10+\nmetadata:\n  version: "1.0.0"\n---\n\n<!-- README-I18N:START -->\n[Language](' + sibling + ')\n<!-- README-I18N:END -->\n', encoding="utf-8")
    return skill


def test_valid_metadata_preserves_distinct_folder_and_identifier(tmp_path):
    skill = create_skill(tmp_path)
    result = validator.validate(skill, tmp_path)
    assert result["valid"] and result["execution_verified"] is False


def test_plain_reciprocal_language_selectors_need_no_markers(tmp_path):
    skill = create_skill(tmp_path)
    for entry in (skill / "SKILL.md", skill / "SKILL_ZH.md"):
        content = entry.read_text(encoding="utf-8")
        entry.write_text(content.replace("<!-- README-I18N:START -->\n", "").replace("<!-- README-I18N:END -->\n", ""), encoding="utf-8")
    assert validator.validate(skill, tmp_path)["valid"]


@pytest.mark.parametrize("selector", [
    "[Language](SKILL_ZH.md)\n[Duplicate](SKILL_ZH.md)",
    "<!-- README-I18N:START -->\n[Language](SKILL_ZH.md)",
    "[Language](SKILL_ZH.md)\n<!-- README-I18N:END -->",
    "<!-- README-I18N:END -->\n[Language](SKILL_ZH.md)\n<!-- README-I18N:START -->",
    "<!-- README-I18N:START -->\n<!-- README-I18N:START -->\n[Language](SKILL_ZH.md)\n<!-- README-I18N:END -->",
    "<!-- README-I18N:START -->\n<!-- README-I18N:END -->\n[Language](SKILL_ZH.md)",
    "<!-- README-I18N:START -->\n[Language](SKILL_ZH.md)\n<!-- README-I18N:END -->\n<!-- README-I18N:END -->",
])
def test_duplicate_or_unbalanced_selectors_refused(tmp_path, selector):
    skill = create_skill(tmp_path)
    entry = skill / "SKILL.md"
    header = entry.read_text(encoding="utf-8").split("<!-- README-I18N:START -->", 1)[0]
    entry.write_text(header + selector + "\n", encoding="utf-8")
    assert "language-selector" in validator.validate(skill, tmp_path)["errors"]


def test_python_syntax_checked_without_execution(tmp_path):
    skill = create_skill(tmp_path)
    (skill / "scripts").mkdir()
    (skill / "scripts/check.py").write_text("raise RuntimeError('must never execute')")
    assert validator.validate(skill, tmp_path)["valid"]
    (skill / "scripts/check.py").write_text("def broken(")
    assert "invalid-python-script" in validator.validate(skill, tmp_path)["errors"]


def test_missing_reference_and_traversal_are_fixed_codes(tmp_path):
    skill = create_skill(tmp_path)
    with (skill / "SKILL.md").open("a") as handle:
        handle.write("[missing](missing.md)\n[escape](../../TEST_ONLY_PRIVATE_VALUE.md)\n")
    result = validator.validate(skill, tmp_path)
    assert "missing-or-linked-reference" in result["errors"]
    assert "reference-outside-repository" in result["errors"]
    assert "TEST_ONLY_PRIVATE_VALUE" not in str(result)


def test_version_compatibility_and_translations_checked(tmp_path):
    skill = create_skill(tmp_path)
    entry = skill / "SKILL_ZH.md"
    entry.write_text(entry.read_text().replace('version: "1.0.0"', 'version: "2.0.0"').replace("compatibility: Python 3.10+\n", ""))
    errors = validator.validate(skill, tmp_path)["errors"]
    assert "missing-compatibility" in errors and "translation-metadata-mismatch" in errors


def test_duplicate_metadata_rejected(tmp_path):
    skill = create_skill(tmp_path)
    entry = skill / "SKILL.md"
    entry.write_text(entry.read_text().replace("name: synthetic-check", "name: synthetic-check\nname: second-name"))
    assert "unreadable-or-invalid-entry" in validator.validate(skill, tmp_path)["errors"]


@pytest.mark.parametrize("name", ['"synthetic-check', "'synthetic-check", '"synthetic-check" trailing', "'synthetic'check'"])
def test_unbalanced_and_invalid_quoted_scalars_refused(tmp_path, name):
    skill = create_skill(tmp_path)
    entry = skill / "SKILL.md"
    entry.write_text(entry.read_text().replace("name: synthetic-check", "name: " + name))
    assert "unreadable-or-invalid-entry" in validator.validate(skill, tmp_path)["errors"]


@pytest.mark.parametrize("description", ["Validate synthetic: metadata outputs.", "# A comment is not a string value", "true", "12345678901234567890"])
def test_plain_scalar_yaml_ambiguities_require_quotes(tmp_path, description):
    skill = create_skill(tmp_path)
    entry = skill / "SKILL.md"
    entry.write_text(entry.read_text().replace("description: Validate a synthetic skill example.", "description: " + description))
    assert "unreadable-or-invalid-entry" in validator.validate(skill, tmp_path)["errors"]


def test_duplicate_metadata_mapping_refused(tmp_path):
    skill = create_skill(tmp_path)
    entry = skill / "SKILL.md"
    entry.write_text(entry.read_text().replace('  version: "1.0.0"', '  version: "1.0.0"\nmetadata:\n  other: value'))
    assert "unreadable-or-invalid-entry" in validator.validate(skill, tmp_path)["errors"]


def test_nested_repository_is_not_parsed(tmp_path):
    skill = create_skill(tmp_path)
    nested = skill / "scripts/other-checkout"
    nested.mkdir(parents=True)
    (nested / ".git").write_text("gitdir: synthetic-only")
    (nested / "invalid.py").write_text("def broken(")
    assert validator.validate(skill, tmp_path)["errors"] == ["nested-repository"]


def test_selected_skill_inside_nested_checkout_refused(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / ".git").write_text("gitdir: synthetic-only")
    skill = create_skill(nested)
    assert validator.validate(skill, tmp_path)["errors"] == ["nested-repository"]


def test_outside_selected_repository_refused(tmp_path):
    skill = create_skill(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    assert validator.validate(skill, other)["errors"] == ["outside-repository"]


def test_historical_identifier_requires_explicit_preservation(tmp_path):
    skill = create_skill(tmp_path)
    for entry in (skill / "SKILL.md", skill / "SKILL_ZH.md"):
        entry.write_text(entry.read_text().replace("name: synthetic-check", "name: published_identifier"))
    assert not validator.validate(skill, tmp_path)["valid"]
    assert validator.validate(skill, tmp_path, "published_identifier")["valid"]


def test_linked_resource_refused(tmp_path):
    skill = create_skill(tmp_path)
    try:
        (skill / "linked.md").symlink_to(skill / "SKILL.md")
    except OSError:
        pytest.skip("OS does not grant symlink creation")
    assert "linked-resource" in validator.validate(skill, tmp_path)["errors"]


def test_static_parser_never_echoes_unknown_arguments():
    result = subprocess.run([sys.executable, str(SCRIPT), "--secret=TEST_ONLY_PRIVATE_VALUE"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "TEST_ONLY_PRIVATE_VALUE" not in result.stdout + result.stderr


def test_static_parser_rejects_abbreviated_flags(tmp_path):
    skill = create_skill(tmp_path)
    result = subprocess.run([sys.executable, str(SCRIPT), "--sk", str(skill), "--repo-root", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "invalid-arguments" in result.stdout + result.stderr
