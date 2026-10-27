"""Synthetic process tests; no authenticated sessions, downloads or model jobs."""

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

import pytest
import yaml

from airmosaic_core.services import ToolExecutionError, ToolRegistryError, ToolRegistryService, ToolRunnerService
from airmosaic_core.services import tool_process, tool_runner
from airmosaic_core.services.tool_execution_paths import parse_parameters


ROOT = Path(__file__).absolute().parents[1]


@pytest.fixture
def roots(tmp_path, monkeypatch):
    result = {}
    for name, child in [("AIRMOSAIC_LOCAL_WORKSPACE", "workspace with spaces"),
                        ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")]:
        path = tmp_path / child
        path.mkdir()
        monkeypatch.setenv(name, str(path))
        result[name] = path
    monkeypatch.delenv("GCAM_RELEASE_DIR", raising=False)
    return result


def synthetic_runner(tmp_path, code=None, tool_id="worldpop_download"):
    repo = tmp_path / "synthetic-repo"
    (repo / "catalog/tools").mkdir(parents=True)
    (repo / "catalog/schemas").mkdir()
    shutil.copyfile(ROOT / "catalog/schemas/tool.schema.json", repo / "catalog/schemas/tool.schema.json")
    data = yaml.safe_load((ROOT / f"catalog/tools/{tool_id}.yaml").read_text(encoding="utf-8"))
    guide = repo / data["documentation"]
    guide.parent.mkdir(parents=True)
    guide.write_text("Synthetic public guide", encoding="utf-8")
    script = repo / data["entrypoint"]["path"]
    script.parent.mkdir(parents=True)
    script.write_text(code or '''import argparse, json, os
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--project', required=True)
p.add_argument('--root', required=True)
p.add_argument('--contains')
a = p.parse_args()
Path(a.root).joinpath('probe.json').write_text(json.dumps({
    'secret_inherited': 'AIRMOSAIC_TEST_SECRET' in os.environ,
    'auth_inherited': 'AIRMOSAIC_AUTH_DIR' in os.environ,
    'config_inherited': 'AIRMOSAIC_CONFIG_DIR' in os.environ,
    'home': os.environ.get('HOME'), 'argument': a.contains}), encoding='utf-8')
print('synthetic-private-stdout', os.environ.get('HOME'))
''', encoding="utf-8")
    data["requirements"]["python_packages"] = []
    data["requirements"]["executables"] = []
    (repo / f"catalog/tools/{tool_id}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return ToolRunnerService(ToolRegistryService(repo)), repo


def test_dry_run_is_read_only_and_reports_permissions(tmp_path, roots, monkeypatch):
    runner, _ = synthetic_runner(tmp_path)
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("dry-run spawned"))
    result = runner.run("worldpop_download", {"project": "wpgp"}, dry_run=True)
    assert result["status"] == "dry_run" and not result["can_execute"]
    assert result["blockers"] == ["network_permission_required"]
    assert list(roots["AIRMOSAIC_LOCAL_WORKSPACE"].iterdir()) == []


def test_real_process_has_isolated_environment_and_redacted_receipt(tmp_path, roots, monkeypatch):
    runner, _ = synthetic_runner(tmp_path)
    monkeypatch.setenv("AIRMOSAIC_TEST_SECRET", "synthetic-private-key")
    marker = '--root=synthetic-private-argument; $(never-execute)'
    result = runner.run("worldpop_download", {"project": "wpgp", "contains": marker}, allow_network=True)
    assert result["status"] == "succeeded", result
    workspace = roots["AIRMOSAIC_LOCAL_WORKSPACE"]
    probe = json.loads((workspace / "output" / result["run_id"] / "worldpop_download/probe.json").read_text())
    assert not probe["secret_inherited"] and not probe["auth_inherited"] and not probe["config_inherited"]
    assert Path(probe["home"]) == workspace / "temp" / result["run_id"]
    assert probe["argument"] == marker
    raw = (workspace / "runs" / result["run_id"] / "record.json").read_text()
    for value in (str(workspace), "synthetic-private", marker, str(roots["AIRMOSAIC_AUTH_DIR"])):
        assert value not in raw and value not in json.dumps(result)
    assert result["parameters"] == {"contains": "string", "project": "string", "root": "string"}


@pytest.mark.parametrize("params", [
    {}, {"project": "wpgp", "unknown": "synthetic-private"}, {"project": "../other"},
    {"project": "wpgp", "year": True}, {"project": "wpgp", "year": "2020"},
    {"project": "wpgp", "limit": -1}, {"project": "wpgp", "contains": "x\nprivate"},
    {"project": "wpgp", "contains": "a" * 4097},
])
def test_invalid_parameters_never_spawn_or_write(tmp_path, roots, monkeypatch, params):
    runner, _ = synthetic_runner(tmp_path)
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("invalid parameters spawned"))
    with pytest.raises(ToolExecutionError, match="invalid_tool_parameters"):
        runner.run("worldpop_download", params)
    assert not list(roots["AIRMOSAIC_LOCAL_WORKSPACE"].iterdir())


