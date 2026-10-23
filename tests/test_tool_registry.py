from importlib import metadata
import ast
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys

import pytest
import yaml

from airmosaic_core.services import ToolRegistryError, ToolRegistryService
from airmosaic_core.services import tool_readiness
from airmosaic_core.services import tool_paths
from airmosaic_core.services.tool_registry import format_tool_table


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def separate_roots(tmp_path, monkeypatch):
    roots = {}
    for name, child in [("AIRMOSAIC_LOCAL_WORKSPACE", "workspace"),
                        ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")]:
        roots[name] = tmp_path / child
        roots[name].mkdir()
        monkeypatch.setenv(name, str(roots[name]))
    for name in ("GCAM_RELEASE_DIR", "UNIT_PRICE_OUT_DIR", "PM25_HIA_OUTPUT_DIR",
                 "PM25_HIA_CONC_DIR", "PM25_HIA_POP_DIR", "PM25_HIA_MORT_FILE",
                 "PM25_HIA_RR_FILE", "PM25_HIA_POP_FILE", "PM25_HIA_SHP_DIR"):
        monkeypatch.delenv(name, raising=False)
    return roots


@pytest.fixture
def installed_dependencies(monkeypatch):
    monkeypatch.setattr(tool_readiness.metadata, "version", lambda name: "1.0")
    monkeypatch.setattr(tool_readiness, "executable_available", lambda name: True)


def synthetic_registry(tmp_path):
    repo = tmp_path / "synthetic-repo"
    (repo / "catalog/tools").mkdir(parents=True)
    (repo / "catalog/schemas").mkdir()
    shutil.copyfile(ROOT / "catalog/schemas/tool.schema.json", repo / "catalog/schemas/tool.schema.json")
    (repo / "harness/usage").mkdir(parents=True)
    (repo / "harness/usage/core.md").write_text("Public guide", encoding="utf-8")
    data = yaml.safe_load((ROOT / "catalog/tools/airmosaic_list_datasets.yaml").read_text(encoding="utf-8"))
    entry = repo / data["entrypoint"]["path"]
    entry.parent.mkdir(parents=True)
    entry.write_text("raise AssertionError('Never execute during discovery')", encoding="utf-8")
    return repo, data


def write_manifest(repo, data, name="sample"):
    path = repo / "catalog/tools" / (name + ".yaml")
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_real_registry_covers_existing_entries_and_filters(separate_roots):
    registry = ToolRegistryService()
    tools = registry.list_tools()
    assert {tool["category"] for tool in tools} == {"core", "data_acquisition", "model"}
    entries = {tool["entrypoint"]["path"] for tool in tools}
    assert {path.relative_to(ROOT).as_posix() for path in (ROOT / "skills").rglob("*.py")} <= entries
    for category in ("core", "data_acquisition", "model"):
        selected = registry.list_tools(category=category)
        assert selected and all(item["category"] == category for item in selected)
    assert {item["skill_id"] for item in registry.list_tools(skill="worldpop")} == {"worldpop"}
    assert registry.list_tools(skill="does-not-exist") == []
    assert {tool["tool_id"] for tool in registry.list_tools(query="WorldPop")} == {"worldpop_download"}
    assert all(item["availability"]["status"] == "ready" for item in registry.list_tools(status="ready"))
    detail = registry.describe_tool("worldpop_download")
    assert detail["entrypoint"]["argument_bindings"]["root"] == "--root"
    assert detail["effects"]["network"] is True
    assert detail["invocation"]["execution_supported"] is True
    detail["title"] = "mutated"
    assert registry.describe_tool("worldpop_download")["title"] != "mutated"


@pytest.mark.parametrize("change", [
    lambda data: data.update(schema_version=2),
    lambda data: data.update(private_field="synthetic-private-value"),
    lambda data: data["requirements"].update(extra="synthetic-private-value"),
    lambda data: data["entrypoint"].update(path="../outside.py"),
    lambda data: data["entrypoint"].update(path="/absolute/outside.py"),
    lambda data: data["entrypoint"]["argument_bindings"].update(extra="--extra"),
    lambda data: data["input_schema"].update(required=["undeclared"]),
    lambda data: data["input_schema"]["properties"].update(layer={"$ref": "https://example.invalid/schema"}),
    lambda data: data["authentication"].update(token="synthetic-private-value"),
])
def test_invalid_manifests_reject_without_echoing_values(tmp_path, change):
    repo, data = synthetic_registry(tmp_path)
    change(data)
    write_manifest(repo, data)
    with pytest.raises(ToolRegistryError) as error:
        ToolRegistryService(repo)
    assert "synthetic-private-value" not in str(error.value)
    assert str(tmp_path) not in str(error.value)


@pytest.mark.parametrize("content", ["title: first\ntitle: second\n", "title: [synthetic-private-value"])
def test_bad_yaml_does_not_expose_excerpts(tmp_path, content):
    repo, _ = synthetic_registry(tmp_path)
    (repo / "catalog/tools/sample.yaml").write_text(content, encoding="utf-8")
    with pytest.raises(ToolRegistryError) as error:
        ToolRegistryService(repo)
    assert "synthetic-private-value" not in str(error.value)


def test_duplicate_ids_fail_instead_of_silently_overwriting(tmp_path):
    repo, data = synthetic_registry(tmp_path)
    write_manifest(repo, data, "first")
    write_manifest(repo, data, "second")
    with pytest.raises(ToolRegistryError, match="duplicate tool IDs"):
        ToolRegistryService(repo)


def test_empty_registry_fails(tmp_path):
    repo, _ = synthetic_registry(tmp_path)
    with pytest.raises(ToolRegistryError, match="no manifests"):
        ToolRegistryService(repo)


def test_entrypoint_link_cannot_escape_repository(tmp_path):
    repo, data = synthetic_registry(tmp_path)
    target = tmp_path / "external.py"
    target.write_text("raise AssertionError('Never run')", encoding="utf-8")
    entry = repo / data["entrypoint"]["path"]
    entry.unlink()
    try:
        entry.symlink_to(target)
    except OSError:
        pytest.skip("Symbolic links unavailable")
    write_manifest(repo, data)
    with pytest.raises(ToolRegistryError, match="leaves the repository"):
        ToolRegistryService(repo)


def test_missing_entrypoint_is_diagnostic_not_ready(tmp_path):
    repo, data = synthetic_registry(tmp_path)
    (repo / data["entrypoint"]["path"]).unlink()
    write_manifest(repo, data)
    assert ToolRegistryService(repo).check_tool(data["tool_id"])["status"] == "missing_entrypoint"


def test_dependency_checks_use_metadata_not_imports(separate_roots, monkeypatch):
    def version(name):
        if name == "requests":
            raise metadata.PackageNotFoundError(name)
        return "1.0"
    monkeypatch.setattr(tool_readiness.metadata, "version", version)
    result = ToolRegistryService().check_tool("worldpop_download")
    assert result["status"] == "missing_dependency"
    assert {check["name"] for check in result["checks"] if check["status"] == "missing_dependency"} == {"requests"}


def test_no_credentials_or_config_contents_are_read(separate_roots, installed_dependencies, monkeypatch):
    marker = "synthetic-private-marker"
    for name in ("AIRMOSAIC_AUTH_DIR", "AIRMOSAIC_CONFIG_DIR"):
        (separate_roots[name] / "private.txt").write_text(marker, encoding="utf-8")
    original = Path.read_text

    def guarded_read(path, *args, **kwargs):
        if any(path.is_relative_to(separate_roots[name]) for name in ("AIRMOSAIC_AUTH_DIR", "AIRMOSAIC_CONFIG_DIR")):
            raise AssertionError("Configuration/authentication contents must not be read")
        return original(path, *args, **kwargs)

    def no_execution(*args, **kwargs):
        raise AssertionError("Discovery must not execute tools or connect to networks")

    monkeypatch.setattr(Path, "read_text", guarded_read)
    monkeypatch.setattr(subprocess, "run", no_execution)
    monkeypatch.setattr(socket, "create_connection", no_execution)
    tools = ToolRegistryService().list_tools()
    public = json.dumps(tools)
    assert marker not in public
    for path in separate_roots.values():
        assert str(path) not in public
    gbd = next(tool for tool in tools if tool["tool_id"] == "ihme_gbd_fetch_results")
    assert gbd["availability"]["status"] == "needs_auth"
    assert gbd["availability"]["authentication"]["status"] == "unverified"


@pytest.mark.parametrize("value", ["relative/location", str(ROOT)])
def test_invalid_workspace_paths_are_not_printed(separate_roots, installed_dependencies, monkeypatch, value):
    monkeypatch.setenv("AIRMOSAIC_LOCAL_WORKSPACE", value)
    result = ToolRegistryService().check_tool("worldpop_download")
    assert result["status"] == "invalid_configuration"
    assert value not in json.dumps(result)


def test_nested_roots_are_rejected(separate_roots, installed_dependencies, monkeypatch):
    monkeypatch.setenv("AIRMOSAIC_AUTH_DIR", str(separate_roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "auth"))
    assert ToolRegistryService().check_tool("worldpop_download")["status"] == "invalid_configuration"


def test_output_cannot_target_data_cache(separate_roots, installed_dependencies, monkeypatch):
    monkeypatch.setenv("PM25_HIA_OUTPUT_DIR", str(separate_roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "data_cache"))
    from airmosaic_core.services.tool_readiness import _configuration
    result = _configuration({"name": "PM25_HIA_OUTPUT_DIR", "role": "output", "kind": "directory"}, ROOT)
    assert result["status"] == "invalid_configuration"
    assert result["reason"] == "output_outside_task_root"


def test_output_ancestor_must_be_directory(separate_roots, installed_dependencies, monkeypatch):
    output = separate_roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "output"
    output.mkdir()
    marker = output / "file"
    marker.write_text("synthetic", encoding="utf-8")
    monkeypatch.setenv("PM25_HIA_OUTPUT_DIR", str(marker / "nested"))
    from airmosaic_core.services.tool_readiness import _configuration
    result = _configuration({"name": "PM25_HIA_OUTPUT_DIR", "role": "output", "kind": "directory"}, ROOT)
    assert result["status"] == "invalid_configuration"


def test_executable_search_skips_unc_and_remote_drives(tmp_path, monkeypatch):
    local_bin = tmp_path / "bin"
    local_bin.mkdir()
    filename = "java.exe" if os.name == "nt" else "java"
    executable = local_bin / filename
    executable.write_text("synthetic executable marker", encoding="utf-8")
    executable.chmod(0o755)
    remote_drive = tmp_path / "remote_drive"
    monkeypatch.setenv("PATH", os.pathsep.join([r"\\example.invalid\share", str(remote_drive), str(local_bin)]))
    monkeypatch.setattr(tool_paths, "_network_drive", lambda path: "remote_drive" in path.parts)
    original = Path.lstat

    def guarded_stat(path, *args, **kwargs):
        assert not str(path).startswith("\\\\")
        assert not path.is_relative_to(remote_drive)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", guarded_stat)
    assert tool_paths.executable_available("java")


def test_junction_is_rejected_before_target_resolution(tmp_path, monkeypatch):
    from types import SimpleNamespace

    original = Path.lstat
    def fake_stat(path, *args, **kwargs):
        if path.name == "redirect":
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "lstat", fake_stat)
    monkeypatch.setattr(tool_paths, "_network_drive", lambda path: False)
    with pytest.raises(ValueError, match="reparse"):
        tool_paths.local_path(str(tmp_path / "redirect" / "network-target"))


