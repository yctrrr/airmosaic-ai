"""In-memory spatial helpers; no data readers, exports, geocoders or credential loading."""
from __future__ import annotations

from functools import partial
import math


def _geo(data, types=None):
    import geopandas as gpd
    if not isinstance(data, gpd.GeoDataFrame) or data.empty or data.crs is None:
        raise ValueError("spatial_object_or_crs_missing")
    if data.geometry.isna().any() or data.geometry.is_empty.any() or not data.geometry.is_valid.all():
        raise ValueError("spatial_geometry_requires_review")
    if types is not None and not data.geometry.geom_type.isin(types).all():
        raise ValueError("spatial_geometry_type_mismatch")


def _field(data, field, numeric=False):
    import numpy as np
    import pandas as pd
    if not isinstance(field, str) or field not in data.columns or not data.columns.is_unique:
        raise ValueError("spatial_field_missing")
    if numeric:
        values = data[field]
        if (not pd.api.types.is_numeric_dtype(values) or pd.api.types.is_bool_dtype(values)
                or not np.isfinite(values.dropna().to_numpy(dtype=float)).all()):
            raise ValueError("spatial_numeric_field_invalid")


def _limits(data, value, value_label, limits):
    import numpy as np
    _field(data, value, numeric=True)
    if not isinstance(value_label, str) or not value_label.strip():
        raise ValueError("spatial_value_label_required")
    if limits is not None:
        values = np.asarray(limits, dtype=float)
        if values.shape != (2,) or not np.isfinite(values).all() or values[0] >= values[1]:
            raise ValueError("spatial_colour_limits_invalid")
        observed = data[value].dropna()
        if ((observed < values[0]) | (observed > values[1])).any():
            raise ValueError("spatial_values_outside_declared_limits")
        return tuple(values)
    return None


def transform_gdf(data, target_crs):
    """Apply a strict xy transformation; require offline PROJ to avoid implicit grid downloads."""
    from pyproj import CRS, Transformer, network
    from shapely.ops import transform
    _geo(data)
    if network.is_network_enabled():
        raise ValueError("spatial_transform_requires_offline_proj")
    target = CRS.from_user_input(target_crs)
    transformer = Transformer.from_crs(data.crs, target, always_xy=True,
                                       allow_ballpark=False, only_best=True)
    converted = data.geometry.map(partial(transform, partial(transformer.transform, errcheck=True)))
    answer = data.copy()
    answer.geometry = converted
    # CRS metadata is replaced only after coordinates have actually been transformed.
    answer = answer.set_crs(target, allow_override=True)
    _geo(answer)
    return answer


def point_polygon_matches(points, polygons, point_id, polygon_id, predicate="intersects"):
    """Return one record per point; retain all ambiguous candidates in source order."""
    import geopandas as gpd
    import pandas as pd
    _geo(points, {"Point"})
    _geo(polygons, {"Polygon", "MultiPolygon"})
    _field(points, point_id)
    _field(polygons, polygon_id)
    for values in (points[point_id], polygons[polygon_id]):
        if values.isna().any() or values.astype(str).str.strip().eq("").any() or values.astype(str).duplicated().any():
            raise ValueError("spatial_keys_invalid")
    if points.crs != polygons.crs:
        raise ValueError("spatial_crs_mismatch")
    if points.crs.is_geographic:
        raise ValueError("spatial_match_requires_reviewed_projected_crs")
    if predicate not in {"intersects", "within"}:
        raise ValueError("spatial_predicate_unsupported")
    left = gpd.GeoDataFrame({"sample_id": points[point_id].astype(str).to_numpy()},
                            geometry=list(points.geometry), crs=points.crs)
    right = gpd.GeoDataFrame({"matched_id": polygons[polygon_id].astype(str).to_numpy()},
                             geometry=list(polygons.geometry), crs=polygons.crs)
    joined = gpd.sjoin(left, right, how="left", predicate=predicate)
    order = {key: i for i, key in enumerate(right.matched_id)}
    groups = joined.groupby("sample_id", sort=False)["matched_id"].agg(
        lambda values: sorted(values.dropna().tolist(), key=order.__getitem__))
    rows = []
    for key in left.sample_id:
        candidates = groups.loc[key]
        count = len(candidates)
        rows.append({"sample_id": key, "matched_id": candidates[0] if count == 1 else None,
                     "n_matches": count,
                     "match_status": "unmatched" if count == 0 else "matched" if count == 1 else "ambiguous",
                     "candidate_ids": candidates})
    return pd.DataFrame(rows)


def _vector_plot(data, value, value_label, types, limits, cmap, **kwargs):
    import matplotlib.pyplot as plt
    _geo(data, types)
    bounds = _limits(data, value, value_label, limits)
    fig, ax = plt.subplots(figsize=(6, 4))
    data.plot(column=value, cmap=cmap, legend=True,
              legend_kwds={"label": value_label}, missing_kwds={"color": "lightgrey"},
              vmin=None if bounds is None else bounds[0],
              vmax=None if bounds is None else bounds[1], ax=ax, **kwargs)
    return fig, ax


