# Adapted from the original GDP overlap-weighted sum. Each source value is
# apportioned by its overlap with the target lattice in geographic coordinates.
gdp_overlap_weights <- function(source_start, source_width, source_count,
                                target_start, target_width, target_count) {
  left <- (target_start - source_start + seq.int(0, target_count - 1L) * target_width) / source_width
  right <- left + target_width / source_width
  first <- pmax.int(0L, floor(left))
  last <- pmin.int(source_count - 1L, ceiling(right) - 1L)
  size <- pmax.int(0L, last - first + 1L)
  destination <- rep.int(seq_len(target_count), size)
  origin <- sequence(size, from = first)
  fraction <- pmax(0, pmin(right[destination], origin + 1) - pmax(left[destination], origin))
  Matrix::sparseMatrix(i = destination, j = origin + 1L, x = fraction,
                       dims = c(target_count, source_count))
}

sum_to_grid <- function(source, target, path) {
  stopifnot(nlyr(source) == 1L, same.crs(source, target), is.lonlat(source))
  template <- rast(target)
  names(template) <- names(source)
  horizontal <- Matrix::t(gdp_overlap_weights(xmin(source), xres(source), ncol(source),
                                               xmin(target), xres(target), ncol(target)))
  vertical <- gdp_overlap_weights(-ymax(source), yres(source), nrow(source),
                                  -ymax(target), yres(target), nrow(target))
  readStart(source)
  on.exit(readStop(source), add = TRUE)
  writeStart(template, path, overwrite = FALSE, wopt = list(datatype = "FLT8S", gdal = "COMPRESS=DEFLATE"))
  for (first in seq.int(1L, nrow(template), by = 120L)) {
    count <- min(120L, nrow(template) - first + 1L)
    band <- vertical[seq.int(first, length.out = count), , drop = FALSE]
    active <- which(Matrix::colSums(band) > 0)
    if (!length(active)) {
      writeValues(template, rep(NA_real_, count * ncol(template)), first, count)
      next
    }
    rows <- seq.int(min(active), max(active))
    raw <- matrix(readValues(source, row = rows[1], nrows = length(rows)), nrow = length(rows), byrow = TRUE)
    present <- !is.na(raw)
    raw[!present] <- 0
    weights <- band[, rows, drop = FALSE]
    total <- as.matrix((weights %*% raw) %*% horizontal)
    support <- as.matrix((weights %*% (present * 1)) %*% horizontal)
    total[support == 0] <- NA_real_
    writeValues(template, as.vector(t(total)), first, count)
  }
  template <- writeStop(template)
  stopifnot(compareGeom(template, target, stopOnError = FALSE))
  template
}

county_coverage <- function(template, counties) {
  cells <- vector("list", nrow(counties))
  sum_fraction <- numeric(ncell(template))
  for (first in seq.int(1L, nrow(counties), by = 32L)) {
    indices <- seq.int(first, min(first + 31L, nrow(counties)))
    pieces <- exactextractr::exact_extract(template, counties[indices, ], include_cell = TRUE, progress = FALSE)
    for (j in seq_along(indices)) {
      cell <- as.integer(pieces[[j]]$cell)
      fraction <- pieces[[j]]$coverage_fraction
      require_ok(length(cell) > 0L && !anyDuplicated(cell) &&
                   all(is.finite(fraction) & fraction > 0 & fraction <= 1 + 1e-6), "Invalid county coverage")
      sum_fraction[cell] <- sum_fraction[cell] + fraction
      cells[[indices[j]]] <- list(cell = cell, fraction = fraction)
    }
  }
  require_ok(max(sum_fraction) <= 1 + 1e-5, "County polygons overlap on the target grid")
  list(cells = cells, sum_fraction = sum_fraction, PAC = counties$PAC)
}
