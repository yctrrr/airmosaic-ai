# Generalized from member-supplied point/polygon and grid/facet plotting helpers.
# Defines functions only: no file reads, global assignments, downloads or exports.

.spatial_need <- function(packages) {
  if (any(!vapply(packages, requireNamespace, logical(1), quietly = TRUE)))
    stop("spatial_dependency_missing", call. = FALSE)
}

.spatial_sf <- function(data, types = NULL) {
  .spatial_need("sf")
  if (!inherits(data, "sf") || !nrow(data) || is.na(sf::st_crs(data)))
    stop("spatial_object_or_crs_missing", call. = FALSE)
  if (any(sf::st_is_empty(data)) || !all(sf::st_is_valid(data)))
    stop("spatial_geometry_requires_review", call. = FALSE)
  if (!is.null(types) && !all(as.character(sf::st_geometry_type(data)) %in% types))
    stop("spatial_geometry_type_mismatch", call. = FALSE)
  invisible(data)
}

.spatial_field <- function(data, field, numeric = FALSE) {
  if (!is.character(field) || length(field) != 1L || !field %in% names(data) ||
      anyDuplicated(names(data)))
    stop("spatial_field_missing", call. = FALSE)
  if (numeric && (!is.numeric(data[[field]]) ||
                 any(!is.finite(data[[field]]) & !is.na(data[[field]]))))
    stop("spatial_numeric_field_invalid", call. = FALSE)
}

.spatial_scale <- function(data, value, value_label, limits, colours) {
  .spatial_field(data, value, numeric = TRUE)
  if (!is.character(value_label) || length(value_label) != 1L || !nzchar(value_label))
    stop("spatial_value_label_required", call. = FALSE)
  if (!is.null(limits)) {
    if (!is.numeric(limits) || length(limits) != 2L ||
        any(!is.finite(limits)) || limits[1] >= limits[2])
      stop("spatial_colour_limits_invalid", call. = FALSE)
    observed <- data[[value]][!is.na(data[[value]])]
    if (any(observed < limits[1] | observed > limits[2]))
      stop("spatial_values_outside_declared_limits", call. = FALSE)
  }
  ggplot2::scale_fill_gradientn(name = value_label, colours = colours,
                               limits = limits, na.value = "grey85")
}

# Transform coordinates; never assign a guessed source CRS.
transform_sf <- function(data, target_crs) {
  .spatial_sf(data)
  if (isTRUE(sf::sf_proj_network()))
    stop("spatial_transform_requires_offline_proj", call. = FALSE)
  target <- sf::st_crs(target_crs)
  if (is.na(target)) stop("spatial_target_crs_invalid", call. = FALSE)
  answer <- sf::st_transform(data, target, allow_ballpark = FALSE, partial = FALSE)
  .spatial_sf(answer)
  answer
}

# Preserve one row per point and all candidate IDs; do not resolve ambiguous borders.
point_polygon_matches <- function(points, polygons, point_id, polygon_id,
                                  predicate = c("intersects", "within")) {
  .spatial_sf(points, "POINT")
  .spatial_sf(polygons, c("POLYGON", "MULTIPOLYGON"))
  .spatial_field(points, point_id)
  .spatial_field(polygons, polygon_id)
  for (values in list(points[[point_id]], polygons[[polygon_id]])) {
    if (anyNA(values) || any(!nzchar(trimws(as.character(values)))) || anyDuplicated(as.character(values)))
      stop("spatial_keys_invalid", call. = FALSE)
  }
  if (sf::st_crs(points) != sf::st_crs(polygons))
    stop("spatial_crs_mismatch", call. = FALSE)
  predicate <- match.arg(predicate)
  if (!grepl("^(PROJCRS|PROJCS)\\[", sf::st_crs(points)$wkt))
    stop("spatial_match_requires_reviewed_projected_crs", call. = FALSE)
  hits <- if (predicate == "intersects") sf::st_intersects(points, polygons) else
    sf::st_within(points, polygons)
  counts <- lengths(hits)
  keys <- as.character(polygons[[polygon_id]])
  result <- data.frame(
    sample_id = as.character(points[[point_id]]),
    matched_id = vapply(hits, function(i) if (length(i) == 1L) keys[i] else NA_character_,
                        character(1)),
    n_matches = counts,
    match_status = ifelse(counts == 0L, "unmatched",
                          ifelse(counts == 1L, "matched", "ambiguous")),
    stringsAsFactors = FALSE
  )
  result$candidate_ids <- I(lapply(hits, function(i) keys[i]))
  result
}

