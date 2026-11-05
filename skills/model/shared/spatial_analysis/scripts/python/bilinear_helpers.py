"""Auditable bilinear sampling of a regional, nonperiodic lon/lat grid.

Functions only: no readers, downloads, CRS inference or exports. Both language
paths expose one-based indices into the original latitude/longitude order.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


COLUMNS = ["point_id", "neighbor", "row_index", "col_index", "source_x", "source_y", "weight"]
NEIGHBORS = ("sw", "se", "nw", "ne")


def _axis(values, longitude):
    axis = np.asarray(values)
    if (axis.ndim != 1 or len(axis) < 2 or axis.dtype.kind not in "fiu"
            or not np.isfinite(axis).all()):
        raise ValueError("bilinear_invalid_axis")
    axis = axis.astype(float)
    delta = np.diff(axis)
    if not ((delta > 0).all() or (delta < 0).all()):
        raise ValueError("bilinear_axis_not_monotonic")
    if not np.allclose(delta, delta[0], rtol=1e-10, atol=1e-12):
        raise ValueError("bilinear_requires_regular_grid")
    if longitude:
        convention = ((axis >= -180).all() and (axis <= 180).all()
                      or (axis >= 0).all() and (axis <= 360).all())
        if not convention or np.ptp(axis) > 180:
            raise ValueError("bilinear_requires_nonperiodic_regional_longitudes")
    elif (np.abs(axis) > 90).any():
        raise ValueError("bilinear_invalid_latitude")
    order = np.argsort(axis)
    return axis, axis[order], order


def bilinear_weights(x, y, points, point_ids, source_crs, point_crs):
    """Return four neighbors per point; reject unknown CRS and extrapolation.

    ``x`` and ``y`` are cell-centre longitude/latitude axes. ``points`` is n×2
    in the same longitude convention. The caller must establish the CRS; these
    functions do not assign a CRS to unverified station coordinates.
    """
    if source_crs != "EPSG:4326" or point_crs != "EPSG:4326":
        raise ValueError("bilinear_requires_verified_epsg4326")
    return _weights_on_regular_axes(x, y, points, point_ids)


def bilinear_weights_under_alignment_assumption(x, y, points, point_ids, *, assumption):
    """Explicit engineering-only angular alignment; does not verify any datum.

    Keep this declaration with outputs. The verified-CRS entry above retains
    its original contract. This path supplies no coordinate transformation.
    """
    if assumption != "angular_lon_lat_aligned_without_verified_datum":
        raise ValueError("bilinear_explicit_alignment_assumption_required")
    return {"weights": _weights_on_regular_axes(x, y, points, point_ids),
            "coordinate_metadata_verified": False, "alignment_assumption": assumption}


def _weights_on_regular_axes(x, y, points, point_ids):
    _, xs, xi = _axis(x, True)
    _, ys, yi = _axis(y, False)
    locations = np.asarray(points)
    if (locations.ndim != 2 or locations.shape[1] != 2 or not len(locations)
            or locations.dtype.kind not in "fiu" or not np.isfinite(locations).all()):
        raise ValueError("bilinear_invalid_points")
    ids = list(point_ids)
    if (len(ids) != len(locations) or any(not isinstance(v, str) or not v.strip() for v in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError("bilinear_invalid_point_ids")
    if ((locations[:, 0] < xs[0]).any() or (locations[:, 0] > xs[-1]).any()
            or (locations[:, 1] < ys[0]).any() or (locations[:, 1] > ys[-1]).any()):
        raise ValueError("bilinear_extrapolation_not_allowed")
    columns = np.clip(np.searchsorted(xs, locations[:, 0], side="right") - 1, 0, len(xs)-2)
    rows = np.clip(np.searchsorted(ys, locations[:, 1], side="right") - 1, 0, len(ys)-2)
    fx = (locations[:, 0]-xs[columns])/(xs[columns+1]-xs[columns])
    fy = (locations[:, 1]-ys[rows])/(ys[rows+1]-ys[rows])
    answer = []
    for i, point_id in enumerate(ids):
        weights = ((1-fx[i])*(1-fy[i]), fx[i]*(1-fy[i]),
                   (1-fx[i])*fy[i], fx[i]*fy[i])
        for name, dx, dy, weight in zip(NEIGHBORS, (0, 1, 0, 1), (0, 0, 1, 1), weights):
            col, row = columns[i]+dx, rows[i]+dy
            answer.append((point_id, name, int(yi[row])+1, int(xi[col])+1,
                           float(xs[col]), float(ys[row]), float(weight)))
    return pd.DataFrame(answer, columns=COLUMNS)


def sample_bilinear(values, weights):
    """Sample one [latitude, longitude] field without filling masked support.

    A missing/invalid positive-weight source node produces ``missing_support``.
    Zero-weight missing nodes do not affect an exact-node/edge evaluation.
    No renormalization, nearest-neighbor fallback or extrapolation is applied.
    """
    field = np.asarray(values)
    if field.ndim != 2 or min(field.shape) < 2 or field.dtype.kind not in "fiu":
        raise ValueError("bilinear_invalid_field")
    if np.ma.isMaskedArray(values):
        field = np.ma.asarray(values, dtype=float).filled(np.nan)
    if (not isinstance(weights, pd.DataFrame) or weights.empty
            or not weights.columns.is_unique or set(weights.columns) != set(COLUMNS)):
        raise ValueError("bilinear_invalid_weights")
    if (weights["point_id"].map(lambda v: not isinstance(v, str) or not v.strip()).any()
            or weights["neighbor"].isna().any()):
        raise ValueError("bilinear_invalid_weights")
    numeric = weights[["row_index", "col_index", "source_x", "source_y", "weight"]]
    if any(c.dtype.kind not in "fiu" for _, c in numeric.items()):
        raise ValueError("bilinear_invalid_weights")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("bilinear_invalid_weights")
    row, col = weights["row_index"].to_numpy(), weights["col_index"].to_numpy()
    if (np.any(row != np.floor(row)) or np.any(col != np.floor(col))
            or np.any(row < 1) or np.any(col < 1)
            or np.any(row > field.shape[0]) or np.any(col > field.shape[1])
            or (weights["weight"] < 0).any() or (weights["weight"] > 1).any()):
        raise ValueError("bilinear_invalid_weights")
    answer = []
    for point_id, group in weights.groupby("point_id", sort=False):
        if (len(group) != 4 or set(group["neighbor"]) != set(NEIGHBORS)
                or group[["row_index", "col_index"]].duplicated().any()
                or not np.isclose(group["weight"].sum(), 1, rtol=0, atol=1e-12)):
            raise ValueError("bilinear_invalid_weights")
        positive = group[group["weight"] > 0]
        support = field[positive["row_index"].to_numpy(dtype=int)-1,
                        positive["col_index"].to_numpy(dtype=int)-1]
        valid = np.isfinite(support).all()
        value = float(np.dot(support, positive["weight"])) if valid else np.nan
        answer.append((point_id, value, "ok" if valid else "missing_support"))
    return pd.DataFrame(answer, columns=["point_id", "value", "status"])


def sample_bilinear_series(values, weights):
    """Vectorized [time,y,x] sampling with the same strict missing-support rule."""
    field = np.asarray(values)
    if field.ndim != 3 or not len(field) or field.dtype.kind not in "fiu":
        raise ValueError("bilinear_invalid_series")
    if np.ma.isMaskedArray(values):
        field = np.ma.asarray(values, dtype=float).filled(np.nan)
    # Reuse every existing table/index/weight validation before vectorization.
    reference = sample_bilinear(np.zeros(field.shape[1:]), weights)
    groups = [group for _, group in weights.groupby("point_id", sort=False)]
    rows = np.asarray([g["row_index"].to_numpy(dtype=int)-1 for g in groups])
    cols = np.asarray([g["col_index"].to_numpy(dtype=int)-1 for g in groups])
    coefficients = np.asarray([g["weight"].to_numpy(dtype=float) for g in groups])
    support = field[:, rows, cols]
    positive = coefficients > 0
    valid = np.all(np.isfinite(support) | ~positive[None, :, :], axis=2)
    result = np.sum(np.where(positive[None, :, :], support, 0) * coefficients, axis=2)
    result[~valid] = np.nan
    return {"point_ids": reference["point_id"].tolist(), "values": result,
            "status": np.where(valid, "ok", "missing_support")}