@pytest.mark.parametrize("destination", ["cache", "auth", "config", "repo", "parent", "unc", "ads"])
def test_bad_output_paths_rejected_before_execution(tmp_path, roots, destination):
    runner, repo = synthetic_runner(tmp_path)
    workspace = roots["AIRMOSAIC_LOCAL_WORKSPACE"]
    choices = {"cache": str(workspace / "data_cache"), "auth": str(roots["AIRMOSAIC_AUTH_DIR"]),
               "config": str(roots["AIRMOSAIC_CONFIG_DIR"]), "repo": str(repo),
               "parent": str(workspace / "output" / ".." / "outside"),
               "unc": r"\\example.invalid\share", "ads": str(workspace / "output" / "file:stream")}
    with pytest.raises(ToolExecutionError):
        runner.run("worldpop_download", {"project": "wpgp", "root": choices[destination]}, dry_run=True)
    assert not list(workspace.iterdir())


def test_overlap_and_git_roots_rejected(roots, tmp_path, monkeypatch):
    runner, _ = synthetic_runner(tmp_path)
    monkeypatch.setenv("AIRMOSAIC_AUTH_DIR", str(roots["AIRMOSAIC_CONFIG_DIR"]))
    with pytest.raises(ToolExecutionError, match="overlapping_roots"):
        runner.run("worldpop_download", {"project": "wpgp"}, dry_run=True)
    monkeypatch.setenv("AIRMOSAIC_AUTH_DIR", str(roots["AIRMOSAIC_AUTH_DIR"]))
    (roots["AIRMOSAIC_CONFIG_DIR"] / ".git").write_text("gitdir: synthetic", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="invalid_separated_roots"):
        runner.run("worldpop_download", {"project": "wpgp"}, dry_run=True)


def test_blocked_run_has_receipt_but_no_process(tmp_path, roots, monkeypatch):
    runner, _ = synthetic_runner(tmp_path)
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: pytest.fail("blocked tool spawned"))
    result = runner.run("worldpop_download", {"project": "wpgp"})
    assert result["status"] == "blocked"
    assert (roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "runs" / result["run_id"] / "record.json").is_file()


def test_run_id_reuse_and_arbitrary_identifiers_rejected(tmp_path, roots):
    runner, _ = synthetic_runner(tmp_path)
    run_id = "a" * 32
    runner.run("worldpop_download", {"project": "wpgp"}, run_id=run_id)
    with pytest.raises(ToolExecutionError, match="already_exists"):
        runner.run("worldpop_download", {"project": "wpgp"}, run_id=run_id)
    for invalid in ("private-name", "../escape", "A" * 32):
        with pytest.raises(ToolExecutionError, match="invalid_run_id"):
            runner.run("worldpop_download", {"project": "wpgp"}, run_id=invalid)


@pytest.mark.parametrize("flags", [{"allow_network": "false"}, {"confirm_browser_session": 1}])
def test_sdk_permission_flags_are_strict_booleans(tmp_path, roots, flags):
    runner, _ = synthetic_runner(tmp_path)
    with pytest.raises(ToolExecutionError, match="invalid_permission_flags"):
        runner.run("worldpop_download", {"project": "wpgp"}, **flags)


@pytest.mark.parametrize("raw", ['[]', '{"project":1,"project":2}', '{"value":NaN}', '{'])
def test_json_contract_no_raw_exception(raw):
    with pytest.raises(ToolExecutionError):
        parse_parameters(raw)


def test_only_explicit_nonsecret_parameter_file_is_read(tmp_path, roots, monkeypatch):
    runner, _ = synthetic_runner(tmp_path)
    config = roots["AIRMOSAIC_CONFIG_DIR"]
    parameter_file = config / "task.json"
    parameter_file.write_text('{"project":"wpgp"}', encoding="utf-8")
    for root in (config, roots["AIRMOSAIC_AUTH_DIR"]):
        (root / "never-read.json").write_text("synthetic-private", encoding="utf-8")
    original = Path.open
    def guarded(path, *args, **kwargs):
        assert path.name != "never-read.json"
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)
    result = runner.run("worldpop_download", params_file=str(parameter_file), dry_run=True)
    assert result["status"] == "dry_run"
    with pytest.raises(ToolExecutionError, match="outside_allowed_roots"):
        runner.run("worldpop_download", params_file=str(roots["AIRMOSAIC_AUTH_DIR"] / "never-read.json"))