# Retains the local helper's sf polygon layer and configurable publication styling.
sf_polygon_plot <- function(data, value, value_label, base_family = "",
                            limits = NULL,
                            colours = rev(grDevices::hcl.colors(7, "YlOrRd"))) {
  .spatial_sf(data, c("POLYGON", "MULTIPOLYGON"))
  .spatial_need("ggplot2")
  ggplot2::ggplot(data) +
    ggplot2::geom_sf(ggplot2::aes(fill = .data[[value]]), colour = NA) +
    .spatial_scale(data, value, value_label, limits, colours) +
    ggplot2::coord_sf() +
    ggplot2::labs(x = NULL, y = NULL) +
    ggplot2::theme_bw(base_family = base_family) +
    ggplot2::theme(legend.position = "bottom",
                   panel.grid.major = ggplot2::element_line(colour = "transparent"))
}

sf_point_plot <- function(data, value, value_label, size = 3.5, alpha = 0.5,
                          limits = NULL,
                          colours = rev(grDevices::hcl.colors(7, "YlOrRd"))) {
  .spatial_sf(data, c("POINT", "MULTIPOINT"))
  .spatial_need("ggplot2")
  if (!is.numeric(size) || length(size) != 1L || !is.finite(size) || size <= 0 ||
      !is.numeric(alpha) || length(alpha) != 1L || !is.finite(alpha) ||
      alpha < 0 || alpha > 1)
    stop("spatial_point_style_invalid", call. = FALSE)
  ggplot2::ggplot(data) +
    ggplot2::geom_sf(ggplot2::aes(fill = .data[[value]]), shape = 21,
                     colour = "white", size = size, alpha = alpha) +
    .spatial_scale(data, value, value_label, limits, colours) +
    ggplot2::coord_sf() +
    ggplot2::labs(x = NULL, y = NULL) +
    ggplot2::theme_bw()
}

# Explicit cell dimensions are in the declared CRS units; no regridding is done.
grid_plot <- function(data, x, y, value, value_label, crs, cell_width, cell_height,
                      facet = NULL, facet_row = 1L, base_family = "", limits = NULL,
                      colours = rev(grDevices::hcl.colors(7, "YlOrRd"))) {
  .spatial_need(c("sf", "ggplot2"))
  if (!is.data.frame(data) || !nrow(data)) stop("spatial_grid_empty", call. = FALSE)
  .spatial_field(data, x, numeric = TRUE)
  .spatial_field(data, y, numeric = TRUE)
  if (anyNA(data[[x]]) || anyNA(data[[y]])) stop("spatial_grid_coordinates_missing", call. = FALSE)
  target <- sf::st_crs(crs)
  dimensions <- c(cell_width, cell_height)
  if (is.na(target) || !grepl("^(PROJCRS|PROJCS)\\[", target$wkt) || length(dimensions) != 2L ||
      any(!is.finite(dimensions)) || any(dimensions <= 0))
    stop("spatial_grid_crs_or_dimensions_invalid", call. = FALSE)
  keys <- c(x, y)
  if (!is.null(facet)) {
    .spatial_field(data, facet)
    keys <- c(keys, facet)
  }
  if (anyDuplicated(data[, keys, drop = FALSE]))
    stop("spatial_grid_duplicate_cells", call. = FALSE)
  answer <- ggplot2::ggplot(data,
    ggplot2::aes(x = .data[[x]], y = .data[[y]], fill = .data[[value]])) +
    ggplot2::geom_tile(width = cell_width, height = cell_height) +
    .spatial_scale(data, value, value_label, limits, colours) +
    ggplot2::coord_fixed(ratio = 1, expand = FALSE) +
    ggplot2::scale_x_continuous(n.breaks = 3,
      labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
    ggplot2::labs(x = paste0(x, " (", target$units_gdal, ")"),
                   y = paste0(y, " (", target$units_gdal, ")")) +
    ggplot2::theme_bw(base_family = base_family)
  if (!is.null(facet))
    answer <- answer + ggplot2::facet_wrap(ggplot2::vars(.data[[facet]]), nrow = facet_row)
  answer
}

grid_facet_plot <- function(data, x, y, value, value_label, crs, cell_width,
                            cell_height, facet, facet_row = 1L, ...) {
  grid_plot(data, x, y, value, value_label, crs, cell_width, cell_height,
            facet = facet, facet_row = facet_row, ...)
}
