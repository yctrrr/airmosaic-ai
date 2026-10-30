"""Synthetic checks for shared data, project results and legacy compatibility."""

import json
from pathlib import Path

import pytest

from runtime.services import DataAccessService, ToolExecutionError, ToolRunnerService
from runtime.services.asset_layout import STAGES
from runtime.services.tool_execution_paths import ExecutionPaths
from runtime.services.mcp_gateway import MCPGateway


REPO = Path(__file__).absolute().parents[2]


@pytest.fixture
def roots(tmp_path, monkeypatch):
    result = {}
    for name, child in (("AIRMOSAIC_ASSETS_DIR", "assets"),
                        ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")):
        path = tmp_path / child
        path.mkdir()
        monkeypatch.setenv(name, str(path))
        result[name] = path
    return result


def test_assets_cli_process_routes_to_project_and_redacts_label(roots):
    result = ToolRunnerService().run("airmosaic_list_datasets", project_id="synthetic_private_project",
                                    stage=STAGES[0])
    assert result["status"] == "succeeded", result
    assert result["layout"] == "assets-v1"
    run = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_private_project" / result["run_id"]
    receipt = run / "records/airmosaic_list_datasets/record.json"
    assert receipt.is_file()
    assert (run / STAGES[0] / "airmosaic_list_datasets").is_dir()
    assert (run / "temp/airmosaic_list_datasets").is_dir()
    public = json.dumps(result) + receipt.read_text(encoding="utf-8")
    assert "synthetic_private_project" not in public
    assert str(roots["AIRMOSAIC_ASSETS_DIR"]) not in public
    assert "<project_id>" in result["locations"]["output"]


def test_assets_dry_run_does_not_create_directories(roots):
    result = ToolRunnerService().run("airmosaic_list_datasets", project_id="example_project",
                                    stage=STAGES[0], dry_run=True)
    assert result["can_execute"]
    assert list(roots["AIRMOSAIC_ASSETS_DIR"].iterdir()) == []


@pytest.mark.parametrize("project,stage,reason", [
    ("../escape", STAGES[0], "invalid_project_id"),
    ("project/child", STAGES[0], "invalid_project_id"),
    ("private label", STAGES[0], "invalid_project_id"),
    (None, STAGES[0], "project_id_required"),
    ("example_project", None, "invalid_research_stage"),
    ("example_project", "../other", "invalid_research_stage"),
    ("example_project", STAGES[1], "stage_is_methods_only"),
])
def test_invalid_context_is_private_and_read_only(roots, project, stage, reason):
    with pytest.raises(ToolExecutionError, match=reason):
        ToolRunnerService().run("airmosaic_list_datasets", project_id=project, stage=stage, dry_run=True)
    assert not list(roots["AIRMOSAIC_ASSETS_DIR"].iterdir())


def test_cross_stage_data_reference_and_output_write_boundary(roots):
    workspace = roots["AIRMOSAIC_ASSETS_DIR"]
    source = workspace / "data" / STAGES[0] / "ExampleDataset/v1/sample.csv"
    source.parent.mkdir(parents=True)
    source.write_text("value\n1\n", encoding="utf-8")
    paths = ExecutionPaths(REPO, "a" * 32, "example_tool", "example_project", STAGES[3])
    assert paths.parameter(str(source), "input_file") == source
    with pytest.raises(ToolExecutionError, match="output_outside_current_task"):
        paths.parameter(str(source), "output_file")
    assert paths.parameter(str(paths.output / "sample.csv"), "output_file").is_relative_to(paths.output)


@pytest.mark.parametrize("area", ["records", "temp"])
def test_records_and_temporary_files_are_not_dataset_inputs(roots, area):
    workspace = roots["AIRMOSAIC_ASSETS_DIR"]
    source = workspace / "results/other_project/previous_run" / area / "sample.csv"
    source.parent.mkdir(parents=True)
    source.write_text("value\n1\n", encoding="utf-8")
    paths = ExecutionPaths(REPO, "a" * 32, "example_tool", "example_project", STAGES[3])
    with pytest.raises(ToolExecutionError, match="input_outside_data_roots"):
        paths.parameter(str(source), "input_file")


def test_result_reference_across_projects_is_explicit_and_read_only(roots):
    source = roots["AIRMOSAIC_ASSETS_DIR"] / "results/other_project/previous_run" / STAGES[2] / "tool/output.csv"
    source.parent.mkdir(parents=True)
    source.write_text("value\n1\n", encoding="utf-8")
    paths = ExecutionPaths(REPO, "a" * 32, "example_tool", "example_project", STAGES[3])
    assert paths.parameter(str(source), "input_file") == source
    with pytest.raises(ToolExecutionError):
        paths.parameter(str(source), "output_file")


def test_run_identifier_cannot_reuse_another_stage(roots):
    paths = ExecutionPaths(REPO, "a" * 32, "tool_one", "example_project", STAGES[0])
    paths.create()
    with pytest.raises(ToolExecutionError, match="run_id_already_exists"):
        ExecutionPaths(REPO, "a" * 32, "tool_two", "example_project", STAGES[3])


def test_context_free_execution_is_rejected(roots):
    with pytest.raises(ToolExecutionError, match="project_id_required"):
        ExecutionPaths(REPO, "a" * 32, "example_tool")


def test_old_cache_is_not_automatically_read(roots):
    workspace = roots["AIRMOSAIC_ASSETS_DIR"]
    old = workspace / "data_cache/worldpop/old.csv"
    old.parent.mkdir(parents=True)
    old.write_text("value\n1\n", encoding="utf-8")
    access = DataAccessService(assets_dir=workspace)
    assert access.query_files("population", "*.csv") == []


def test_mcp_context_reaches_the_shared_runner(roots):
    gateway = MCPGateway()
    payload, error = gateway.call("worldpop_download", {
        "parameters": {"project": "wpgp"}, "project_id": "example_project",
        "stage": STAGES[0],
    })
    assert not error
    assert payload["mode"] == "preview"
    assert payload["result"]["layout"] == "assets-v1"
    assert "/results/<project_id>/" in payload["result"]["locations"]["output"]
    assert not list(roots["AIRMOSAIC_ASSETS_DIR"].iterdir())


def test_runner_availability_uses_only_shared_data(roots):
    workspace = roots["AIRMOSAIC_ASSETS_DIR"]
    folder = workspace / "data/01_socioeconomic_natural_change/WorldPop/v1"
    folder.mkdir(parents=True)
    (folder / "synthetic.csv").write_text("value\n1\n", encoding="utf-8")
    result = ToolRunnerService().run("airmosaic_check_availability", {
        "dataset_id": "population", "pattern": "v1/*.csv",
    }, project_id="example_project", stage=STAGES[0])
    assert result["status"] == "succeeded", result
    assert result["result_summary"]["matched_file_count"] == 1
