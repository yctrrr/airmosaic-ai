"""Public/private separation using synthetic local packages only."""

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from runtime.services.tool_registry import ToolRegistryService, ToolRegistryError
from runtime.services.tool_runner import ToolRunnerService
from runtime.services.tool_execution_paths import ToolExecutionError
from runtime.services.capability_catalog import CapabilityCatalogService
from runtime.services.mcp_gateway import MCPGateway
from runtime.services.data_catalog import DataCatalogService


ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "SYNTHETIC_LOCAL_ONLY_DOCUMENT"


@pytest.fixture
def local_package(tmp_path, monkeypatch):
    for name in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
        monkeypatch.delenv(name, raising=False)
    private = tmp_path / "local source"
    private.mkdir()
    declaration = json.loads((ROOT / "catalog/local-capabilities.json").read_text())
    for relative in declaration["files"]:
        dest = private / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        public = ROOT / relative
        if relative.startswith("catalog/tools/"):
            body = public.read_text(encoding="utf-8")
        elif dest.name in {"SKILL.md", "SKILL_ZH.md", "datasets.yaml"}:
            body = public.read_text(encoding="utf-8") + "\n# " + SENTINEL + "\n"
        elif dest.suffix in {".md", ".py", ".R"}:
            body = "# " + SENTINEL + "\n"
        else:
            body = "{}"
        dest.write_text(body, encoding="utf-8")
    manifest = private / "capabilities.json"
    manifest.write_text(json.dumps({key: declaration[key]
                                   for key in ("schema_version", "extension_id", "files")}))
    tool = private / "catalog/tools/csmar_process_company_info.yaml"
    data = yaml.safe_load(tool.read_text(encoding="utf-8"))
    data.update(implementation_status="implemented", registration_status="registered")
    data["entrypoint"] = {"kind": "python_script", "path":
        "skills/data_acquisition/01_socioeconomic_natural_change/csmar/scripts/process_listed_company_basic_info.py",
        "argument_bindings": {"zip": "--zip", "out_dir": "--out-dir"}}
    data["input_schema"] = {"type": "object", "properties": {
        "zip": {"type": "string"}, "out_dir": {"type": "string"}},
        "required": ["zip", "out_dir"], "additionalProperties": False}
    data["execution"] = {"enabled": True, "adapter": "csmar",
                         "path_parameters": {"zip": "input_file", "out_dir": "output_directory"}}
    tool.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    config = tmp_path / "mapping.json"
    config.write_text(json.dumps({"schema_version": 1, "root": str(private)}))
    return private, config


def test_default_has_no_private_documents_or_execution(local_package):
    registry = ToolRegistryService()
    assert registry.check_tool("csmar_process_company_info")["status"] == "private_extension_required"
    with pytest.raises(ToolExecutionError, match="^private_extension_required$"):
        ToolRunnerService(registry).run("csmar_process_company_info", dry_run=True)
    gateway = MCPGateway(registry)
    assert "csmar_process_company_info" not in {tool["name"] for tool in gateway.tools()}
    assert SENTINEL not in json.dumps(gateway.capabilities.snapshot())
    assert not (ROOT / registry._tools["csmar_process_company_info"]["entrypoint"]["path"]).suffix == ".py"


def test_explicit_selection_reuses_ids_and_serves_only_declared_documents(local_package):
    private, config = local_package
    registry = ToolRegistryService(local_config=config)
    detail = registry.describe_tool("csmar_process_company_info")
    assert detail["source_scope"] == "local_private" and detail["invocation"]["execution_supported"]
    catalog = CapabilityCatalogService(registry)
    skill = catalog.describe("skill", "csmar-downloader")
    assert skill["source_scope"] == "local_private"
    gateway = MCPGateway(registry)
    body, _ = gateway.read_resource(skill["resources"]["en"])
    assert SENTINEL in body
    assert str(private) not in json.dumps(detail) + json.dumps(catalog.snapshot())
    assert "csmar_process_company_info" in {tool["name"] for tool in gateway.tools()}
    assert registry.describe_tool("worldpop_download")["source_scope"] == "public"
    assert DataCatalogService(registry=registry).describe_dataset("gdp")["dataset_id"] == "industrial_yearbook_regional_sector"


@pytest.mark.parametrize("corruption", ["extra", "missing", "duplicate", "traversal", "id", "root"])
def test_invalid_local_package_fails_with_fixed_errors(local_package, corruption):
    private, config = local_package
    manifest = private / "capabilities.json"
    value = json.loads(manifest.read_text())
    if corruption == "extra":
        value["files"].append("secrets/SYNTHETIC_PRIVATE_PATH.json")
    elif corruption == "missing":
        (private / value["files"][0]).unlink()
    elif corruption == "duplicate":
        value["files"].append(value["files"][0])
    elif corruption == "traversal":
        value["files"][0] = "../SYNTHETIC_PRIVATE_PATH"
    elif corruption == "id":
        f = private / "catalog/tools/csmar_process_company_info.yaml"
        t = yaml.safe_load(f.read_text(encoding="utf-8")); t["tool_id"] = "worldpop_download"
        f.write_text(yaml.safe_dump(t), encoding="utf-8")
    else:
        config.write_text(json.dumps({"schema_version": 1, "root": str(ROOT)}))
    manifest.write_text(json.dumps(value))
    with pytest.raises(ToolRegistryError) as error:
        ToolRegistryService(local_config=config)
    assert "SYNTHETIC_PRIVATE_PATH" not in str(error.value) and str(private) not in str(error.value)


