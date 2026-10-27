import pytest

from airmosaic.services import CausalDesignService, DataAccessService, DataCatalogService


def test_catalog_loads_initial_datasets():
    catalog = DataCatalogService()
    records = catalog.list_datasets()
    dataset_ids = {record.dataset_id for record in records}

    assert len(records) == len(dataset_ids)
    assert "worldpop_population_grid" in dataset_ids
    assert "csmar_listed_company_basic" in dataset_ids
    assert "industrial_yearbook_regional_sector" in dataset_ids
    assert "ihme_gbd_mortality_rates" in dataset_ids
    assert catalog.describe_dataset("population")["dataset_id"] == "worldpop_population_grid"
    assert catalog.describe_dataset("gdp")["dataset_id"] == "industrial_yearbook_regional_sector"


def test_catalog_filters_data_acquisition_datasets():
    catalog = DataCatalogService()

    socioeconomic = catalog.list_datasets(layer="01_socioeconomic_natural_change")
    worldpop = catalog.list_datasets(skill="worldpop")
    health = catalog.list_datasets(domain="health")

    assert {record.layer for record in socioeconomic} == {"01_socioeconomic_natural_change"}
    assert {record.skill_id for record in worldpop} == {"worldpop"}
    assert {record.domain for record in health} == {"health"}


def test_data_access_reports_missing_cache(tmp_path):
    catalog = DataCatalogService()
    access = DataAccessService(catalog=catalog, assets_dir=tmp_path)

    availability = access.check_local_availability("population", "*.csv")

    assert availability.dataset_id == "worldpop_population_grid"
    assert availability.cache_root == tmp_path / "data" / "01_socioeconomic_natural_change" / "WorldPop"
    assert availability.existing_files == []
    assert availability.missing_hint is not None


def test_data_access_requires_explicit_workspace(monkeypatch):
    monkeypatch.delenv("AIRMOSAIC_ASSETS_DIR", raising=False)
    with pytest.raises(ValueError, match="Set AIRMOSAIC_ASSETS_DIR"):
        DataAccessService()


def test_data_access_reads_configured_workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("AIRMOSAIC_ASSETS_DIR", str(tmp_path))
    cache = tmp_path / "data" / "01_socioeconomic_natural_change" / "WorldPop" / "raw"
    cache.mkdir(parents=True)
    sample = cache / "synthetic.csv"
    sample.write_text("value\n1\n", encoding="utf-8")

    result = DataAccessService().check_local_availability("population", "raw/*.csv")
    assert result.existing_files == [sample]
    assert result.missing_hint is None


def test_data_access_explicit_workspace_takes_precedence(tmp_path, monkeypatch):
    monkeypatch.setenv("AIRMOSAIC_ASSETS_DIR", str(tmp_path / "environment"))
    explicit = tmp_path / "explicit"
    assert DataAccessService(assets_dir=explicit).assets_dir == explicit


def test_causal_design_plan_is_structured():
    plan = CausalDesignService().draft_plan(
        question="Did clean air policy reduce mortality?",
        treatment="clean air policy",
        outcome="mortality",
    )

    payload = plan.to_dict()
    assert payload["treatment"] == "clean air policy"
    assert payload["outcome"] == "mortality"
    assert payload["identification_strategies"]
    assert payload["refutation_tests"]
