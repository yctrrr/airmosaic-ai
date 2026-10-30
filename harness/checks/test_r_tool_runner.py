"""R adapter contracts and isolated synthetic integration; no model simulations."""

import csv
import json
import os
from pathlib import Path
import shutil

import pytest

from runtime.services import ToolRunnerService, ToolExecutionError, ToolRegistryService
from runtime.services import tool_r, tool_runner
from runtime.services.tool_execution_paths import ExecutionPaths
from runtime.services.tool_process import child_environment, execute
from test_tool_runner import synthetic_runner


PLOT = "gcam_plot_sector_change"
INSPECT = "gcam_inspect_output_structure"


@pytest.fixture
def roots(tmp_path_factory, monkeypatch):
    # A short synthetic root leaves room for R's native output filenames on Windows.
    base = tmp_path_factory.mktemp("r")
    result = {}
    for name, child in (("AIRMOSAIC_ASSETS_DIR", "assets with spaces"),
                        ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")):
        path = base / child
        path.mkdir()
        monkeypatch.setenv(name, str(path))
        result[name] = path
    monkeypatch.delenv("GCAM_RELEASE_DIR", raising=False)
    return result


@pytest.fixture
def market(roots):
    path = roots["AIRMOSAIC_ASSETS_DIR"] / "data/market rows.csv"
    path.parent.mkdir()
    rows = ["scenario,source,sector,region,year,price,quantity"]
    for year in (2021, 2035):
        rows += [f"example_scenario,sector_cost,cement,AH,{year},10,1",
                 f"example_scenario,sector_cost,cement,BJ,{year},20,3",
                 f"example_scenario,sector_cost,cement,China,{year},999,999",
                 f"example_scenario,market,cement,AH,{year},999,999",
                 f"example_scenario,sector_cost,coke,AH,{year},2,-2",
                 f"example_scenario,sector_cost,coke,BJ,{year},4,0"]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def model(tmp_path, monkeypatch):
    path = tmp_path / "model release with spaces"
    (path / "output/database_basexdb").mkdir(parents=True)
    (path / "database_R").mkdir()
    (path / "database_R/Prov_code_china.csv").write_text("GCAM_name\nAH\nBJ\n", encoding="utf-8")
    monkeypatch.setenv("GCAM_RELEASE_DIR", str(path))
    return path


@pytest.mark.parametrize("tool_id", [INSPECT, PLOT])
def test_r_dry_run_does_not_load_r_or_create_files(roots, market, model, monkeypatch, tool_id):
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("dry-run spawned R"))
    workspace = roots["AIRMOSAIC_ASSETS_DIR"]
    before = set(workspace.rglob("*"))
    params = {"input_csv": str(market)} if tool_id == PLOT else {"max_memory": "512m"}
    result = ToolRunnerService().run(tool_id, params, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")
    assert result["status"] == "dry_run"
    assert result["r_dependencies"]["status"] == "unverified"
    assert before == set(workspace.rglob("*"))
    assert str(model) not in json.dumps(result) and str(market) not in json.dumps(result)


@pytest.mark.parametrize("params", [{"max_memory": "1g;echo synthetic"}, {"max_memory": "0g"},
                                    {"max_memory": 1}, {"release_dir": "synthetic"}, {"scenario": "x"}])
def test_structure_rejects_unknown_or_injected_arguments(roots, params):
    with pytest.raises(ToolExecutionError, match="invalid_tool_parameters"):
        ToolRunnerService().run(INSPECT, params, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")


@pytest.mark.parametrize("params", [{}, {"sectors": ["cement"]}, {"scenarios": "--input-csv"},
                                    {"sectors": "cement,,coke"}, {"years": "2020,2030"}])
def test_plot_requires_input_and_valid_filters(roots, market, params):
    supplied = {} if not params else {"input_csv": str(market), **params}
    with pytest.raises(ToolExecutionError, match="invalid_tool_parameters"):
        ToolRunnerService().run(PLOT, supplied, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")


def test_plot_cannot_read_private_roots_or_write_outside_task(roots, market):
    runner = ToolRunnerService()
    for name in ("AIRMOSAIC_AUTH_DIR", "AIRMOSAIC_CONFIG_DIR"):
        with pytest.raises(ToolExecutionError, match="input_outside_data_roots"):
            runner.run(PLOT, {"input_csv": str(roots[name] / "private.csv")}, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")
    with pytest.raises(ToolExecutionError, match="output_outside_current_task"):
        runner.run(PLOT, {"input_csv": str(market), "out_dir": str(market.parent)}, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")
    ambiguous = market.with_name("comma,name.csv")
    ambiguous.write_text("synthetic", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="r_input_path_contains_comma"):
        runner.run(PLOT, {"input_csv": str(ambiguous)}, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")


def test_structure_missing_resource_and_root_overlap(roots, model, monkeypatch):
    (model / "database_R/Prov_code_china.csv").unlink()
    result = ToolRunnerService().run(INSPECT, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")
    assert "model_resource_unavailable" in result["blockers"]
    monkeypatch.setenv("GCAM_RELEASE_DIR", str(roots["AIRMOSAIC_ASSETS_DIR"]))
    with pytest.raises(ToolExecutionError, match="model_overlaps_data_workspace"):
        ToolRunnerService().run(INSPECT, dry_run=True, project_id="example_project", stage="01_socioeconomic_natural_change")


def test_missing_native_r_blocks_without_execution(roots, market, monkeypatch):
    monkeypatch.setattr(tool_r, "r_executable", lambda: None)
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("missing R spawned"))
    result = ToolRunnerService().run(PLOT, {"input_csv": str(market)}, project_id="example_project", stage="01_socioeconomic_natural_change")
    assert result["status"] == "blocked" and "missing_dependency" in result["blockers"]


def require_r():
    if tool_r.r_executable() is None:
        pytest.skip("Native Rscript unavailable; R integration not run")


def test_real_r_isolates_startup_secrets_and_output(tmp_path, roots, market, monkeypatch):
    require_r()
    code = '''
stopifnot(!nzchar(Sys.getenv("SYNTHETIC_SECRET")), !nzchar(Sys.getenv("R_PROFILE_USER")),
          !nzchar(Sys.getenv("AIRMOSAIC_CONFIG_DIR")), !nzchar(Sys.getenv("AIRMOSAIC_AUTH_DIR")))
out <- Sys.getenv("UNIT_PRICE_OUT_DIR")
writeLines("synthetic", file.path(out, "sector_change_2021_2035.png"))
writeLines("synthetic", file.path(out, "sector_change_weighted_mean.csv"))
writeLines(commandArgs(TRUE), file.path(out, "argv.txt"))
cat("synthetic-private-stdout"); message("synthetic-private-stderr")
'''
    runner, _ = synthetic_runner(tmp_path, code, PLOT)
    runner.registry._tools[PLOT]["requirements"]["r_packages"] = ["base"]
    for key in ("SYNTHETIC_SECRET", "R_PROFILE_USER", "R_ENVIRON_USER", "R_LIBS_USER", "UNIT_PRICE_OUT_DIR"):
        monkeypatch.setenv(key, "synthetic-private-marker")
    run_id = "a" * 32
    out = roots["AIRMOSAIC_ASSETS_DIR"] / "results" / "example_project" / run_id / "01_socioeconomic_natural_change" / PLOT / "nested with spaces"
    params = {"input_csv": str(market), "out_dir": str(out), "sectors": "iron and steel,cement"}
    result = runner.run(PLOT, params, run_id=run_id, project_id="example_project", stage="01_socioeconomic_natural_change")
    assert result["status"] == "succeeded", result
    assert result["r_dependencies"]["status"] == "available"
    argv = (out / "argv.txt").read_text().splitlines()
    assert argv == ["--input-csv", str(market), "--sectors", "iron and steel,cement"]
    receipt = (roots["AIRMOSAIC_ASSETS_DIR"] / "results" / "example_project" / run_id / "records" / PLOT / "record.json").read_text()
    for value in ("synthetic-private", str(market), "iron and steel", str(out)):
        assert value not in receipt


@pytest.mark.parametrize("mode,reason", [("dependency", "r_dependency_unavailable"),
                                        ("error", "r_script_failed"), ("partial", "expected_outputs_missing"),
                                        ("timeout", "timeout")])
def test_r_failure_and_partial_results_are_not_success(tmp_path, roots, market, mode, reason):
    require_r()
    scripts = {"dependency": 'stop("must not execute")', "error": 'stop("synthetic-private")',
               "partial": 'writeLines("synthetic", file.path(Sys.getenv("UNIT_PRICE_OUT_DIR"), "sector_change_2021_2035.png"))',
               "timeout": 'Sys.sleep(30)'}
    runner, _ = synthetic_runner(tmp_path, scripts[mode], PLOT)
    runner.registry._tools[PLOT]["requirements"]["r_packages"] = (
        ["AirMosaicSyntheticMissingPackage"] if mode == "dependency" else ["base"])
    result = runner.run(PLOT, {"input_csv": str(market)}, timeout=1 if mode == "timeout" else 30, project_id="example_project", stage="01_socioeconomic_natural_change")
    assert result["status"] == "failed" and result["reason"] == reason, result
    assert "synthetic-private" not in json.dumps(result)
    if mode == "timeout":
        assert result["process_tree_cleanup_confirmed"] is True


def test_actual_plot_preserves_filters_weights_and_artifacts(roots, market):
    require_r()
    result = ToolRunnerService().run(PLOT, {"input_csv": str(market), "sectors": "cement,coke",
                                          "scenarios": "example_scenario"}, timeout=120, project_id="example_project", stage="01_socioeconomic_natural_change")
    if result.get("reason") == "r_dependency_unavailable":
        pytest.skip("Declared R plotting packages unavailable; scientific fixture not run")
    assert result["status"] == "succeeded", result
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results" / "example_project" / result["run_id"] / "01_socioeconomic_natural_change" / PLOT
    assert (output / "sector_change_2021_2035.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    with (output / "sector_change_weighted_mean.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    for row in rows:
        assert float(row["weighted_price"]) == (17.5 if row["sector"] == "cement" else 3)
        assert float(row["quantity_sum"]) == (4 if row["sector"] == "cement" else -2)
        assert int(row["province_count"]) == 2 and int(row["year"]) in (2021, 2035)


def test_plot_registry_no_longer_needs_personal_output_setting(roots, monkeypatch):
    monkeypatch.setenv("UNIT_PRICE_OUT_DIR", str(roots["AIRMOSAIC_AUTH_DIR"]))
    detail = ToolRegistryService().describe_tool(PLOT)
    assert detail["invocation"]["execution_supported"]
    assert all(check["name"] != "UNIT_PRICE_OUT_DIR" for check in detail["availability"]["checks"])


def test_actual_structure_queries_against_synthetic_basex(roots, model):
    require_r()
    java = shutil.which("java")
    if not java:
        pytest.skip("Java unavailable; synthetic BaseX integration not run")
    prep = ExecutionPaths(Path(__file__).absolute().parents[2], "b" * 32, INSPECT, project_id="example_project", stage="01_socioeconomic_natural_change")
    prep.create()
    env = tool_r.environment(child_environment(prep, model), Path("unused.R"), [], prep.temp, None)
    expression = ('if (!all(vapply(c("data.table","rgcam"), requireNamespace, logical(1), quietly=TRUE))) '
                  'quit(status=70L); cat(rgcam:::DEFAULT.MICLASSPATH())')
    code, reason, _, raw = execute([str(tool_r.r_executable()), "--vanilla", "-e", expression],
                                   prep.temp, env, 30, capture=True)
    if code == 70:
        pytest.skip("R inspection packages unavailable; synthetic BaseX integration not run")
    assert code == 0 and reason is None
    classpath = raw.decode("utf-8").strip()
    # Only synthetic data; preserve the R script's fixed query vocabulary.
    xml = '''<scenario name="example_scenario" date="synthetic">
      <model-version>synthetic</model-version><world>
      <region type="region" name="AH"><sector type="sector" name="cement">
      <cost year="2021" unit="synthetic-currency">10</cost>
      <subsector type="subsector" name="example"><technology type="technology" name="example">
      <output type="output" name="cement"><physical-output vintage="2021" unit="Mt">2</physical-output></output>
      <input type="input" name="coal"><demand-physical year="2021">3</demand-physical></input>
      </technology></subsector></sector></region></world></scenario>'''
    query = "db:create('database_basexdb', " + xml + ", 'synthetic.xml')"
    code, reason, _, _ = execute([java, "-cp", classpath, "-Dorg.basex.DBPATH=" + str(model / "output"),
                                  "org.basex.BaseX", "-q", query], prep.temp, env, 30, capture=False)
    assert code == 0 and reason is None, "Synthetic BaseX fixture creation failed"
    # Check the model release receives no result CSV, and all queries return rows.
    result = ToolRunnerService().run(INSPECT, {"max_memory": "128m"}, timeout=120, project_id="example_project", stage="01_socioeconomic_natural_change")
    assert result["status"] == "succeeded", result
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results" / "example_project" / result["run_id"] / "01_socioeconomic_natural_change" / INSPECT
    for name in tool_r.OUTPUTS["gcam_inspect"]:
        with (output / name).open(encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 1 and rows[0]["scenario"] == "example_scenario"
    assert not list(model.rglob("inspect_*.csv"))
