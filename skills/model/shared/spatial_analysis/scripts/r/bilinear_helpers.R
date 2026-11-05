# Pure, base-R bilinear interpolation for explicitly geographic regular grids.
# Matrix layout is [y, x]. Indices always refer to the original axis order.
# Sourcing this file performs no I/O, network calls or dependency loading.

.bilinear_axis <- function(axis, name, limits) {
  if (!is.numeric(axis) || is.complex(axis) || !is.null(dim(axis)) || length(axis) < 2L ||
      any(!is.finite(axis)) || anyDuplicated(axis) ||
      any(axis < limits[1L] | axis > limits[2L])) {
    stop(name, " must be a finite, unique one-dimensional geographic axis")
  }
  delta <- diff(axis)
  if (!(all(delta > 0) || all(delta < 0))) {
    stop(name, " must be strictly ascending or descending")
  }
  if (any(abs(delta - delta[1L]) > 1e-12 + 1e-10 * abs(delta[1L]))) {
    stop(name, " must be equally spaced")
  }
  axis
}

# Return four rows per point in geographic sw, se, nw, ne order.
bilinear_weights <- function(x, y, points, point_ids, source_crs, point_crs) {
  if (!identical(source_crs, "EPSG:4326") ||
      !identical(point_crs, "EPSG:4326")) {
    stop("source_crs and point_crs must both be explicitly EPSG:4326")
  }
  x <- .bilinear_axis(x, "x", c(-180, 360))
  y <- .bilinear_axis(y, "y", c(-90, 90))
  if (diff(range(x)) > 180 ||
      !(all(x >= -180 & x <= 180) || all(x >= 0 & x <= 360))) {
    stop("x must be a nonperiodic regional axis within one longitude convention")
  }
  if (!is.matrix(points) || !is.numeric(points) || is.complex(points) || ncol(points) != 2L ||
      any(!is.finite(points))) {
    stop("points must be a finite numeric n-by-2 matrix")
  }
  if (!is.character(point_ids) || length(point_ids) != nrow(points) ||
      anyNA(point_ids) || any(!nzchar(trimws(point_ids))) ||
      anyDuplicated(point_ids)) {
    stop("point_ids must be nonempty unique character IDs, one per point")
  }
  if (any(points[, 1L] < min(x) | points[, 1L] > max(x) |
          points[, 2L] < min(y) | points[, 2L] > max(y))) {
    stop("extrapolation is not permitted")
  }
  result <- data.frame(point_id = character(), neighbor = character(),
                       row_index = integer(), col_index = integer(),
                       source_x = numeric(), source_y = numeric(),
                       weight = numeric(), stringsAsFactors = FALSE)
  if (!nrow(points)) return(result)
  xo <- order(x)
  yo <- order(y)
  xs <- x[xo]
  ys <- y[yo]
  rows <- lapply(seq_len(nrow(points)), function(i) {
    ix <- min(findInterval(points[i, 1L], xs), length(xs) - 1L)
    iy <- min(findInterval(points[i, 2L], ys), length(ys) - 1L)
    tx <- (points[i, 1L] - xs[ix]) / (xs[ix + 1L] - xs[ix])
    ty <- (points[i, 2L] - ys[iy]) / (ys[iy + 1L] - ys[iy])
    ci <- xo[c(ix, ix + 1L, ix, ix + 1L)]
    ri <- yo[c(iy, iy, iy + 1L, iy + 1L)]
    data.frame(point_id = rep(point_ids[i], 4L),
               neighbor = c("sw", "se", "nw", "ne"),
               row_index = ri, col_index = ci,
               source_x = x[ci], source_y = y[ri],
               weight = c((1 - tx) * (1 - ty), tx * (1 - ty),
                          (1 - tx) * ty, tx * ty),
               stringsAsFactors = FALSE)
  })
  do.call(rbind, rows)
}

# Missing support with positive weight is propagated without renormalization.
sample_bilinear <- function(values, weights) {
  if (!is.matrix(values) || !is.numeric(values) || is.complex(values) ||
      nrow(values) < 2L || ncol(values) < 2L) {
    stop("values must be a numeric [y, x] matrix with at least two rows/columns")
  }
  fields <- c("point_id", "neighbor", "row_index", "col_index",
              "source_x", "source_y", "weight")
  if (!is.data.frame(weights) || !setequal(fields, names(weights)) ||
      anyDuplicated(names(weights))) stop("weights must contain the complete schema")
  if (!is.character(weights$point_id) || anyNA(weights$point_id) ||
      any(!nzchar(trimws(weights$point_id))) ||
      !is.character(weights$neighbor) || anyNA(weights$neighbor)) {
    stop("point_id and neighbor must be nonempty character columns")
  }
  for (field in fields[3L:7L]) {
    if (!is.numeric(weights[[field]]) || is.complex(weights[[field]]) ||
        !is.null(dim(weights[[field]])) || any(!is.finite(weights[[field]]))) {
      stop(field, " must be finite numeric")
    }
  }
  if (any(weights$row_index != floor(weights$row_index) |
          weights$row_index < 1L | weights$row_index > nrow(values)) ||
      any(weights$col_index != floor(weights$col_index) |
          weights$col_index < 1L | weights$col_index > ncol(values)) ||
      any(weights$weight < 0 | weights$weight > 1)) stop("invalid indices or weights outside [0, 1]")
  ids <- unique(weights$point_id)
  result <- data.frame(point_id = ids, value = rep(NA_real_, length(ids)),
                       status = rep("ok", length(ids)), stringsAsFactors = FALSE)
  for (i in seq_along(ids)) {
    w <- weights[weights$point_id == ids[i], , drop = FALSE]
    if (nrow(w) != 4L || anyDuplicated(w$neighbor) ||
        !setequal(w$neighbor, c("sw", "se", "nw", "ne")) ||
        anyDuplicated(w[c("row_index", "col_index")]) ||
        abs(sum(w$weight) - 1) > 1e-12) {
      stop("each point must have four unique neighbors and weights summing to one")
    }
    support <- values[cbind(w$row_index, w$col_index)]
    positive <- w$weight > 0
    if (any(!is.finite(support[positive]))) {
      result$status[i] <- "missing_support"
    } else {
      result$value[i] <- sum(support[positive] * w$weight[positive])
    }
  }
  result
}