def test_missing_dependencies_and_browser_attestation(roots, monkeypatch):
    from importlib.metadata import PackageNotFoundError
    from airmosaic_core.services import tool_readiness
    monkeypatch.setattr(tool_readiness.metadata, "version", lambda _: (_ for _ in ()).throw(PackageNotFoundError()))
    params = {key: "1" for key in ("years", "locations", "causes", "ages", "sexes", "measures", "metrics")}
    runner = ToolRunnerService()
    result = runner.run("ihme_gbd_fetch_results", params, dry_run=True)
    assert set(result["blockers"]) == {"missing_dependency", "network_permission_required", "browser_session_confirmation_required"}
    confirmed = runner.run("ihme_gbd_fetch_results", params, dry_run=True, allow_network=True, confirm_browser_session=True)
    assert confirmed["blockers"] == ["missing_dependency"] and confirmed["authentication"] == "unverified"


def test_timeout_and_nonzero_exit_leave_sanitized_receipts(tmp_path, roots):
    runner, _ = synthetic_runner(tmp_path, "import time; time.sleep(30)")
    result = runner.run("worldpop_download", {"project": "wpgp"}, allow_network=True, timeout=1)
    assert result["status"] == "failed" and result["reason"] == "timeout"
    assert result["process_tree_cleanup_confirmed"] is True


def test_nonzero_stderr_does_not_leak(tmp_path, roots):
    runner, _ = synthetic_runner(tmp_path, "import sys; print('synthetic-private',file=sys.stderr); sys.exit(7)")
    result = runner.run("worldpop_download", {"project": "wpgp"}, allow_network=True)
    assert result["status"] == "failed" and result["exit_code"] == 7
    assert "synthetic-private" not in json.dumps(result)


def test_bounded_capture_of_owned_process(tmp_path, roots):
    from airmosaic_core.services.tool_execution_paths import ExecutionPaths
    paths = ExecutionPaths(ROOT, "b" * 32, "airmosaic_list_datasets")
    paths.create()
    result = tool_process.execute([sys.executable, "-I", "-c", "print('x'*2000000)"], paths.temp,
                                  tool_process.child_environment(paths, None), 10, capture=True)
    assert result[1] == "output_limit" and result[3] == b""


def test_descendant_holding_stdout_cannot_hang_runner(roots):
    from airmosaic_core.services.tool_execution_paths import ExecutionPaths
    paths = ExecutionPaths(ROOT, "c" * 32, "airmosaic_list_datasets")
    paths.create()
    code = "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])"
    started = time.monotonic()
    result = tool_process.execute([sys.executable, "-I", "-c", code], paths.temp,
                                  tool_process.child_environment(paths, None), 1, capture=True)
    assert time.monotonic() - started < 4
    assert result[1] == "output_stream_open" and result[2] is True


def test_interruption_cleans_owned_process(roots, monkeypatch):
    from airmosaic_core.services.tool_execution_paths import ExecutionPaths
    paths = ExecutionPaths(ROOT, "d" * 32, "airmosaic_list_datasets")
    paths.create()
    owned = []
    def interrupt(process, *args):
        owned.append(process)
        raise KeyboardInterrupt
    monkeypatch.setattr(tool_process, "_monitor", interrupt)
    with pytest.raises(KeyboardInterrupt):
        tool_process.execute([sys.executable, "-I", "-c", "import time;time.sleep(30)"], paths.temp,
                             tool_process.child_environment(paths, None), 30, capture=False)
    assert owned[0].poll() is not None


def test_interruption_finalizes_receipt(tmp_path, roots, monkeypatch):
    runner, _ = synthetic_runner(tmp_path)
    monkeypatch.setattr(tool_runner, "execute", lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt()))
    result = runner.run("worldpop_download", {"project": "wpgp"}, allow_network=True)
    assert result["status"] == "failed" and result["reason"] == "interrupted"
    assert "finished_at" in result


def test_requested_nested_output_directory_is_created(tmp_path, roots):
    runner, _ = synthetic_runner(tmp_path)
    run_id = "e" * 32
    nested = roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "output" / run_id / "worldpop_download" / "nested"
    dry = runner.run("worldpop_download", {"project": "wpgp", "root": str(nested)}, run_id=run_id, dry_run=True, allow_network=True)
    assert dry["can_execute"] and not nested.exists()
    result = runner.run("worldpop_download", {"project": "wpgp", "root": str(nested)}, run_id=run_id, allow_network=True)
    assert result["status"] == "succeeded" and (nested / "probe.json").is_file()


