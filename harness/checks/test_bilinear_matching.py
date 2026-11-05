"""Synthetic interpolation identities and deliberate refusal cases."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("bilinear_helpers", ROOT /
    "skills/model/shared/spatial_analysis/scripts/python/bilinear_helpers.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def weights(x=(100, 101, 102), y=(30, 31, 32), points=((100.25, 30.75),), ids=("A",)):
    return MODULE.bilinear_weights(x, y, points, ids, "EPSG:4326", "EPSG:4326")


@pytest.mark.parametrize("reverse_x,reverse_y", [(False, False), (True, False), (False, True), (True, True)])
def test_affine_plane_and_original_axis_indices(reverse_x, reverse_y):
    x = np.array([100, 101, 102])[::(-1 if reverse_x else 1)]
    y = np.array([30, 31, 32])[::(-1 if reverse_y else 1)]
    field = 2*x[None, :] + 3*y[:, None] + 7
    result = MODULE.sample_bilinear(field, weights(x, y)).iloc[0]
    assert result["value"] == pytest.approx(2*100.25+3*30.75+7)
    assert result["status"] == "ok"


def test_corners_and_zero_weight_missing_support():
    field = np.array([[5, np.nan], [np.nan, np.nan]])
    w = weights((100, 101), (30, 31), ((100, 30),))
    assert MODULE.sample_bilinear(field, w).iloc[0]["value"] == 5
    assert MODULE.sample_bilinear(np.array([[1, 2], [3, 4]]),
        weights((100, 101), (30, 31), ((101, 31),))).iloc[0]["value"] == 4


@pytest.mark.parametrize("missing", [np.nan, np.inf, -np.inf])
def test_positive_weight_missing_support_is_not_reweighted(missing):
    field = np.array([[1, 2], [3, missing]])
    result = MODULE.sample_bilinear(field,
        weights((100, 101), (30, 31), ((100.5, 30.5),))).iloc[0]
    assert pd.isna(result["value"]) and result["status"] == "missing_support"


def test_masked_support_is_missing_in_scalar_and_series():
    field = np.ma.array([[1, 2], [3, 9999]], mask=[[False, False], [False, True]])
    w = weights((100, 101), (30, 31), ((100.5, 30.5), (100, 30)), ("center", "corner"))
    scalar = MODULE.sample_bilinear(field, w)
    assert scalar["status"].tolist() == ["missing_support", "ok"]
    assert pd.isna(scalar.iloc[0]["value"]) and scalar.iloc[1]["value"] == 1
    series = MODULE.sample_bilinear_series(np.ma.stack([field, field]), w)
    np.testing.assert_allclose(series["values"], [[np.nan, 1], [np.nan, 1]], equal_nan=True)
    assert series["status"].tolist() == [["missing_support", "ok"], ["missing_support", "ok"]]
    assert field.mask[1, 1] and field.data[1, 1] == 9999


@pytest.mark.parametrize("x,y,point", [
    ([100, 101, 103], [30, 31], [100.5, 30.5]),
    ([100, 100], [30, 31], [100, 30.5]),
    ([100, 101], [30, 31], [99.9, 30.5]),
    ([179, -179], [30, 31], [179, 30.5]),
    ([0, 200], [30, 31], [100, 30.5]),
    ([100, 101], [90, 91], [100.5, 90]),
])
def test_bad_axes_and_extrapolation_are_rejected(x, y, point):
    with pytest.raises(ValueError):
        weights(x, y, (point,))


def test_explicit_0_to_360_regional_convention():
    w = weights((170, 190), (30, 31), ((180, 30.5),))
    assert MODULE.sample_bilinear(np.array([[1, 3], [5, 7]]), w).iloc[0]["value"] == 4


def test_crs_and_station_identity_are_required():
    with pytest.raises(ValueError, match="verified_epsg4326"):
        MODULE.bilinear_weights([100, 101], [30, 31], [[100.5, 30.5]], ["A"], None, "EPSG:4326")
    with pytest.raises(ValueError, match="point_ids"):
        weights(points=((100.5, 30.5), (100.6, 30.6)), ids=("A", "A"))


@pytest.mark.parametrize("change", ["sum", "negative", "index", "neighbor", "duplicate"])
def test_modified_weight_tables_are_rejected(change):
    w = weights()
    if change == "sum": w.loc[0, "weight"] += .01
    elif change == "negative": w.loc[0, "weight"] = -.1
    elif change == "index": w.loc[0, "row_index"] = 0
    elif change == "neighbor": w.loc[0, "neighbor"] = "unknown"
    else: w.loc[1, ["row_index", "col_index"]] = w.loc[0, ["row_index", "col_index"]].values
    with pytest.raises(ValueError, match="invalid_weights"):
        MODULE.sample_bilinear(np.ones((3, 3)), w)
def test_explicit_unverified_alignment_and_series():
    import importlib.util
    from pathlib import Path
    import numpy as np
    path = Path(__file__).resolve().parents[2] / 'skills/model/shared/spatial_analysis/scripts/python/bilinear_helpers.py'
    spec = importlib.util.spec_from_file_location('series', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    x=np.array([100.,101.,102.]); y=np.array([32.,31.,30.])
    result=module.bilinear_weights_under_alignment_assumption(x,y,[[100.5,31.5],[101,31]],['a','b'],
        assumption='angular_lon_lat_aligned_without_verified_datum')
    assert result['coordinate_metadata_verified'] is False
    field=np.arange(18,dtype=float).reshape(2,3,3);field[1,0,0]=np.nan
    series=module.sample_bilinear_series(field,result['weights'])
    for t in range(2):
        expected=module.sample_bilinear(field[t],result['weights'])
        np.testing.assert_allclose(series['values'][t],expected.value,equal_nan=True)
        assert series['status'][t].tolist()==expected.status.tolist()