def test_parent_component_is_rejected_before_any_filesystem_probe(tmp_path, monkeypatch):
    def no_probe(*args, **kwargs):
        raise AssertionError("Parent traversal must be rejected before filesystem probes")
    monkeypatch.setattr(tool_paths, "_network_drive", no_probe)
    with pytest.raises(ValueError):
        tool_paths.local_path(str(tmp_path / "redirect" / ".." / "data"))


def test_registered_cli_arguments_match_actual_parser():
    from airmosaic_core.cli import build_parser
    parser = build_parser()
    commands = next(action for action in parser._actions if hasattr(action, "choices") and isinstance(action.choices, dict)).choices
    registry = ToolRegistryService()
    for record in registry._tools.values():
        entry = record["entrypoint"]
        if entry["kind"] != "cli":
            continue
        subparser = commands[entry["subcommand"]]
        actions = {option: action for action in subparser._actions for option in action.option_strings}
        for name, binding in entry["argument_bindings"].items():
            if binding.startswith("positional:"):
                assert any(action.dest == name and not action.option_strings for action in subparser._actions)
                continue
            assert binding in actions
            if actions[binding].choices:
                assert set(record["input_schema"]["properties"][name]["enum"]) <= set(actions[binding].choices)


def test_python_script_bindings_match_source_parsers():
    registry = ToolRegistryService()
    for record in registry._tools.values():
        entry = record["entrypoint"]
        if entry["kind"] != "python_script":
            continue
        module = ast.parse((ROOT / entry["path"]).read_text(encoding="utf-8-sig"))
        arguments = {}
        for node in ast.walk(module):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
                options = {keyword.arg: keyword.value for keyword in node.keywords}
                for value in node.args:
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        arguments[value.value] = options
        for name, binding in entry["argument_bindings"].items():
            assert binding in arguments
            keywords = arguments[binding]
            if isinstance(keywords.get("required"), ast.Constant) and keywords["required"].value:
                assert name in record["input_schema"]["required"]
            if isinstance(keywords.get("type"), ast.Name) and keywords["type"].id == "int":
                assert record["input_schema"]["properties"][name]["type"] == "integer"


