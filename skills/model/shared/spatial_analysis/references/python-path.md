# Python path: vector, bilinear and daily-grid helpers

**English** | [中文](python-path_ZH.md)

The [Python helpers](../scripts/python/spatial_helpers.py) implement the same bounded matching/CRS/map operations as the R route. Use the [common configuration and result contract](operations.md). Required packages are GeoPandas, pandas, NumPy, Shapely, pyproj 3.5+ and Matplotlib; Rasterio/geopy are not required by these helpers.

A separate sandbox dependency environment was used for the synthetic check; optional spatial packages were not installed into the main project environment. Invoke the interpreter from an environment that actually contains them. No automatic installer, file loader or configuration loader is supplied.

In the chosen dedicated Python environment, an explicit minimal setup is:

```sh
python -m pip install geopandas matplotlib "pyproj>=3.5"
```

Record the installed versions; this command is not a lockfile or an implicit task action.

## Check the path

From repository root:

```sh
python skills/model/shared/spatial_analysis/examples/python/synthetic_spatial.py
```

This runs only synthetic data and builds four figures with a headless backend; it exports only when an explicit fresh directory is supplied. Source helper imports have no data reads or network calls. Coordinate transformation requires PROJ networking to be disabled, so unavailable transformation grids fail rather than trigger downloads.

## Use prepared objects

With authorized GeoDataFrames `sites` and `areas` and reviewed `working_crs` / `shared_limits`:

```python
import importlib.util
from pathlib import Path
from pyproj import network

path = Path("skills/model/shared/spatial_analysis/scripts/python/spatial_helpers.py")
spec = importlib.util.spec_from_file_location("spatial_helpers", path)
spatial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spatial)
network.set_network_enabled(False)
sites_work = spatial.transform_gdf(sites, working_crs)
areas_work = spatial.transform_gdf(areas, working_crs)
matched = spatial.point_polygon_matches(
    sites_work, areas_work, "sample_id", "area_id", predicate="intersects"
)
fig, ax = spatial.plot_polygons(
    areas_work, "value", "Study value (declared unit)", limits=shared_limits
)
```

The helper applies a strict pyproj transformation with longitude/latitude `always_xy=True`, no ballpark fallback and checked output geometry. Replacing CRS metadata occurs only after transforming coordinates. Missing source CRS, invalid geometry or an enabled PROJ network setting stops that operation.

## Functions and output

| Operation | Python function | R counterpart |
|---|---|---|
| Coordinate conversion | `transform_gdf` | `transform_sf` |
| Projected point/polygon match | `point_polygon_matches` | `point_polygon_matches` |
| Polygon map | `plot_polygons` | `sf_polygon_plot` |
| Point map | `plot_points` | `sf_point_plot` |
| Projected rectangular grid | `grid_plot` | `grid_plot` |
| Faceted rectangular grid | `grid_facet_plot` | `grid_facet_plot` |

Match outputs retain all candidates in polygon source order. Inputs are copied, not relabelled or modified in place. Grid width/height use the declared projected CRS units. Shared colour limits are checked against values, not used to silently censor them. Plot calls return figure/axes; R returns a ggplot object. Point marker-size conventions and palette implementations differ; geometric/QA equivalence does not imply pixel identity.

For an authorized new external `target_plot`, explicitly choose physical dimensions:

```python
if target_plot.exists():
    raise ValueError("fresh_output_required")
fig.set_size_inches(14 / 2.54, 10 / 2.54)
fig.savefig(target_plot, dpi=300)
```

Verify the external project boundary before exporting; this direct call does not inherit runner path checks. Persist candidate lists as JSON arrays, and retain source/CRS/QA identities. Nearest matching, general raster conservation and online geocoding remain library-guided adaptations, not functions secretly supplied by this module.

## Pure bilinear and local-day functions

[Bilinear helpers](../scripts/python/bilinear_helpers.py) and [daily-grid helpers](../scripts/python/grid_daily.py) require only NumPy and pandas; they do not require the vector/map dependencies above. Select an existing environment containing them and record versions. The following standalone example runs from repository root, uses only synthetic arrays and performs no data/configuration reads or exports. `importlib` loads source modules by explicit repository paths; no package installation is implied.

```python
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

def load_helper(name, filename):
    path = Path("skills/model/shared/spatial_analysis/scripts/python") / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bilinear = load_helper("bilinear_helpers", "bilinear_helpers.py")
daily_grid = load_helper("grid_daily", "grid_daily.py")
x = np.array([100., 102., 104.])
y = np.array([24., 22., 20.])  # original descending latitude order
points = np.array([[101., 21.], [104., 24.]])
weights = bilinear.bilinear_weights(
    x, y, points, ["site_a", "site_b"], "EPSG:4326", "EPSG:4326"
)
field = 2*x[None, :] + 3*y[:, None] + 7
sampled = bilinear.sample_bilinear(field, weights)
assert np.allclose(sampled["value"], [272., 287.])
assert sampled["status"].tolist() == ["ok", "ok"]
assert np.allclose(weights["source_y"], y[weights["row_index"].to_numpy()-1])

# Eight 3-hourly samples belonging to 2024-01-01 in Asia/Shanghai.
times = pd.date_range("2023-12-31T18:00:00Z", periods=8, freq="3h")
cube = np.broadcast_to(field, (8, *field.shape)).copy()
daily = daily_grid.daily_grid_mean(
    cube, times, ["2024-01-01", "2024-01-02"],
    timezone="Asia/Shanghai", sample_interval_hours=3,
)
assert daily["expected_samples_per_day"] == 8
assert daily["source_sample_count"] == [8, 0]
assert np.all(daily["finite_sample_count"][0] == 8)
assert np.allclose(daily["values"][0], field)
assert np.isnan(daily["values"][1]).all()  # absent date retained
assert daily["outside_expected_period_samples"] == 0
```

Both bilinear languages follow the [same operational contract](operations.md#bilinear-and-daily-grid-calls): explicit verified `EPSG:4326`, regional regular axes in one longitude convention, no wrapping or extrapolation, four rows per point and **one-based original-axis indices**. `sample_bilinear` consumes those indices directly and returns `point_id,value,status`; positive-weight NaN/Inf support yields `missing_support` without redistributing weights. Zero-weight missing nodes are ignored. Check IDs, four-neighbor weights, statuses and original source coordinates. Scientific choice of support is covered by the [method](../../../../../methods/shared/spatial_analysis.md).

`daily_grid_mean` returns the dictionary documented in [operations](operations.md#bilinear-and-daily-grid-calls). For hourly input, pass `sample_interval_hours=1` and all 24 UTC samples belonging to each local day. For three-hourly input, pass `3` and all eight phase-aligned samples; this is an eight-sample mean. Any absent/nonfinite sample makes that day/cell unavailable. All requested dates remain present, including entirely missing days. Review `source_sample_count`, `finite_sample_count` and outside-period counts rather than treating a returned date as evidence of complete input. This helper preserves instantaneous-value units and does not process accumulations or read weather files.

## Further library recipes

Use [GeoPandas nearest joins](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html) with a suitable measurement CRS, declared maximum distance and retained ties. Use [Rasterio](https://rasterio.readthedocs.io/en/stable/topics/reproject.html) only after declaring quantity meaning and complete target geometry. Service access follows [geocoding guidance](geocoding.md), separate from geometry processing.
