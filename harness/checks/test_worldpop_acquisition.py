from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / (
    "skills/data_acquisition/01_socioeconomic_natural_change/"
    "worldpop/scripts/download_worldpop.py"
)


@pytest.fixture
def worldpop():
    spec = importlib.util.spec_from_file_location("worldpop_acquisition_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("population_year", [2020, "2020", " 2020 "])
def test_exact_population_year_is_selected(worldpop, population_year):
    record = {"popyear": population_year, "data_file": "synthetic_2020.tif"}
    assert worldpop.matches(record, 2020, [], [".tif"])


@pytest.mark.parametrize(
    "population_year", [2000, "2000", None, "", True, 2020.0, "2020-2021", "02020", [], {}]
)
def test_unrelated_year_text_cannot_select_another_data_year(worldpop, population_year):
    record = {
        "popyear": population_year,
        "date": "2020-01-01",
        "title": "Released in 2020",
        "category": "Global per country 2000-2020",
        "data_file": "synthetic_2020.tif",
    }
    assert not worldpop.matches(record, 2020, [], [".tif"])


def test_missing_popyear_has_no_fallback_to_title_or_filename(worldpop):
    record = {"title": "Population 2020", "data_file": "synthetic_2020.tif"}
    assert not worldpop.matches(record, 2020, [], [".tif"])
    assert worldpop.matches(record, None, [], [".tif"])


def test_year_selection_preserves_other_filters(worldpop):
    record = {"popyear": "2020", "title": "Synthetic constrained", "data_file": "synthetic_2020.tif"}
    assert worldpop.matches(record, 2020, ["CONSTRAINED"], [".TIF"])
    assert not worldpop.matches(record, 2020, ["unconstrained"], [".tif"])
    assert not worldpop.matches(record, 2020, [], [".zip"])


def test_discovery_uses_hub_and_keeps_default_tls_verification(worldpop, monkeypatch):
    calls = []

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"popyear": "2020", "data_file": "synthetic_2020.tif"}]}

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(worldpop.requests, "get", get)
    records = worldpop.discover("G2_CN_POP_R25A_1km", "lie", timeout=12)
    assert records[0]["popyear"] == "2020"
    assert calls == [(
        "https://hub.worldpop.org/rest/data/pop/G2_CN_POP_R25A_1km",
        {"params": {"iso3": "LIE"}, "timeout": 12},
    )]


def test_main_filters_data_year_before_limit_without_downloading(worldpop, monkeypatch, tmp_path, capsys):
    root = tmp_path / "task"
    rows = [
        {"popyear": "2000", "category": "2000-2020", "data_file": "synthetic_2000.tif"},
        {"popyear": "2020", "data_file": "synthetic_2020.tif"},
        {"popyear": "2021", "date": "2020", "data_file": "synthetic_2021.tif"},
    ]
    monkeypatch.setattr(worldpop, "discover", lambda project, iso3: rows)

    def reject_download(*args, **kwargs):
        pytest.fail("Metadata-only discovery must not download a file")

    monkeypatch.setattr(worldpop, "download", reject_download)
    monkeypatch.setattr(sys, "argv", [
        "download_worldpop.py", "--project", "G2_CN_POP_R25A_1km", "--iso3", "LIE",
        "--year", "2020", "--limit", "1", "--root", str(root),
    ])
    worldpop.main()
    result = json.loads(capsys.readouterr().out)
    manifest = root / "metadata/G2_CN_POP_R25A_1km_LIE_2020_manifest.json"
    assert json.loads(manifest.read_text(encoding="utf-8")) == [rows[1]]
    assert result["records"] == 1 and result["downloaded"] == []
    assert not (root / "raw").exists()
