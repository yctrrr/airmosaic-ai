# Spatial matching, coordinate systems and mapping

**English** | [中文](spatial_analysis_ZH.md)

Spatial analysis connects locations and supports, not just tables with coordinate columns. State the question, geometry, time/boundary version and acceptable location error before choosing operations. The [spatial skill](../../skills/model/shared/spatial_analysis/SKILL.md) supplies separate R and Python functions, calls and checks.

## Four task families

| Task | Decision before calculation | R tools | Python tools |
|---|---|---|---|
| Spatial matching | Identity join, containment, intersection, overlap or nearest? What cardinality, boundary and distance rules apply? | `sf::st_join`, `st_intersects`, `st_within`, `st_is_within_distance` | GeoPandas `sjoin` / `sjoin_nearest`, Shapely predicates |
| Coordinate conversion | Verified source datum/CRS, axis order, area of use and required accuracy | `sf::st_transform`; `terra::project` for rasters | GeoPandas `to_crs`; pyproj `Transformer`; Rasterio warp |
| Mapping | Variable meaning/unit, support, shared colour limits, projection and missingness | `ggplot2::geom_sf`, grid/facet helpers; optional ggspatial | GeoPandas/Matplotlib; reviewed interactive output |
| Geocoding | Address-to-location or reverse? Which source/provider, precision, privacy and permitted workload? | Local gazetteer; tidygeocoder for an explicitly selected service | Local gazetteer; geopy as a service client |

Geocoding does not prove administrative containment, and assigning a CRS does not transform coordinates. An attractive map does not validate matching or measurement.

## 1. Match spatial objects with explicit ambiguity

Prefer stable verified identifiers when they represent the same entities and boundary version. Otherwise choose a geometric relation. A point exactly on a shared polygon border can have zero strict `within` matches or multiple `intersects` matches. Retain `matched`, `unmatched` and `ambiguous` states; do not select the first result or automatically snap it to the nearest region.

Nearest matching needs a study-based maximum distance and tie rule. A nearest object always exists in a nonempty reference layer, even when scientifically implausible. Record distance, units, candidates, coverage and unmatched fraction. GeoPandas nearest joins can return multiple equidistant matches; its distances are planar and unreliable in a geographic CRS. See [sf predicates](https://r-spatial.github.io/sf/reference/geos_binary_pred.html) and [GeoPandas nearest joins](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html).

Check invalid/empty geometry, duplicate keys, many-to-many joins and boundary vintage before aggregation. Geometry repair can split objects or change area/type: preserve the source and inspect changes. For long/lat work, document the spherical/ellipsoidal engine; [sf's s2 guide](https://r-spatial.github.io/sf/articles/sf7.html) explains why planar assumptions cannot be transferred automatically.

## 2. Distinguish CRS assignment from transformation

`st_set_crs` / `set_crs` declare what existing numbers mean; `st_transform` / `to_crs` calculate new coordinates. Unknown source CRS needs source verification, not a guess based on numeric range. Retain the original coordinates and datum, including coordinate epoch where required.

Distance and area require a suitable local projected or geodesic/equal-area approach. “Projected” alone does not guarantee metre units or low distortion. Web map display coordinates are not a general measurement CRS. With pyproj, explicitly use `always_xy=True` when the contract is longitude/latitude, and inspect transformation availability/accuracy. Missing grids or unsupported operations are reasons to review the transformation rather than silently accept an approximation. See [sf transformation](https://r-spatial.github.io/sf/reference/st_transform.html), [GeoPandas CRS guidance](https://geopandas.org/en/stable/docs/user_guide/projections.html) and [pyproj Transformer](https://pyproj4.github.io/pyproj/stable/api/transformer.html).

Chinese web-map coordinate products need their own source/provider convention. Do not label GCJ-02 or BD-09 as WGS84 and expect an ordinary EPSG reprojection to correct them. Review a provider's documented coordinate service and terms, such as the [AMap conversion interface](https://lbs.amap.com/api/webservice/guide/api/convert); no conversion API is invoked by this skill.

## 3. Preserve the meaning of raster values and aggregation

A population count, concentration, density and category need different operations. Choose the target grid's CRS, extent, origin, resolution and missing mask together; sharing only resolution does not establish alignment.

| Value meaning | A defensible direction | Required check |
|---|---|---|
| Category | Nearest/mode appropriate to the source | Codes remain valid; no invented fractional categories |
| Intensive continuous field | Declared interpolation or area-weighted mean | Units/support and missing coverage; do not sum concentrations |
| Cell totals | Conservative redistribution appropriate to the original support | Counts/mass before and after, including edge/mask losses |
| Exposure summary | Explicit area or population weights | Weight denominator, population support and excluded population |

The local `dfproj` pattern uses terra reprojection but its historical `sum` default is unsuitable as a general method. Specify the resampling rule for the quantity; a method named “sum” alone does not establish conservation after changing extent/masks. Use [terra's template-based projection](https://rspatial.github.io/terra/reference/project.html), [Rasterio reprojection](https://rasterio.readthedocs.io/en/stable/topics/reproject.html) and, for partial polygon cells, [exactextractr](https://isciences.gitlab.io/exactextractr/). No raster adapter or conservation validation is implemented here.

## 4. Map the result without changing the analysis

Use the correct geometry support, declare value units and retain missing-data styling. Fix comparable colour limits/breaks for paired scenarios; report values outside the scale rather than silently clipping them. Point, polygon and rectangular grid layers are distinct representations. A basemap is a versioned input, not an implicit file or online download.

Reuse the member's point/polygon and grid/facet patterns through [generalized R helpers](../../skills/model/shared/spatial_analysis/scripts/r/spatial_helpers.R). Basemap inputs, extents, legends and export dimensions belong to task settings; there are no private-path defaults or global boundary objects. Exports specify physical size, DPI and units. Scale bars/north arrows must match the displayed projection and extent. See [ggplot2 sf mapping](https://ggplot2.tidyverse.org/reference/ggsf.html) and [GeoPandas mapping](https://geopandas.org/en/stable/docs/user_guide/mapping.html).

## 5. Treat geocoding as uncertain data acquisition

Normalize addresses without discarding meaningful unit/locality information. Keep source IDs, provider/version, returned coordinate convention, candidate precision and manual-review state. A city centroid is not a building coordinate. Reverse-geocoded text is not proof of a person's location.

Begin with an authorized local gazetteer when possible. Online services need deliberate provider selection and their current privacy, rate, cache and license conditions. geopy/tidygeocoder are clients, not a universal free data source. In particular, the [public Nominatim policy](https://operations.osmfoundation.org/policies/nominatim/) restricts generic agent/platform integration, prohibits personal/confidential submissions and imposes workload conditions; it is not this skill's default provider. Follow the [operating guidance](../../skills/model/shared/spatial_analysis/references/geocoding.md).

## 6. Handoff and review

1. Define objects, spatial/time support, IDs, source versions and intended relation.
2. Verify CRS, geometry and variable units; choose accuracy and aggregation rules.
3. Inspect candidate/missing matches or source/provider suitability before resolving them.
4. Execute the authorized bounded operation on fresh outputs and preserve source inputs.
5. Check cardinality, distances/areas, units, population/mass totals where relevant and map support.
6. Save inputs/configuration identities, QA and results; review before reusing derived data.

Spatial preparation can support data acquisition, prediction and impact assessment without replacing their scientific validation. Operational use is shared across 01, 03 and 04; stage 02 remains conceptual only. Source data stay versioned in external assets, non-secret settings in personal configuration, credentials in their protected mechanism, and results under external `assets/results/<project_id>/`. Sensitive locations never enter shared examples.
