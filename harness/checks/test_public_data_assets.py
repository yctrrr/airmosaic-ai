"""Published inputs stay distinct from synthetic fixtures and writable results."""

import hashlib
import json
from pathlib import Path

import pytest

from runtime.services.public_data_assets import is_public_dataset
from runtime.services.tool_execution_paths import ExecutionPaths, ToolExecutionError
from runtime.services.toy_assets import is_public_toy


ROOT = Path(__file__).resolve().parents[2]
RELATIVE = "data/03_atmospheric_transport/AQ-Bench/v1/AQbench_dataset.csv"


@pytest.fixture
def public_input(tmp_path):
    repo = tmp_path / "repo"
    source = repo / "assets" / RELATIVE
    source.parent.mkdir(parents=True)
    # Above the toy size limit, while still synthetic test content.
    source.write_bytes(b"sample,target\n" + b"1,2\n" * 270000)
    entry = {"bytes": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    dataset = {"publication_authorized": True, "license": {"id": "CC-BY-4.0"},
               "source": "https://example.invalid/dataset", "attribution": "Synthetic test creator",
               "files": {RELATIVE: entry}}
    manifest = repo / "assets/public-data-manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1, "data_type": "published_public_datasets",
                                    "datasets": [dataset]}), encoding="utf-8")
    return repo, source, manifest


def test_published_csv_is_read_only_and_is_not_a_toy(public_input, tmp_path, monkeypatch):
    repo, source, _ = public_input
    for key, name in (("AIRMOSAIC_ASSETS_DIR", "private_assets"), ("AIRMOSAIC_CONFIG_DIR", "settings"),
                      ("AIRMOSAIC_AUTH_DIR", "auth")):
        root = tmp_path / name; root.mkdir(); monkeypatch.setenv(key, str(root))
    assert is_public_dataset(source, repo)
    assert not is_public_toy(source, repo)
    paths = ExecutionPaths(repo, "a" * 32, "example", "example_project", "03_atmospheric_transport")
    assert paths.parameter("assets/" + RELATIVE, "input_file") == source
    with pytest.raises(ToolExecutionError, match="output_outside_current_task"):
        paths.parameter("assets/" + RELATIVE, "output_file")


@pytest.mark.parametrize("change", ["changed", "unlisted", "unapproved", "license", "duplicate", "size", "nested_git"])
def test_public_input_failures_are_not_admitted(public_input, change):
    repo, source, manifest = public_input
    doc = json.loads(manifest.read_text()); dataset = doc["datasets"][0]
    if change == "changed":
        raw = source.read_bytes(); source.write_bytes(b"X" + raw[1:])
    elif change == "unlisted":
        source = source.with_name("unlisted.csv")
    elif change == "unapproved": dataset["publication_authorized"] = False
    elif change == "license": dataset["license"] = {}
    elif change == "duplicate": doc["datasets"].append(dataset)
    elif change == "size": dataset["files"][RELATIVE]["bytes"] += 1
    else: (source.parent / ".git").write_text("gitdir: synthetic")
    manifest.write_text(json.dumps(doc), encoding="utf-8")
    assert not is_public_dataset(source, repo)


def test_repository_snapshot_has_declared_source_hashes():
    doc = json.loads((ROOT / "assets/public-data-manifest.json").read_text())
    for dataset in doc["datasets"]:
        for relative, entry in dataset["files"].items():
            path = ROOT / "assets" / relative
            assert path.stat().st_size == entry["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
            assert is_public_dataset(path, ROOT) and not is_public_toy(path, ROOT)
