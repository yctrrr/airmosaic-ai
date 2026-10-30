# Run from the repository root; only in-memory synthetic geometries are used.
module <- new.env(parent = baseenv())
sys.source("skills/model/shared/spatial_analysis/scripts/r/spatial_helpers.R", envir = module)
stopifnot(requireNamespace("sf", quietly = TRUE), requireNamespace("ggplot2", quietly = TRUE))
Sys.setenv(PROJ_NETWORK = "OFF")
sf::sf_proj_network(FALSE)
square <- function(xmin) sf::st_polygon(list(matrix(c(
  xmin, 0, xmin + 1000, 0, xmin + 1000, 1000, xmin, 1000, xmin, 0
), ncol = 2, byrow = TRUE)))
areas <- sf::st_sf(area_id = c("A", "B"), value = c(1, 2),
  geometry = sf::st_sfc(square(500000), square(501000), crs = 32631))
points <- sf::st_as_sf(data.frame(
  sample_id = c("inside", "boundary", "outside"), value = c(1, 2, 3),
  x = c(500500, 501000, 503000), y = c(500, 500, 500)
), coords = c("x", "y"), crs = 32631)
matches <- module$point_polygon_matches(points, areas, "sample_id", "area_id")
stopifnot(identical(matches$n_matches, c(1L, 2L, 0L)),
          identical(matches$match_status, c("matched", "ambiguous", "unmatched")),
          identical(matches$matched_id, c("A", NA_character_, NA_character_)))
stopifnot(identical(unclass(matches$candidate_ids), list("A", c("A", "B"), character(0))))
strict <- module$point_polygon_matches(points, areas, "sample_id", "area_id", "within")
stopifnot(identical(strict$n_matches, c(1L, 0L, 0L)))
back <- module$transform_sf(module$transform_sf(points, 4326), 32631)
roundtrip_error_m <- as.numeric(sf::st_distance(points, back, by_element = TRUE))
stopifnot(max(roundtrip_error_m) < 0.001)
grid <- data.frame(x = c(500500, 501500), y = c(500, 500), value = c(1, 2))
facets <- rbind(transform(grid, scenario = "baseline"),
                transform(grid, scenario = "comparison", value = value + 1))
plots <- list(
  polygons = module$sf_polygon_plot(areas, "value", "Synthetic index (1)", limits = c(0, 3)),
  points = module$sf_point_plot(points, "value", "Synthetic index (1)", limits = c(0, 3)),
  grid = module$grid_plot(grid, "x", "y", "value", "Synthetic index (1)", 32631, 1000, 1000),
  facets = module$grid_facet_plot(facets, "x", "y", "value", "Synthetic index (1)",
                                 32631, 1000, 1000, "scenario", limits = c(0, 3))
)
for (plot in plots) invisible(ggplot2::ggplot_build(plot))
fails <- function(expr) inherits(tryCatch(force(expr), error = identity), "error")
stopifnot(fails(module$point_polygon_matches(sf::st_transform(points, 4326), areas,
                                             "sample_id", "area_id")),
          fails(module$sf_polygon_plot(areas, "value", "Synthetic index (1)", limits = c(0, 1))),
          fails(module$grid_plot(rbind(grid, grid[1, ]), "x", "y", "value",
                                  "Synthetic index (1)", 32631, 1000, 1000)),
          fails(module$point_polygon_matches(
            sf::st_set_crs(points, NA), areas, "sample_id", "area_id")),
          fails(module$point_polygon_matches(
            transform(points, sample_id = c("same", "same", "other")), areas,
            "sample_id", "area_id")),
          fails(module$point_polygon_matches(
            module$transform_sf(points, 4326), module$transform_sf(areas, 4326),
            "sample_id", "area_id")))
args <- commandArgs(trailingOnly = TRUE)
if (length(args)) {
  stopifnot(length(args) == 1L, dir.exists(args[[1]]))
  targets <- file.path(args[[1]], paste0(names(plots), ".png"))
  stopifnot(!any(file.exists(targets)))
  for (i in seq_along(plots))
    ggplot2::ggsave(targets[[i]], plots[[i]], width = 14, height = 10, units = "cm", dpi = 120)
}
cat("Synthetic boundary predicates, projected CRS round-trip, four plot builds and six refusal checks passed.\n")