def test_registered_machine_output_matches_actual_cli(separate_roots):
    from jsonschema import Draft202012Validator
    registry = ToolRegistryService()
    tool = registry.describe_tool("airmosaic_list_tools")
    assert tool["invocation"]["tokens"][-2:] == ["--format", "json"]
    parameters = {"format": "json", "category": "core"}
    Draft202012Validator(tool["input_schema"]).validate(parameters)
    env = {**os.environ, "PYTHONUTF8": "1"}
    command = [sys.executable, "-B", *tool["invocation"]["tokens"][1:], "--category", "core"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=env, timeout=30)
    assert result.returncode == 0
    Draft202012Validator(tool["output_schema"]).validate(json.loads(result.stdout))
    assert not Draft202012Validator(tool["input_schema"]).is_valid({"format": "table"})


def test_r_libraries_remain_unverified(separate_roots, installed_dependencies, monkeypatch):
    monkeypatch.setenv("UNIT_PRICE_OUT_DIR", str(separate_roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "output/run/plot"))
    result = ToolRegistryService().check_tool("gcam_plot_sector_change")
    assert result["status"] == "unknown"
    assert {check["status"] for check in result["checks"] if check["kind"] == "r_package"} == {"unverified"}


def test_templates_never_appear_callable(separate_roots, installed_dependencies):
    detail = ToolRegistryService().describe_tool("pm25_hia_calculate_template")
    assert detail["availability"]["status"] == "not_executable"
    assert detail["registration_status"] == "catalogued"
    assert detail["invocation"]["tokens"] == []