def test_real_core_cli_and_private_free_text_summary(roots):
    runner = ToolRunnerService()
    result = runner.run("airmosaic_list_datasets")
    assert result["status"] == "succeeded" and result["result_summary"]["item_count"] > 0
    params = {key: "synthetic-private-free-text" for key in ("question", "treatment", "outcome")}
    causal = runner.run("airmosaic_draft_causal_plan", params)
    assert causal["status"] == "succeeded" and "synthetic-private" not in json.dumps(causal)


@pytest.mark.parametrize("tool_id", ["pm25_hia_calculate_template", "csmar_browser_download", "gcam_configuration_reference", "airmosaic_run_tool"])
def test_unsupported_entries_never_execute(roots, tool_id):
    with pytest.raises(ToolExecutionError, match="execution_not_supported"):
        ToolRunnerService().run(tool_id)


def test_input_file_policy(roots):
    runner = ToolRunnerService()
    auth_file = roots["AIRMOSAIC_AUTH_DIR"] / "private.csv"
    auth_file.write_text("synthetic", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="input_outside_data_roots"):
        runner.run("gcam_aggregate_provinces", {"input_csv": str(auth_file)}, dry_run=True)
    data = roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "data_cache/gcam/example.csv"
    data.parent.mkdir(parents=True)
    data.write_text("synthetic", encoding="utf-8")
    assert runner.run("gcam_aggregate_provinces", {"input_csv": str(data)}, dry_run=True)["status"] == "dry_run"


def test_manifest_cannot_enable_unreviewed_policy(tmp_path, roots):
    runner, repo = synthetic_runner(tmp_path)
    manifest = repo / "catalog/tools/worldpop_download.yaml"
    data = deepcopy(runner.registry._tools["worldpop_download"])
    data.pop("manifest")
    data["execution"]["path_parameters"] = {}
    manifest.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ToolRegistryError, match="reviewed adapter"):
        ToolRegistryService(repo)


def load_script(path):
    spec = importlib.util.spec_from_file_location("synthetic_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("url", ["https://example.invalid/..", "https://example.invalid/%2e%2e",
                                    "https://example.invalid/%2Fescape", "https://example.invalid/C:escape",
                                    "https://example.invalid/CON.tif", "https://example.invalid/a%5Cb.tif"])
def test_remote_filename_cannot_escape_task(url):
    pytest.importorskip("requests")
    script = load_script(ROOT / "skills/data_acquisition/01_socioeconomic_natural_change/worldpop/scripts/download_worldpop.py")
    with pytest.raises(ValueError):
        script.safe_name(url)
    assert script.safe_name("https://example.invalid/valid.tif?signature=synthetic-private") == "valid.tif"


def test_real_csmar_zip_processing_keeps_input_read_only(roots):
    pd = pytest.importorskip("pandas")
    pytest.importorskip("openpyxl")
    import io
    workspace = roots["AIRMOSAIC_LOCAL_WORKSPACE"]
    source = workspace / "data_cache/csmar/source.zip"
    source.parent.mkdir(parents=True)
    columns = ["Symbol", "EndDate", "IndustryName", "IndustryNameC", "IndustryNameD", "IndustryCode",
               "IndustryCodeC", "IndustryCodeD", "ShortName", "FullName", "MAINBUSSINESS", "SocialCreditCode",
               "PROVINCE", "CITY", "LISTINGSTATE"]
    row = {key: "synthetic" for key in columns}
    row.update(Symbol="000001", EndDate="2020-12-31", IndustryName="cement")
    buffer = io.BytesIO()
    pd.DataFrame([row]).to_excel(buffer, index=False)
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("../../STK_LISTEDCOINFOANL.xlsx", buffer.getvalue())
    before = source.read_bytes()
    result = ToolRunnerService().run("csmar_process_company_info", {"zip": str(source)})
    assert result["status"] == "succeeded", result
    assert source.read_bytes() == before and list(source.parent.iterdir()) == [source]
    output = workspace / "output" / result["run_id"] / "csmar_process_company_info"
    assert len(list(output.glob("*.csv"))) == 2 and len(list(output.glob("*.xlsx"))) == 1