def test_private_script_runs_with_existing_path_and_environment_contract(local_package, tmp_path, monkeypatch):
    private, config = local_package
    for name in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
        root = tmp_path / name
        root.mkdir()
        monkeypatch.setenv(name, str(root))
    assets = Path(__import__("os").environ["AIRMOSAIC_ASSETS_DIR"])
    source = assets / "data/synthetic.zip"
    source.parent.mkdir()
    source.write_bytes(b"synthetic")
    registry = ToolRegistryService(local_config=config)
    script = registry.path(registry._tools["csmar_process_company_info"]["entrypoint"]["path"])
    script.write_text("import argparse, os\nfrom pathlib import Path\np=argparse.ArgumentParser()\n"
                      "p.add_argument('--zip');p.add_argument('--out-dir');a=p.parse_args()\n"
                      "assert 'AIRMOSAIC_AUTH_DIR' not in os.environ\n"
                      "Path(a.out_dir).joinpath('synthetic.txt').write_text('ok')\n")
    runner = ToolRunnerService(registry)
    params = {"zip": str(source)}
    preview = runner.run("csmar_process_company_info", params, dry_run=True,
                         project_id="local_test", stage="01_socioeconomic_natural_change")
    assert preview["can_execute"]
    assert not (assets / "results").exists()
    result = runner.run("csmar_process_company_info", params,
                        project_id="local_test", stage="01_socioeconomic_natural_change")
    assert result["status"] == "succeeded"
    assert str(private) not in json.dumps(result)
    with pytest.raises(ToolExecutionError):
        runner.run("csmar_process_company_info", {"zip": str(config)}, dry_run=True,
                   project_id="local_test", stage="01_socioeconomic_natural_change")


def test_cli_selected_mapping_and_invalid_mapping_are_private(local_package):
    private, config = local_package
    result = subprocess.run([sys.executable, "-X", "utf8", "-m", "runtime.cli", "--local-capabilities-config", str(config),
                             "describe-tool", "csmar_process_company_info"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0 and json.loads(result.stdout)["source_scope"] == "local_private"
    assert str(private) not in result.stdout + result.stderr
    result = subprocess.run([sys.executable, "-X", "utf8", "-m", "runtime.cli", "--local-capabilities-config",
                             str(config.parent / "SYNTHETIC_PRIVATE_PATH.json"), "list-tools"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 2 and "SYNTHETIC_PRIVATE_PATH" not in result.stdout + result.stderr


@pytest.mark.parametrize("payload", [
    b"skill_id: [SYNTHETIC_PRIVATE_VALUE\n", b"\xff", b"- SYNTHETIC_PRIVATE_VALUE\n",
])
def test_invalid_selected_dataset_errors_hide_private_paths_and_content(local_package, payload):
    private, config = local_package
    declaration = private / "skills/data_acquisition/01_socioeconomic_natural_change/csmar/datasets.yaml"
    declaration.write_bytes(payload)
    registry = ToolRegistryService(local_config=config)
    with pytest.raises(ValueError, match="^invalid_dataset_metadata$"):
        DataCatalogService(registry=registry).list_datasets()
    gateway = MCPGateway(registry)
    response, failed = gateway.call("airmosaic_list_datasets", {})
    assert failed and response == {"error": "mcp_call_failed"}
    with pytest.raises(ValueError, match="^invalid_dataset_metadata$"):
        gateway.read_resource("airmosaic://catalog/datasets")
    for command in (["list-datasets"], ["describe-dataset", "gdp"], ["search-datasets", "company"]):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "runtime.cli", "--local-capabilities-config", str(config), *command],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        assert result.returncode == 2
        assert json.loads(result.stderr) == {"error": "catalog_query_failed"}
        for secret in (str(private), str(config), "SYNTHETIC_PRIVATE_VALUE", "Traceback"):
            assert secret not in result.stdout + result.stderr


def test_core_cli_child_preserves_explicit_selection_without_disclosing_paths(local_package, tmp_path, monkeypatch):
    private, config = local_package
    for name in ("AIRMOSAIC_ASSETS_DIR", "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_AUTH_DIR"):
        root = tmp_path / name
        root.mkdir()
        monkeypatch.setenv(name, str(root))
    selected = ToolRegistryService(local_config=config)
    invocation = selected.describe_tool("csmar_process_company_info")["invocation"]
    assert invocation["working_directory"] == "selected_local_capability_root"
    assert invocation["runner_tokens"][3:5] == [
        "--local-capabilities-config", "<local-capabilities-config.json>"]
    expected = selected.check_tool("csmar_process_company_info")["status"]
    assert expected != "private_extension_required"
    for registry, expected_status in ((selected, expected), (ToolRegistryService(), "private_extension_required")):
        result = ToolRunnerService(registry).run(
            "airmosaic_check_tool", {"tool_id": "csmar_process_company_info"},
            project_id="local_test", stage="01_socioeconomic_natural_change")
        assert result["status"] == "succeeded"
        assert result["result_summary"] == {"status": expected_status}
        encoded = json.dumps(result) + json.dumps(invocation)
        assert str(private) not in encoded and str(config) not in encoded