def plot_polygons(data, value, value_label, limits=None, cmap="YlOrRd"):
    return _vector_plot(data, value, value_label, {"Polygon", "MultiPolygon"},
                        limits, cmap, edgecolor="none")


def plot_points(data, value, value_label, limits=None, cmap="YlOrRd",
                markersize=30, alpha=0.5):
    if not math.isfinite(markersize) or markersize <= 0 or not math.isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError("spatial_point_style_invalid")
    return _vector_plot(data, value, value_label, {"Point", "MultiPoint"}, limits, cmap,
                        markersize=markersize, alpha=alpha, edgecolor="white")


def _grid(data, x, y, value, value_label, crs, cell_width, cell_height, limits, facet=None):
    import numpy as np
    from pyproj import CRS
    if data.empty:
        raise ValueError("spatial_grid_empty")
    _field(data, x, numeric=True)
    _field(data, y, numeric=True)
    _field(data, value, numeric=True)
    if data[[x, y]].isna().any().any():
        raise ValueError("spatial_grid_coordinates_missing")
    target = CRS.from_user_input(crs)
    dimensions = np.asarray([cell_width, cell_height], dtype=float)
    if (not target.is_projected or not np.isfinite(dimensions).all()
            or not (dimensions > 0).all()):
        raise ValueError("spatial_grid_crs_or_dimensions_invalid")
    keys = [x, y]
    if facet is not None:
        _field(data, facet)
        keys.append(facet)
    if data.duplicated(keys).any():
        raise ValueError("spatial_grid_duplicate_cells")
    bounds = _limits(data, value, value_label, limits)
    if bounds is None:
        finite = data[value].dropna()
        if finite.empty:
            raise ValueError("spatial_colour_limits_required_for_missing_only_data")
        low, high = float(finite.min()), float(finite.max())
        bounds = (low, high if high > low else low + 1.0)
    return bounds, target


def _rectangles(ax, data, x, y, value, width, height, norm, cmap):
    import numpy as np
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Rectangle
    patches = [Rectangle((a - width / 2, b - height / 2), width, height)
               for a, b in zip(data[x], data[y])]
    collection = PatchCollection(patches, cmap=cmap, norm=norm, edgecolor="none")
    collection.set_array(np.ma.masked_invalid(data[value].to_numpy(dtype=float)))
    ax.add_collection(collection)
    ax.autoscale_view()
    ax.set_aspect("equal")
    return collection


def _projected_axes(ax, crs, x, y):
    from matplotlib.ticker import MaxNLocator
    unit = crs.axis_info[0].unit_name
    ax.set_xlabel(f"{x} ({unit})")
    ax.set_ylabel(f"{y} ({unit})")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=2))
    ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0), useOffset=True)


def grid_plot(data, x, y, value, value_label, crs, cell_width, cell_height,
              limits=None, cmap="YlOrRd"):
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    bounds, target = _grid(data, x, y, value, value_label, crs, cell_width, cell_height, limits)
    fig, ax = plt.subplots(figsize=(6, 4))
    colourmap = plt.get_cmap(cmap).copy()
    colourmap.set_bad("lightgrey")
    collection = _rectangles(ax, data, x, y, value, cell_width, cell_height,
                             Normalize(*bounds), colourmap)
    _projected_axes(ax, target, x, y)
    fig.colorbar(collection, ax=ax, label=value_label)
    return fig, ax


def grid_facet_plot(data, x, y, value, value_label, crs, cell_width, cell_height,
                    facet, facet_rows=1, limits=None, cmap="YlOrRd"):
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    bounds, target = _grid(data, x, y, value, value_label, crs, cell_width, cell_height, limits, facet)
    if isinstance(facet_rows, bool) or not isinstance(facet_rows, int) or facet_rows < 1:
        raise ValueError("spatial_facet_rows_invalid")
    groups = list(data.groupby(facet, sort=False, dropna=False, observed=True))
    columns = math.ceil(len(groups) / facet_rows)
    fig, axes = plt.subplots(facet_rows, columns, figsize=(6 * columns, 4 * facet_rows),
                              squeeze=False, sharex=True, sharey=True, layout="constrained")
    colourmap = plt.get_cmap(cmap).copy()
    colourmap.set_bad("lightgrey")
    active = []
    for ax, (label, group) in zip(axes.flat, groups):
        collection = _rectangles(ax, group, x, y, value, cell_width, cell_height,
                                  Normalize(*bounds), colourmap)
        ax.set_title(str(label))
        _projected_axes(ax, target, x, y)
        active.append(ax)
    for ax in list(axes.flat)[len(groups):]:
        ax.set_visible(False)
    fig.colorbar(collection, ax=active, label=value_label)
    return fig, axes