def test_real_gcam_aggregate_synthetic_rows(roots):
    pd = pytest.importorskip("pandas")
    workspace = roots["AIRMOSAIC_LOCAL_WORKSPACE"]
    source = workspace / "data_cache/gcam/rows.csv"
    source.parent.mkdir(parents=True)
    pd.DataFrame([
        {"scenario": "synthetic", "source": "marketplace", "sector": "cement", "year": 2020,
         "region": region, "price": price, "quantity": quantity}
        for region, price, quantity in [("AH", 10, 2), ("BJ", 20, 1), ("China", 900, 100), ("Global", 900, 100)]
    ]).to_csv(source, index=False)
    result = ToolRunnerService().run("gcam_aggregate_provinces", {"input_csv": str(source)})
    assert result["status"] == "succeeded", result
    output = workspace / "output" / result["run_id"] / "gcam_aggregate_provinces/province_aggregate.csv"
    row = pd.read_csv(output).iloc[0]
    assert row["weighted_price"] == pytest.approx(40 / 3) and row["quantity_sum"] == 3
    assert row["province_count"] == 2


def test_gcam_preflight_checks_selected_database_and_jar(roots, tmp_path, monkeypatch):
    from airmosaic_core.services import tool_readiness
    model = tmp_path / "model"
    (model / "libs/jars").mkdir(parents=True)
    monkeypatch.setenv("GCAM_RELEASE_DIR", str(model))
    monkeypatch.setattr(tool_readiness, "executable_available", lambda _: True)
    monkeypatch.setattr(tool_readiness.metadata, "version", lambda _: "1.0")
    runner = ToolRunnerService()
    params = {"scenarios": "synthetic", "sectors": "cement"}
    dry = runner.run("gcam_extract_market_sector", params, dry_run=True)
    assert set(dry["blockers"]) == {"basex_jar_unavailable", "scenario_database_unavailable"}
    (model / "libs/jars/BaseX-synthetic.jar").write_bytes(b"synthetic")
    (model / "output/synthetic/database_basexdb").mkdir(parents=True)
    assert runner.run("gcam_extract_market_sector", params, dry_run=True)["can_execute"]
    with pytest.raises(ToolExecutionError, match="invalid_scenario_identifier"):
        runner.run("gcam_extract_market_sector", {**params, "scenarios": "a..b"}, dry_run=True)


def test_reparse_input_is_rejected_before_target_access(roots, monkeypatch):
    import stat
    from types import SimpleNamespace
    original = Path.lstat
    def info(path, *args, **kwargs):
        if path.name == "redirect":
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        assert path.name != "do-not-probe.csv"
        return original(path, *args, **kwargs)
    (roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "data_cache").mkdir()
    monkeypatch.setattr(Path, "lstat", info)
    with pytest.raises(ToolExecutionError, match="invalid_local_path"):
        ToolRunnerService().run("gcam_aggregate_provinces", {
            "input_csv": str(roots["AIRMOSAIC_LOCAL_WORKSPACE"] / "data_cache/redirect/do-not-probe.csv")}, dry_run=True)


def test_cache_query_redacts_filenames_and_rejects_traversal(roots):
    from airmosaic_core.services import DataCatalogService
    workspace = roots["AIRMOSAIC_LOCAL_WORKSPACE"]
    meta = DataCatalogService().describe_dataset("worldpop_population_grid")
    root = Path((meta.get("cache_root") or meta["default_cache_root"]).replace("${AIRMOSAIC_LOCAL_WORKSPACE}", str(workspace)))
    root.mkdir(parents=True)
    (root / "synthetic-private-filename.tif").write_text("synthetic", encoding="utf-8")
    runner = ToolRunnerService()
    result = runner.run("airmosaic_check_availability", {"dataset_id": "worldpop_population_grid"})
    assert result["status"] == "succeeded" and result["result_summary"] == {"matched_file_count": 1}
    assert "synthetic-private" not in json.dumps(result)
    with pytest.raises(ToolExecutionError, match="invalid_cache_pattern"):
        runner.run("airmosaic_check_availability", {"dataset_id": "worldpop_population_grid", "pattern": "../*"}, dry_run=True)


@pytest.mark.parametrize("arguments", [["--timeout", "synthetic-private"], ["--synthetic-private"], ["--params", "synthetic-private"]])
def test_cli_parser_errors_do_not_echo_values(roots, arguments):
    result = subprocess.run([sys.executable, "-B", "-m", "airmosaic_core.cli", "run-tool",
                             "worldpop_download", *arguments], capture_output=True, text=True, timeout=30)
    assert result.returncode == 2 and "synthetic-private" not in result.stderr


def test_cli_errors_are_value_free(roots):
    result = subprocess.run([sys.executable, "-B", "-m", "airmosaic_core.cli", "run-tool",
                             "worldpop_download", "--params", '{"project":"synthetic-private/../"}'],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 2 and "synthetic-private" not in result.stderr
    assert json.loads(result.stderr)["reason"] == "invalid_tool_parameters"
