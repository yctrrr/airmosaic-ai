"""Synthetic-only checks for explicit record maintenance; no private inputs."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "skills/agent_operations/shared/autoskill/scripts/maintain.py"
spec = importlib.util.spec_from_file_location("autoskill_maintenance", SCRIPT)
maintenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(maintenance)


@pytest.fixture
def task(tmp_path):
    roots = {}
    for name in ("task", "assets", "config", "auth"):
        roots[name] = tmp_path / name
        roots[name].mkdir()
    args = SimpleNamespace(task_root=str(roots["task"]), assets_root=str(roots["assets"]),
                           config_root=str(roots["config"]), auth_root=str(roots["auth"]),
                           catalog="catalog.json", input=["records.json"], task_id="synthetic", proposal=None)
    (roots["task"] / "catalog.json").write_text(json.dumps({"skills": [
        {"name": "example-check", "description": "Validate synthetic metadata and references."},
        {"name": "example-format", "description": "Format reviewed public prose."}]}))
    write_records(roots["task"], [{"status": "observed", "outcome": "success", "skills": ["example-check"], "summary": "Synthetic check."}])
    return roots, args


def write_records(root, rows):
    (root / "records.json").write_text(json.dumps({"schema_version": 1, "records": rows}))


def receipt(roots):
    return next((roots["assets"] / "results/skill_maintenance").glob("*/review.json")).read_text(encoding="utf-8")


@pytest.mark.parametrize("names,outcome,expected", [(["example-check"], "success", "reuse"),
    (["example-check"], "failure", "revise"), (["example-check", "example-format"], "success", "compose"),
    ([], "unknown", "novel")])
def test_routes_have_explicit_evidence(task, names, outcome, expected):
    roots, args = task
    write_records(roots["task"], [{"status": "observed", "outcome": outcome, "summary": "Synthetic.", "skills": names}])
    assert maintenance.run(args)["route"] == expected
    report = json.loads(receipt(roots))
    assert report["routing"]["scientific_acceptance"] is False
    assert report["source_execution"] is False


def test_stale_and_lexical_mentions_do_not_establish_reuse(task):
    roots, args = task
    write_records(roots["task"], [{"status": "stale", "outcome": "success", "summary": "example-check references", "skills": ["example-check"]}])
    assert maintenance.run(args)["route"] == "novel"
    report = json.loads(receipt(roots))
    assert report["routing"]["unverified_claims"] == 1
    assert report["evidence"][0]["matches"][0]["description_terms"] == ["references"]


def test_private_content_and_ids_are_never_copied(task):
    roots, args = task
    private = "C:\\Users\\Synthetic\\private.csv https://private.invalid/?token=TEST_ONLY api_key=TEST_ONLY"
    write_records(roots["task"], [{"id": private, "status": "reported", "outcome": "unknown", "summary": private}])
    maintenance.run(args)
    result = receipt(roots)
    assert "TEST_ONLY" not in result and "private.csv" not in result and "private.invalid" not in result
    assert json.loads(result)["evidence"][0]["sensitive_content_omitted"]


def test_output_collision_preserves_existing_result(task):
    roots, args = task
    maintenance.run(args)
    before = receipt(roots)
    with pytest.raises(maintenance.Refusal, match="output-collision"):
        maintenance.run(args)
    assert receipt(roots) == before


@pytest.mark.parametrize("selected", ["../outside.json", "auth/records.json", "credentials.json", "config.json", "tokens.json", "harness/plan.md", ".env", "C:/private.json"])
def test_forbidden_paths_fail_before_read(task, selected):
    roots, args = task
    args.input = [selected]
    with pytest.raises(maintenance.Refusal, match="unsafe-input-path"):
        maintenance.run(args)
    assert not (roots["assets"] / "results").exists()


def test_rejects_links_nested_git_and_overlapping_roots(task):
    roots, args = task
    args.config_root = args.assets_root
    with pytest.raises(maintenance.Refusal, match="storage-roots-overlap"):
        maintenance.run(args)
    args.config_root = str(roots["config"])
    (roots["task"] / ".git").mkdir()
    with pytest.raises(maintenance.Refusal, match="git-root-refused"):
        maintenance.run(args)


def test_linked_input_rejected(task):
    roots, args = task
    link = roots["task"] / "linked.json"
    try:
        link.symlink_to(roots["task"] / "records.json")
    except OSError:
        pytest.skip("OS does not grant symlink creation")
    args.input = ["linked.json"]
    with pytest.raises(maintenance.Refusal, match="unsafe-input-file"):
        maintenance.run(args)


def test_task_root_cannot_be_authentication_directory(task):
    roots, args = task
    sensitive = roots["task"].parent / ".ssh"
    sensitive.mkdir()
    args.task_root = str(sensitive)
    with pytest.raises(maintenance.Refusal, match="sensitive-task-root"):
        maintenance.run(args)


def test_linked_output_parent_rejected(task):
    roots, args = task
    target = roots["assets"].parent / "elsewhere"
    target.mkdir()
    try:
        (roots["assets"] / "results").symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("OS does not grant symlink creation")
    with pytest.raises(maintenance.Refusal, match="unsafe-output-parent"):
        maintenance.run(args)
    assert not list(target.iterdir())


def test_nested_git_and_oversized_input_refused(task):
    roots, args = task
    nested = roots["task"] / "nested"
    nested.mkdir()
    (nested / ".git").write_text("gitdir: synthetic-only")
    (nested / "records.json").write_text("{}")
    args.input = ["nested/records.json"]
    with pytest.raises(maintenance.Refusal, match="nested-git-refused"):
        maintenance.run(args)
    args.input = ["records.json"]
    (roots["task"] / "records.json").write_text(" " * (maintenance.MAX_BYTES + 1))
    with pytest.raises(maintenance.Refusal, match="input-size-limit"):
        maintenance.run(args)


@pytest.mark.parametrize("value", ["https://synthetic.invalid/?token=TEST_ONLY", "C:\\Users\\Synthetic\\private.csv", "/synthetic-private.csv", "password=TEST_ONLY", "api_key=TEST_ONLY"])
def test_catalog_sensitive_strings_refused_without_echo(task, value):
    roots, args = task
    (roots["task"] / "catalog.json").write_text(json.dumps({"skills": [{"name": "example-check", "description": value}]}))
    with pytest.raises(maintenance.Refusal, match="sensitive-proposal-or-catalog") as error:
        maintenance.run(args)
    assert value not in str(error.value)
    assert not (roots["assets"] / "results").exists()


def test_plain_reviewed_text_does_not_execute_code(task):
    roots, args = task
    marker = roots["task"] / "executed.txt"
    (roots["task"] / "source.md").write_text("example-check\nimport os\nos.remove('never-run')")
    args.input = ["source.md"]
    assert maintenance.run(args)["route"] == "novel"
    assert not marker.exists()
    assert "import os" not in receipt(roots)


@pytest.mark.parametrize("content", ['{"schema_version": 1, "records": [', '{"schema_version": 1, "records": [], "records": []}', '{"schema_version": 1, "records": NaN}'])
def test_malformed_input_errors_are_fixed_codes(task, content):
    roots, args = task
    (roots["task"] / "records.json").write_text(content + "TEST_ONLY_PRIVATE_VALUE")
    command = [sys.executable, str(SCRIPT)]
    for key in ("task_root", "assets_root", "config_root", "auth_root", "catalog", "task_id"):
        command.extend(["--" + key.replace("_", "-"), getattr(args, key)])
    command.extend(["--input", "records.json"])
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 2 and "TEST_ONLY_PRIVATE_VALUE" not in result.stdout + result.stderr
    assert "Traceback" not in result.stdout + result.stderr


def test_parser_does_not_echo_unknown_secret_argument():
    result = subprocess.run([sys.executable, str(SCRIPT), "--secret=TEST_ONLY_PRIVATE_VALUE"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "TEST_ONLY_PRIVATE_VALUE" not in result.stdout + result.stderr


def test_explicit_sanitized_proposal_writes_draft_without_installing(task):
    roots, args = task
    draft = {"name": "example-review", "description": "Review synthetic authoring outputs.",
             "description_zh": "审查合成编写结果。", "version": "1.0.0", "compatibility": "Python 3.10+",
             "instructions": "Review selected synthetic outputs. Preserve uncertainty.",
             "instructions_zh": "审查选定的合成输出，保留不确定性。"}
    proposal = {"schema_version": 1, "sanitized": True, "authorship": "current-agent", "route": "revise",
                "skill_names": ["example-check"], "evidence_ids": ["input-1-record-1"], "draft": draft}
    (roots["task"] / "proposal.json").write_text(json.dumps(proposal))
    args.proposal = "proposal.json"
    assert maintenance.run(args)["draft_written"]
    output = next((roots["assets"] / "results/skill_maintenance").glob("*/draft/example-review/SKILL.md"))
    assert "Review selected synthetic outputs" in output.read_text(encoding="utf-8")
    assert not (roots["task"] / "draft").exists()


def test_sensitive_draft_refused_before_output(task):
    roots, args = task
    data = {"schema_version": 1, "sanitized": True, "authorship": "supplied-reviewed", "route": "novel", "skill_names": [],
            "evidence_ids": ["input-1-record-1"], "draft": {"name": "safe-name", "description": "api_key=TEST_ONLY",
            "description_zh": "合成", "version": "1.0.0", "compatibility": "Python", "instructions": "Review.", "instructions_zh": "审查。"}}
    (roots["task"] / "proposal.json").write_text(json.dumps(data))
    args.proposal = "proposal.json"
    with pytest.raises(maintenance.Refusal, match="sensitive-proposal-or-catalog"):
        maintenance.run(args)
    assert not (roots["assets"] / "results").exists()
