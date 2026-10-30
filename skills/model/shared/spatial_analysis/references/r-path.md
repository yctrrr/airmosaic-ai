# R path: sf and local mapping helpers

**English** | [中文](r-path_ZH.md)

Use sf and ggplot2 for the implemented functions, with terra/exactextractr only for separately adapted raster tasks. Follow the [common configuration and result contract](operations.md). The grid helpers accept projected rectangles with explicit cell dimensions, not arbitrary curvilinear or geographic raster cells.

Select a dedicated R environment with sf and ggplot2 installed. If setup is needed, run the following explicitly; Linux source builds may also require the native libraries described in the [sf installation guide](https://r-spatial.github.io/sf/).

```r
install.packages(c("sf", "ggplot2"))
```

From repository root:

```sh
Rscript --vanilla skills/model/shared/spatial_analysis/examples/r/synthetic_spatial.R
```

The synthetic script checks topology/CRS and builds four plot types, without reading business data or exporting by default. An explicitly supplied fresh output directory is only for reviewed synthetic image checks.

## Reusing the local R methods


| Original pattern | Current reusable form | Adaptation |
|---|---|---|
| `sf_polygon_plot` / `sf_point_plot` | Same function names in the reviewed module | Explicit value label and limits, modern column evaluation and namespaced calls |
| `grid_plot` / `grid_facet_plot` | Same function names | Required CRS and rectangular cell dimensions; no implicit projection or input loading |
| `dfproj` | Not copied as a general adapter | Select resampling from quantity meaning; historical sum/projection defaults require adaptation |
| Boundary loaders, global labels and insets | Task-level inputs/design | No fixed source directories, global objects, automatic country bounds or source-time demonstration |
| Historical export helper | Explicit export call after review | Physical units and DPI cannot be exchanged with pixel dimensions |

The user's original files remain unchanged. The extracted functions preserve the plotting pattern, with generalized interfaces and styling, rather than promising byte-identical legacy figures. No source paths or private map layers are copied.

Load the module from repository root, with already authorized sf objects `sites` and `areas`:

```r
spatial <- new.env(parent = baseenv())
sys.source("skills/model/shared/spatial_analysis/scripts/r/spatial_helpers.R",
           envir = spatial)
sf::sf_proj_network(FALSE)
sites_work <- spatial$transform_sf(sites, working_crs)
areas_work <- spatial$transform_sf(areas, working_crs)
matched <- spatial$point_polygon_matches(
  sites_work, areas_work, "sample_id", "area_id", predicate = "intersects"
)
plot <- spatial$sf_polygon_plot(
  areas_work, "value", "Study value (declared unit)", limits = shared_limits
)
```

`working_crs` and `shared_limits` are task choices, not implicit defaults. Coordinate transformation refuses enabled PROJ networking and ballpark operations; review the available pipeline and its accuracy for the task. The matching helper requires a reviewed projected CRS, unique keys and valid point/polygon geometries. It returns one row per point, a unique match only when available, match count/status and a list of all candidate IDs. It does not resolve borders or perform nearest matching. Callers must preserve the list when exporting; do not silently drop it into an unsupported CSV representation.

For a fresh authorized output `target_plot`, an explicit export can use:

```r
if (file.exists(target_plot)) stop("fresh_output_required")
ggplot2::ggsave(target_plot, plot, width = 14, height = 10,
                units = "cm", dpi = 300)
```

Verify the destination under the external project root before this call; it is a direct library operation, not a runner-protected export. Grid plotting draws declared rectangles only; it does not reconstruct curvilinear cell boundaries, reproject rasters or validate totals.
