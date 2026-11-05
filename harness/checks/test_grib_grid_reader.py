"""Actual ecCodes synthetic messages, with no external inputs."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ec = pytest.importorskip("eccodes")
pytest.importorskip("pandas")
ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "grib_grid", ROOT / "skills/model/shared/spatial_analysis/scripts/python/grib_grid.py")
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)


def contract(param=167, short="2t", units="K"):
    return {"param_id": param, "short_name": short, "units": units,
            "type_of_level": "surface", "level": 0, "centre": "ecmf"}


def write_grib(path, messages):
    with path.open("wb") as stream:
        for overrides, values in messages:
            h = ec.codes_grib_new_from_samples("regular_ll_sfc_grib1")
            try:
                settings = {"Ni": 3, "Nj": 2, "latitudeOfFirstGridPointInDegrees": 31,
                            "latitudeOfLastGridPointInDegrees": 30,
                            "longitudeOfFirstGridPointInDegrees": 100,
                            "longitudeOfLastGridPointInDegrees": 102,
                            "iDirectionIncrementInDegrees": 1, "jDirectionIncrementInDegrees": 1,
                            "dataDate": 20200101, "dataTime": 0, "paramId": 167}
                settings.update(overrides)
                for key, value in settings.items():
                    ec.codes_set(h, key, value)
                ec.codes_set_values(h, values)
                ec.codes_write(h, stream)
            finally:
                ec.codes_release(h)


def plane(offset=0):
    return (np.array([31, 30])[:, None] * 2 + np.array([100, 101, 102])[None, :] * 3 + offset).ravel()


def test_native_plane_time_sort_and_selection(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({"dataTime": 300}, plane(3)), ({}, plane()),
                      ({"paramId": 168}, plane(-2))])
    result = reader.read_regular_grib([path], {"t2m": contract(), "d2m": contract(168, "2d")},
                                      requested_fields=["t2m"], max_cells=12)
    np.testing.assert_array_equal(result["x"], [100, 101, 102])
    np.testing.assert_array_equal(result["y"], [31, 30])
    np.testing.assert_allclose(result["fields"]["t2m"], [plane().reshape(2, 3), plane(3).reshape(2, 3)])
    assert result["times_utc"].strftime("%Y-%m-%dT%H:%MZ").tolist() == ["2020-01-01T00:00Z", "2020-01-01T03:00Z"]
    assert result["metadata"]["message_count"] == 3
    assert result["metadata"]["decoded_message_count"] == 2
    assert str(tmp_path) not in repr(result["metadata"])


@pytest.mark.parametrize("messages,contracts,reason", [
    ([({}, plane()), ({}, plane())], {"t": contract()}, "duplicate_variable_time"),
    ([({}, plane())], {"t": contract(units="degC")}, "units_mismatch"),
    ([({"paramId": 168}, plane())], {"t": contract()}, "unknown_or_ambiguous_identity"),
    ([({}, plane()), ({"dataTime": 300, "longitudeOfFirstGridPointInDegrees": 101,
                           "longitudeOfLastGridPointInDegrees": 103}, plane())], {"t": contract()}, "grid_mismatch"),
    ([({"stepType": "accum", "endStep": 3}, plane())], {"t": contract()}, "unsupported_forecast_or_statistic"),
    ([({"endStep": 3}, plane())], {"t": contract()}, "unsupported_forecast_or_statistic"),
    ([({"dataType": "fc"}, plane())], {"t": contract()}, "unsupported_forecast_or_statistic"),
])
def test_refusals(tmp_path, messages, contracts, reason):
    path = tmp_path / "synthetic.grib"
    write_grib(path, messages)
    with pytest.raises(ValueError, match="grib_grid_" + reason):
        reader.read_regular_grib([path], contracts)


def test_bitmap_missing_and_absent_time(tmp_path):
    path = tmp_path / "synthetic.grib"
    values = plane()
    values[2] = 9999
    write_grib(path, [({"bitmapPresent": 1, "missingValue": 9999}, values),
                      ({"paramId": 168, "dataTime": 300}, plane())])
    result = reader.read_regular_grib([path], {"t": contract(), "d": contract(168, "2d")})
    assert np.isnan(result["fields"]["t"][0, 0, 2])
    assert np.isnan(result["fields"]["t"][1]).all()
    assert result["metadata"]["missing_value_counts"]["t"] == 1
    assert result["metadata"]["absent_time_counts"] == {"t": 1, "d": 1}


def test_limits_and_sanitized_error(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane()), ({"dataTime": 300}, plane())])
    for limits, reason in [({"max_messages": 1}, "message_limit"),
                           ({"max_cells": 6}, "cell_limit")]:
        with pytest.raises(ValueError, match="grib_grid_" + reason):
            reader.read_regular_grib([path], {"t": contract()}, **limits)
    with pytest.raises(ValueError) as exc:
        reader.read_regular_grib([tmp_path / "private-absent.grib"], {"t": contract()})
    assert str(exc.value) == "grib_grid_decode_failed"


def test_skipped_field_identity_is_validated(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane()), ({"paramId": 168}, plane())])
    with pytest.raises(ValueError, match="units_mismatch"):
        reader.read_regular_grib([path], {"t": contract(), "d": contract(168, "2d", "bad")}, requested_fields=["t"])


@pytest.mark.parametrize("param,short,units", [(167, "2t", "K"), (168, "2d", "K"),
    (165, "10u", "m s**-1"), (166, "10v", "m s**-1"), (134, "sp", "Pa"),
    (210207, "aod550", "~")])
def test_ecmwf_grib1_surface_identity(tmp_path, param, short, units):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({"paramId": param}, plane())])
    result = reader.read_regular_grib([path], {"field": contract(param, short, units)})
    np.testing.assert_allclose(result["fields"]["field"][0], plane().reshape(2, 3))


def test_ascending_latitude_preserved(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({"latitudeOfFirstGridPointInDegrees": 30,
                       "latitudeOfLastGridPointInDegrees": 31,
                       "jScansPositively": 1}, plane())])
    result = reader.read_regular_grib([path], {"t": contract()})
    np.testing.assert_array_equal(result["y"], [30, 31])


def test_dense_union_cap(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane()), ({"paramId": 168, "dataTime": 300}, plane())])
    with pytest.raises(ValueError, match="dense_cell_limit"):
        reader.read_regular_grib([path], {"t": contract(), "d": contract(168, "2d")}, max_cells=12)


def test_identical_duplicates_require_explicit_policy(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane())])
    encoded = path.read_bytes()
    path.write_bytes(encoded * 3)
    for kwargs in ({}, {"duplicate_policy": "error"}):
        with pytest.raises(ValueError, match="grib_grid_duplicate_variable_time"):
            reader.read_regular_grib([path], {"t": contract()}, **kwargs)
    result = reader.read_regular_grib([path], {"t": contract()},
                                     duplicate_policy="identical", max_cells=6)
    np.testing.assert_array_equal(result["fields"]["t"][0], plane().reshape(2, 3))
    metadata = result["metadata"]
    assert metadata["duplicate_policy"] == "identical"
    assert metadata["skipped_duplicate_count"] == 2
    assert metadata["message_count"] == 3
    assert metadata["field_message_counts"] == {"t": 1}
    assert metadata["decoded_message_count"] == 1
    assert metadata["absent_time_counts"] == {"t": 0}
    assert metadata["missing_value_counts"] == {"t": 0}


@pytest.mark.parametrize("overrides,values", [({}, plane(1)),
    ({"generatingProcessIdentifier": 42}, plane()),
    ({"bitsPerValue": 16}, plane())])
def test_identical_policy_rejects_encoded_conflicts(tmp_path, overrides, values):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane()), (overrides, values)])
    with pytest.raises(ValueError, match="grib_grid_duplicate_message_conflict"):
        reader.read_regular_grib([path], {"t": contract()}, duplicate_policy="identical")


@pytest.mark.parametrize("conflict", [False, True])
def test_unselected_duplicate_messages_checked(tmp_path, conflict):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane()), ({"paramId": 168}, plane()),
                      ({"paramId": 168}, plane(int(conflict)))])
    kwargs = dict(requested_fields=["t"], duplicate_policy="identical")
    contracts = {"t": contract(), "d": contract(168, "2d")}
    if conflict:
        with pytest.raises(ValueError, match="grib_grid_duplicate_message_conflict"):
            reader.read_regular_grib([path], contracts, **kwargs)
    else:
        result = reader.read_regular_grib([path], contracts, **kwargs)
        assert result["metadata"]["skipped_duplicate_count"] == 1
        assert result["metadata"]["field_message_counts"] == {"t": 1, "d": 1}
        assert result["metadata"]["decoded_message_count"] == 1


def test_identical_duplicates_count_towards_message_limit(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane())])
    path.write_bytes(path.read_bytes() * 2)
    with pytest.raises(ValueError, match="grib_grid_message_limit"):
        reader.read_regular_grib([path], {"t": contract()},
                                 duplicate_policy="identical", max_messages=1)


def test_duplicate_policy_contract(tmp_path):
    path = tmp_path / "synthetic.grib"
    write_grib(path, [({}, plane())])
    with pytest.raises(ValueError, match="grib_grid_invalid_duplicate_policy"):
        reader.read_regular_grib([path], {"t": contract()}, duplicate_policy="last")
    result = reader.read_regular_grib([path], {"t": contract()})
    assert result["metadata"]["duplicate_policy"] == "error"
    assert result["metadata"]["skipped_duplicate_count"] == 0
