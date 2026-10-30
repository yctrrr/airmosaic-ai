# Python path: GeoPandas and pyproj

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

Verify the external project boundary before exporting; this direct call does not inherit runner path checks. Persist candidate lists as JSON arrays, and retain source/CRS/QA identities. Nearest matching, raster conservation and online geocoding remain library-guided adaptations, not functions secretly supplied by this module.

## Further library recipes

Use [GeoPandas nearest joins](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html) with a suitable measurement CRS, declared maximum distance and retained ties. Use [Rasterio](https://rasterio.readthedocs.io/en/stable/topics/reproject.html) only after declaring quantity meaning and complete target geometry. Service access follows [geocoding guidance](geocoding.md), separate from geometry processing.
