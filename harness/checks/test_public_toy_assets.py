"""Public fixtures are read-only; real/generated assets remain outside Git."""

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from airmosaic.services import DataAccessService, ToolExecutionError, ToolRunnerService
from airmosaic.services.asset_layout import STAGES
from airmosaic.services.toy_assets import is_public_toy
from airmosaic.services.tool_execution_paths import ExecutionPaths


ROOT = Path(__file__).absolute().parents[2]
DATA = "assets/data/01_socioeconomic_natural_change/ExampleMarketRows/v1/rows.csv"
REFERENCE = "assets/results/toy_example/reference/01_socioeconomic_natural_change/gcam_aggregate_provinces/province_aggregate.csv"


@pytest.fixture
def roots(tmp_path, monkeypatch):
    result = {}
    for name, child in (("AIRMOSAIC_ASSETS_DIR", "assets"), ("AIRMOSAIC_CONFIG_DIR", "config"),
                        ("AIRMOSAIC_AUTH_DIR", "auth")):
        path = tmp_path / child
        path.mkdir()
        monkeypatch.setenv(name, str(path))
        result[name] = path
    return result


def test_existing_tool_runs_public_toy_and_preserves_inputs(roots):
    pd = pytest.importorskip("pandas")
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (DATA, REFERENCE)}
    result = ToolRunnerService().run("gcam_aggregate_provinces", params_file="config/examples/run-tool/toy-aggregate.json",
                                    project_id="toy_example", stage=STAGES[0])
    assert result["status"] == "succeeded", result
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/toy_example" / result["run_id"] / STAGES[0] / "gcam_aggregate_provinces/province_aggregate.csv"
    actual = pd.read_csv(output).iloc[0]
    expected = pd.read_csv(ROOT / REFERENCE).iloc[0]
    for name in ("weighted_price", "quantity_sum", "province_count"):
        assert actual[name] == pytest.approx(expected[name])
    assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in before.items())


def test_public_results_are_also_read_only_inputs(roots):
    paths = ExecutionPaths(ROOT, "a" * 32, "example_tool", "example_project", STAGES[3])
    assert paths.parameter(REFERENCE, "input_file") == ROOT / REFERENCE
    with pytest.raises(ToolExecutionError, match="output_outside_current_task"):
        paths.parameter(REFERENCE, "output_file")


def test_unlisted_and_changed_fixtures_are_rejected_without_reading_other_files(tmp_path):
    repo = tmp_path / "repo"
    toy = repo / DATA
    toy.parent.mkdir(parents=True)
    toy.write_bytes((ROOT / DATA).read_bytes())
    shutil.copyfile(ROOT / "assets/toy-manifest.json", repo / "assets/toy-manifest.json")
    assert is_public_toy(toy, repo)
    toy.write_text("synthetic changed fixture", encoding="utf-8")
    assert not is_public_toy(toy, repo)
    assert not is_public_toy(repo / "assets/unlisted.csv", repo)
    (repo / "assets/toy-manifest.json").write_text('{"schema_version":1,"synthetic":true,"files":[]}', encoding="utf-8")
    assert not is_public_toy(toy, repo)


def test_public_root_cannot_be_selected_for_real_outputs(roots, monkeypatch):
    monkeypatch.setenv("AIRMOSAIC_ASSETS_DIR", str(ROOT / "assets"))
    with pytest.raises(ToolExecutionError, match="invalid_separated_roots"):
        ExecutionPaths(ROOT, "a" * 32, "example_tool", "example_project", STAGES[0])


def test_nested_git_under_results_cannot_receive_receipts(roots):
    results = roots["AIRMOSAIC_ASSETS_DIR"] / "results"
    results.mkdir()
    (results / ".git").write_text("gitdir: synthetic", encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="generated_paths_inside_git"):
        ExecutionPaths(ROOT, "a" * 32, "example_tool", "example_project", STAGES[0])
    assert sorted(p.name for p in results.iterdir()) == [".git"]


def test_direct_availability_rejects_git_root_and_parent_pattern(roots, tmp_path):
    repo = tmp_path / "synthetic_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    with pytest.raises(ValueError, match="invalid_private_assets_root"):
        DataAccessService(assets_dir=repo)
    access = DataAccessService(assets_dir=roots["AIRMOSAIC_ASSETS_DIR"])
    with pytest.raises(ValueError, match="invalid_asset_pattern"):
        access.check_local_availability("population", "../*.json")


def test_only_allowlisted_public_assets_are_visible_to_git():
    import subprocess
    hidden = subprocess.run(["git", "check-ignore", "assets/data/private.csv", "assets/results/private_project/result.csv"],
                            cwd=ROOT, capture_output=True, text=True)
    assert hidden.returncode == 0
    assert len(hidden.stdout.splitlines()) == 2
    public = subprocess.run(["git", "check-ignore", DATA, REFERENCE], cwd=ROOT, capture_output=True, text=True)
    assert public.returncode == 1 and not public.stdout


def test_public_toy_hashes_survive_windows_style_git_checkout(tmp_path):
    import subprocess
    prefix = str(tmp_path / "checkout") + "/"
    paths = [DATA, REFERENCE, "assets/toy-manifest.json"]
    result = subprocess.run(["git", "-c", "core.autocrlf=true", "checkout-index", "--prefix=" + prefix,
                             "--", *paths], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    manifest = json.loads((tmp_path / "checkout/assets/toy-manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((tmp_path / "checkout/assets" / name).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize("area", ["config", "data", "results"])
def test_private_parameters_cannot_be_read_from_nested_git(roots, area):
    parent = roots["AIRMOSAIC_CONFIG_DIR"] if area == "config" else roots["AIRMOSAIC_ASSETS_DIR"] / area
    checkout = parent / "nested_checkout"
    checkout.mkdir(parents=True)
    (checkout / ".git").mkdir()
    parameters = checkout / "params.json"
    parameters.write_text('{}', encoding="utf-8")
    paths = ExecutionPaths(ROOT, "a" * 32, "example_tool", "example_project", STAGES[0])
    with pytest.raises(ToolExecutionError, match="parameter_file_inside_git"):
        paths.read_parameters(str(parameters), ROOT)
