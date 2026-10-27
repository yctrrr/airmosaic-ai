"""MCP projection and privilege checks use only public metadata and fixtures."""

import json
from pathlib import Path
import threading

import pytest
from jsonschema import Draft202012Validator

from airmosaic.services.mcp_gateway import (
    MCPGateway, MCPGatewayError, MCPPolicy, METADATA_TOOLS,
)
from airmosaic.services.tool_registry import ToolRegistryService
from airmosaic.services import tool_process


@pytest.fixture
def local_roots(tmp_path, monkeypatch):
    roots = {}
    for name, child in (("AIRMOSAIC_ASSETS_DIR", "workspace"),
                        ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")):
        path = tmp_path / child
        path.mkdir()
        monkeypatch.setenv(name, str(path))
        roots[name] = path
    monkeypatch.delenv("GCAM_RELEASE_DIR", raising=False)
    monkeypatch.setenv("AIRMOSAIC_TEST_SECRET", "synthetic-secret-marker")
    return roots


def test_discovery_is_catalog_derived_and_does_not_execute(monkeypatch):
    monkeypatch.setattr(tool_process, "execute", lambda *a, **k: pytest.fail("discovery executed"))
    gateway = MCPGateway()
    expected = {n for n, t in gateway.registry._tools.items() if t["execution"]["enabled"]}
    assert {item["name"] for item in gateway.tools()} == expected
    assert len(expected) == 16
    assert len(gateway.skills) == 23
    assert all(item["name"] != "airmosaic_run_tool" for item in gateway.tools())
    for item in gateway.tools():
        Draft202012Validator.check_schema(item["input_schema"])
        Draft202012Validator.check_schema(item["output_schema"])


@pytest.mark.parametrize("name,args", [
    ("airmosaic_list_tools", {}),
    ("airmosaic_describe_tool", {"tool_id": "timexer_workflow_reference"}),
    ("airmosaic_check_tool", {"tool_id": "worldpop_download"}),
    ("airmosaic_list_datasets", {}),
    ("airmosaic_describe_dataset", {"dataset_id": "population"}),
    ("airmosaic_search_datasets", {"query": "population"}),
])
def test_metadata_queries_work_without_personal_roots(monkeypatch, name, args):
    for key in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
        monkeypatch.delenv(key, raising=False)
    gateway = MCPGateway()
    monkeypatch.setattr(gateway.runner, "run", lambda *a, **k: pytest.fail("metadata used runner"))
    result, error = gateway.call(name, args)
    assert not error and result["mode"] == "metadata"
    assert str(Path.cwd()) not in gateway.serialize(result)


def test_metadata_default_arguments_and_reference_visibility():
    gateway = MCPGateway()
    result, error = gateway.call("airmosaic_list_tools", None)
    assert not error and len(result["result"]) == 25
    assert any(not t["invocation"]["execution_supported"] for t in result["result"])


@pytest.mark.parametrize("name,args", [
    ("synthetic-secret-marker", {}),
    ("timexer_workflow_reference", {}),
    ("airmosaic_run_tool", {}),
    ("worldpop_download", {"parameters": {"project": "wpgp"}, "allow_network": True, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}),
    ("worldpop_download", {"parameters": {"project": "wpgp", "root": "synthetic-secret-marker"}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}),
    ("worldpop_download", {"parameters": {"project": "wpgp"}, "dry_run": "synthetic-secret-marker", "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}),
    ("worldpop_download", {"parameters": {"project": "wpgp"}, "timeout": 301, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}),
    ("worldpop_download", {"parameters": {"project": "wpgp"}, "params_file": "synthetic-secret-marker", "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}),
    ("airmosaic_describe_tool", {"tool_id": "synthetic-secret-marker"}),
    ("airmosaic_describe_dataset", {"dataset_id": "synthetic-secret-marker"}),
    ("airmosaic_list_tools", {"query": "synthetic-secret-marker\n"}),
])
def test_invalid_calls_never_echo_values_or_run(local_roots, monkeypatch, name, args):
    gateway = MCPGateway()
    monkeypatch.setattr(gateway.runner, "run", lambda *a, **k: pytest.fail("invalid request executed"))
    payload, error = gateway.call(name, args)
    assert error and "synthetic-secret-marker" not in gateway.serialize(payload)
    assert not list(local_roots["AIRMOSAIC_ASSETS_DIR"].iterdir())


def test_preview_has_no_writes_and_does_not_grant_network(local_roots, monkeypatch):
    gateway = MCPGateway()
    monkeypatch.setattr(tool_process, "execute", lambda *a, **k: pytest.fail("preview executed"))
    payload, error = gateway.call("worldpop_download", {"parameters": {"project": "wpgp"}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
    assert not error and payload["mode"] == "preview"
    assert "network_permission_required" in payload["result"]["blockers"]
    assert not list(local_roots["AIRMOSAIC_ASSETS_DIR"].iterdir())


def test_execution_requires_startup_grant_before_runner(local_roots, monkeypatch):
    gateway = MCPGateway()
    monkeypatch.setattr(gateway.runner, "run", lambda *a, **k: pytest.fail("unapproved execution"))
    payload, error = gateway.call("worldpop_download", {"parameters": {"project": "wpgp"}, "dry_run": False, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
    assert error and payload == {"error": "execution_not_authorized"}
    assert not list(local_roots["AIRMOSAIC_ASSETS_DIR"].iterdir())


@pytest.mark.parametrize("policy", [
    MCPPolicy(execution_tools=frozenset({"airmosaic_run_tool"})),
    MCPPolicy(execution_tools=frozenset({"airmosaic_list_tools"})),
    MCPPolicy(network_tools=frozenset({"worldpop_download"})),
    MCPPolicy(execution_tools=frozenset({"gcam_aggregate_provinces"}),
              network_tools=frozenset({"gcam_aggregate_provinces"})),
    MCPPolicy(max_timeout=True),
    MCPPolicy(max_timeout=3601),
    MCPPolicy(browser_port=9222),
    MCPPolicy(execution_tools=frozenset({"ihme_gbd_fetch_results"}),
              network_tools=frozenset({"ihme_gbd_fetch_results"}),
              browser_tools=frozenset({"ihme_gbd_fetch_results"})),
])
def test_invalid_startup_policy_is_rejected(policy):
    with pytest.raises(MCPGatewayError, match="invalid_server_policy"):
        MCPGateway(policy=policy)


def test_browser_port_is_operator_bound(local_roots, monkeypatch):
    tool = "ihme_gbd_fetch_results"
    gateway = MCPGateway(policy=MCPPolicy(frozenset({tool}), frozenset({tool}),
                                        frozenset({tool}), browser_port=9222))
    seen = []
    def run(name, parameters, **options):
        seen.append((parameters, options))
        return {"status": "succeeded", "authentication": "unverified"}
    monkeypatch.setattr(gateway.runner, "run", run)
    parameters = {key: "1" for key in ("years", "locations", "causes", "ages", "sexes", "measures", "metrics")}
    result, error = gateway.call(tool, {"parameters": parameters, "dry_run": False, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
    assert not error and result["result"]["authentication"] == "unverified"
    assert seen[0][0]["port"] == 9222
    assert seen[0][1]["allow_network"] and seen[0][1]["confirm_browser_session"]
    result, error = gateway.call(tool, {"parameters": {**parameters, "port": 9333}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
    assert error and len(seen) == 1


def test_input_path_boundaries_apply_through_gateway(local_roots):
    gateway = MCPGateway()
    private_file = local_roots["AIRMOSAIC_AUTH_DIR"] / "synthetic-secret-marker.csv"
    private_file.write_text("must not be read", encoding="utf-8")
    payload, error = gateway.call("gcam_aggregate_provinces", {"parameters": {"input_csv": str(private_file)}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
    assert error and payload == {"error": "input_outside_data_roots"}
    assert str(private_file) not in gateway.serialize(payload)


def test_resources_expose_only_indexed_public_documents(local_roots):
    gateway = MCPGateway()
    uris = {resource["uri"] for resource in gateway.resources()}
    assert len(uris) == 49
    for resource in gateway.resources():
        body, mime = gateway.read_resource(resource["uri"])
        assert body and mime in {"application/json", "text/markdown"}
        assert "synthetic-secret-marker" not in body
    with pytest.raises(MCPGatewayError, match="resource_not_exposed"):
        gateway.read_resource((local_roots["AIRMOSAIC_AUTH_DIR"] / "session.json").as_uri())
    with pytest.raises(MCPGatewayError):
        gateway.read_resource("airmosaic://skills/../../credentials/en")


def test_nonfinite_and_oversized_inputs_are_fixed_errors():
    gateway = MCPGateway()
    for value in (float('nan'), 'x' * (1024 * 1024 + 1)):
        payload, error = gateway.call("worldpop_download", {"parameters": {"project": value}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
        assert error and set(payload) == {"error"}


def test_unexpected_failure_does_not_echo_exception(monkeypatch):
    gateway = MCPGateway()
    monkeypatch.setattr(gateway.registry, "list_tools", lambda **k: (_ for _ in ()).throw(RuntimeError("synthetic-secret-marker")))
    payload, error = gateway.call("airmosaic_list_tools", {})
    assert error and payload == {"error": "mcp_call_failed"}


def test_pre_cancelled_call_cannot_execute(monkeypatch):
    gateway = MCPGateway()
    event = threading.Event()
    event.set()
    monkeypatch.setattr(gateway.runner, "run", lambda *a, **k: pytest.fail("cancelled call ran"))
    assert gateway.call("worldpop_download", {"parameters": {"project": "wpgp"}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}, event) == ({"error": "cancelled"}, True)
