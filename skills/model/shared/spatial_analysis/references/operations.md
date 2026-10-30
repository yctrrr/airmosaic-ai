# Configuration, calls and checks

**English** | [中文](operations_ZH.md)

Read the [method](../../../../../methods/shared/spatial_analysis.md) first. The [configuration example](../examples/task.example.json) documents fields for an agent/task author; it is not a loader, a run-tool parameter file or an approved task.

## Dependencies and configuration

R direct functions need sf and ggplot2 (including their GEOS/GDAL/PROJ and tidy-evaluation dependencies). Raster adaptation additionally needs terra; Python helpers use GeoPandas, Shapely and pyproj, with Matplotlib for maps and Rasterio for rasters. geopy/tidygeocoder are optional provider clients, not core dependencies. Record actual versions; no package installation is automatic.

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

Retain language/library/engine versions, source and result identities, matching counts, units, boundary version, CRS transform settings, missingness and task-relevant coverage/totals with QA. A missing distance/conservation check is unperformed, not zero error. The module supplies no automatic path loader, file export, raster resampler, geocoder, run-tool or MCP adapter.

The dated [synthetic check receipt](../examples/checks.json) records actual dependency versions, tested cases and source hashes. It documents one checked environment, not a universal version lock or scientific acceptance.

## Improvements informed by related skills

The [GeoMaster skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/geomaster/SKILL.md) provides a useful language/tool matrix and routes between vector, raster and other tasks. AirMosaic uses a narrower task contract and two implemented language paths. Its examples are reference material, not a scientific guarantee; missing values here remain missing rather than being changed to zero.

The local R expertise and scientific-visualization skills informed explicit function inputs, unit-labelled figures, consistent comparison scales and physical export dimensions. Only relevant patterns are adopted, with no dependence on those personal skill folders. No third-party skill was installed or copied wholesale. Actual spatial API behavior is checked against the primary library documentation and synthetic tests, not repository popularity.