def test_table_includes_categories_entrypoints_dependencies_and_login(separate_roots):
    text = format_tool_table(ToolRegistryService().list_tools())
    assert "data_acquisition" in text and "model" in text and "core" in text
    assert "python -m airmosaic_core.cli" in text
    assert "dependencies:" in text and "login: browser_session (unverified)" in text
    assert format_tool_table([]) == "No matching tools."


@pytest.mark.parametrize("arguments", [
    ["list-tools", "--format", "json", "--category", "core"],
    ["describe-tool", "worldpop_download"],
    ["check-tool", "ihme_gbd_fetch_results"],
    ["list-datasets"],
])
def test_cli_json_interfaces_and_old_catalog_compatibility(arguments, separate_roots):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    result = subprocess.run([sys.executable, "-B", "-m", "airmosaic_core.cli", *arguments],
                            capture_output=True, text=True, encoding="utf-8", env=env, timeout=30)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data
    assert str(separate_roots["AIRMOSAIC_AUTH_DIR"]) not in result.stdout


def test_cli_error_does_not_echo_unknown_identifier():
    result = subprocess.run([sys.executable, "-B", "-m", "airmosaic_core.cli", "describe-tool", "synthetic-private-value"],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    assert result.stdout == ""
    assert json.loads(result.stderr)["error"] == "tool_registry_error"
    assert "synthetic-private-value" not in result.stderr
