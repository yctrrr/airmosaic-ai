# Configuration, calls and checks

**English** | [中文](operations_ZH.md)

Read the [method](../../../../../methods/shared/spatial_analysis.md) first. The [configuration example](../examples/task.example.json) documents fields for an agent/task author; it is not a loader, a run-tool parameter file or an approved task.

## Dependencies and configuration

R vector/map functions need sf and ggplot2 (including their GEOS/GDAL/PROJ and tidy-evaluation dependencies); `bilinear_helpers.R` needs only base R. Python `bilinear_helpers.py` and `grid_daily.py` need only NumPy and pandas; vector/map helpers use GeoPandas, Shapely and pyproj, with Matplotlib for maps. General raster adaptation additionally needs terra or Rasterio. geopy/tidygeocoder are optional provider clients, not core dependencies. Record actual versions; no package installation is automatic.

| Setting | Decide explicitly |
|---|---|
| Language | Set `language` to `r` or `python` after choosing an available environment; the example's null is unresolved |
| Input versions and IDs | Fixed data/boundary version; stable unique keys; authorized personal locations |
| Source/working/display CRS | Verified source datum and axis convention; appropriate calculation and display support |
| Relation and ambiguity | Containment/intersection/nearest; retained candidates and maximum distance where relevant |
| Raster quantity and target grid | Category/intensive/total; method, resolution, origin, extent and missing mask |
| Map | Value/unit, cell dimensions in CRS units, shared limits and export size/DPI |
| Geocoder | Disabled by default; deliberate provider/endpoint, privacy classification and current terms |
| Output | Fresh external project destination and input/configuration/QA identities |

Credentials are not configuration values. Provider-specific clients may read an explicitly authorized environment/secret mechanism at invocation; never serialize keys into the task JSON or public URLs.

## Choose a language path

| Path | Entry | Current verification |
|---|---|---|
| R | [R operations](r-path.md), `scripts/r/` and `examples/r/` | In-memory matching, transformation and four plot types checked with synthetic data |
| Python | [Python operations](python-path.md), `scripts/python/` and `examples/python/` | The corresponding operations checked in an isolated dependency environment |
| Geocoding | [Source/provider workflow](geocoding.md) | No live provider registered or tested |

Honor the user's language choice. Otherwise choose an available environment and suitable maintained library, recording the choice; never silently switch language after failure. Match source IDs, geometries, predicate/boundary rules, CRS/axis conventions, value units and QA between paths. Figures need not be pixel-identical: palette implementations and point-size units can differ, so supply the same explicit colours/limits when required.

## Result contract and reuse

Both matching routes return `sample_id`, `matched_id`, `n_matches`, `match_status` and `candidate_ids`. Preserve all candidates: use a JSON array or separate candidate table, not a truncated scalar or language-specific list string. Suggested vector interchange is GeoPackage or reviewed GeoParquet with CRS metadata; names and layout are task choices.

Retain language/library/engine versions, source and result identities, matching counts, units, boundary version, CRS transform settings, missingness and task-relevant coverage/totals with QA. A missing distance/conservation check is unperformed, not zero error. The modules supply no automatic data/configuration loader, file export, general raster reprojection/conservative remapping, geocoder, run-tool or MCP adapter. Existing tool IDs are unchanged.

## Bilinear and daily-grid calls

Use the runnable loading/call examples in the [Python path](python-path.md) and [R path](r-path.md). Scientific choices follow the [spatial method](../../../../../methods/shared/spatial_analysis.md); the operational contract is:

- `bilinear_weights(x, y, points, point_ids, source_crs, point_crs)` takes finite regular one-dimensional axes with at least two unique coordinates, strictly ascending or descending. Latitude is within `[-90,90]`; longitude lies entirely within `[-180,180]` or `[0,360]`, with span at most 180 degrees. This is a regional, nonperiodic grid: `170..190` is allowed in the latter convention, but no longitude wrapping is performed. Supply a nonempty finite n-by-2 longitude/latitude point array (R matrix), matching nonempty unique string IDs and both CRS arguments exactly `"EPSG:4326"`. Neither CRS inference nor coordinate transformation is performed. Points must share the grid's longitude convention; extrapolation is refused, while exact nodes and edges are allowed.
- Each point returns four rows with `point_id`, `neighbor` (`sw,se,nw,ne`), `row_index`, `col_index`, `source_x`, `source_y`, `weight`. Indices are **one-based in both languages**, referencing the original y/x order, including descending axes. Do not subtract one before passing this table to either sampling helper.
- `sample_bilinear(values, weights)` accepts a numeric `[y,x]` field and the complete table. It checks the exact column set, four unique neighbor labels and index pairs per point, finite valid integer indices, weights in `[0,1]` and sum equal to one within `1e-12`. It returns `point_id,value,status` in first-seen point order. Any NA/NaN/Inf at a positive-weight neighbor yields missing `value` and `status="missing_support"`; zero-weight missing values do not affect the result. Complete support yields `status="ok"`. Weights are never redistributed. Review weights, original-axis indexing, output IDs and status counts before reuse; these checks do not certify scientific applicability.
- Python `daily_grid_mean(values, times_utc, expected_dates, *, timezone, sample_interval_hours)` accepts a nonempty numeric `[time,y,x]` cube, unique increasing timezone-aware zero-offset UTC times, an explicit increasing unique `YYYY-MM-DD` date list, `timezone="Asia/Shanghai"` and interval `1` or `3` hours. Timestamps must be on whole hours and the UTC 00:00-based interval phase. It does not infer frequency or resample. Every requested day/cell needs all 24 hourly or 8 three-hourly finite samples; incomplete support stays NaN, with counts retained. Three-hourly output is the mean of eight samples. Units are preserved; accumulated variables require a different reviewed operation.
- Daily output is a dictionary with `dates`, `[day,y,x]` `values`, matching `finite_sample_count`, daily `source_sample_count`, `expected_samples_per_day`, `sample_interval_hours`, `timezone`, `outside_expected_period_samples` and `statistic`. Requested dates remain present even when every sample is absent. Inspect counts and outside-period samples explicitly; the latter are reported, not aggregated into requested days. No R daily-grid counterpart is supplied.

The dated [synthetic check receipt](../examples/checks.json) records actual dependency versions, tested cases and source hashes. It documents one checked environment, not a universal version lock or scientific acceptance.

## Improvements informed by related skills

The [GeoMaster skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/geomaster/SKILL.md) provides a useful language/tool matrix and routes between vector, raster and other tasks. AirMosaic uses a narrower task contract and two implemented language paths. Its examples are reference material, not a scientific guarantee; missing values here remain missing rather than being changed to zero.

The local R expertise and scientific-visualization skills informed explicit function inputs, unit-labelled figures, consistent comparison scales and physical export dimensions. Only relevant patterns are adopted, with no dependence on those personal skill folders. No third-party skill was installed or copied wholesale. Actual spatial API behavior is checked against the primary library documentation and synthetic tests, not repository popularity.
