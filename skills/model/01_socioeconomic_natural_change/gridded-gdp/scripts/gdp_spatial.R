# Annual raster intake, county predictors, grid prediction, and independent readback.
load_counties <- function(path, province_codes, extent) {
  check_county_source(path)
  counties <- if (grepl("\\.rds$", path, ignore.case = TRUE)) readRDS(path) else
    suppressWarnings(sf::st_read(path, quiet = TRUE))
  require_ok(inherits(counties, "sf") && all(c("PAC", "Province_code") %in% names(counties)),
             "County layer requires PAC and Province_code")
  require_ok(!is.na(sf::st_crs(counties)), "County layer lacks a CRS")
  counties <- sf::st_transform(counties, 4326)
  keep <- !is.na(counties$Province_code) & as.character(counties$Province_code) %in% province_codes
  counties <- counties[keep, ]
  counties$PAC <- key_clean(counties$PAC)
  counties$Province_code <- key_clean(counties$Province_code)
  counties <- counties[order(counties$PAC), ]
  require_ok(setequal(counties$Province_code, province_codes) && !anyDuplicated(counties$PAC), "County map keys or province scope differ")
  require_ok(all(sf::st_is_valid(counties)) && !any(sf::st_is_empty(counties)) &&
               all(sf::st_geometry_type(counties) %in% c("POLYGON", "MULTIPOLYGON")), "Invalid county polygons")
  bbox <- unname(sf::st_bbox(counties))
  require_ok(all(bbox[c(1, 2)] >= extent[c(1, 3)] - 1e-8) && all(bbox[c(3, 4)] <= extent[c(2, 4)] + 1e-8),
             "County boundary goes outside the configured grid")
  counties
}
make_target <- function(extent, resolution) {
  size <- diff(extent[1:2]) / resolution
  height <- diff(extent[3:4]) / resolution
  require_ok(all(is.finite(c(size, height))) && min(size, height) >= 1 &&
               all(abs(c(size, height) - round(c(size, height))) < 1e-7), "Extent is not aligned to grid resolution")
  rast(nrows = round(height), ncols = round(size), xmin = extent[1], xmax = extent[2],
       ymin = extent[3], ymax = extent[4], crs = "EPSG:4326")
}

make_county_grid <- function(extent, resolution) {
  # The historical county features used terra's nominal resolution on the
  # original extent. It rounds the cell count, keeping the extent unchanged.
  rast(ext(extent), resolution = resolution, crs = "EPSG:4326")
}
annual_layer <- function(path, kind, spec, target, year, synthetic) {
  require_ok(length(spec$year) == 1 && spec$year == year && nzchar(spec$version) &&
               is.character(spec$sha256) && grepl("^[a-f0-9]{64}$", spec$sha256),
             paste("Missing annual source metadata for", kind))
  if (!synthetic) {
    expected <- c(light = "Harvard Dataverse", population = "LandScan Global 30 arcsec",
                  cover = "C3S satellite-land-cover")
    require_ok(identical(spec$product, unname(expected[kind])), paste("Unexpected source product for", kind))
    if (kind == "cover") require_ok(spec$version %in% c("2.1.1", "v2.1.1"), "Unexpected land cover version")
  }
  if (grepl("\\.nc$", path, ignore.case = TRUE) && kind == "cover") {
    layer <- rast(path, subds = "lccs_class")
  } else {
    layer <- rast(path)
  }
  if (nlyr(layer) > 1L) {
    index <- match(spec$layer, names(layer))
    require_ok(length(index) == 1L && !is.na(index), "Select an exact annual layer name")
    layer <- layer[[index]]
  }
  require_ok(nlyr(layer) == 1L && is.lonlat(layer) && same.crs(layer, target), "Annual input must be geographic WGS84")
  times <- time(layer)
  if (has.time(layer)) {
    date <- if (timeInfo(layer)$step == "years") as.integer(times) else
      if (inherits(times, c("Date", "POSIXt"))) as.integer(format(times, "%Y")) else NA_integer_
    require_ok(length(date) == 1L && isTRUE(date == year), "Embedded raster year contradicts manifest")
  } else if (kind == "cover" && grepl("\\.nc$", path, ignore.case = TRUE)) {
    stop("NetCDF land cover has no readable year", call. = FALSE)
  }
  extent <- as.vector(ext(layer))
  bounds <- as.vector(ext(target))
  require_ok(all(extent[c(1, 3)] <= bounds[c(1, 3)] + 1e-8) && all(extent[c(2, 4)] >= bounds[c(2, 4)] - 1e-8),
             "Annual layer does not span configured grid")
  if (!synthetic && kind == "population")
    require_ok(all(abs(res(layer) - 1 / 120) < 1e-7), "Population resolution differs from 30 arcseconds")
  if (!synthetic && kind == "cover")
    require_ok(all(abs(res(layer) - 1 / 360) < 1e-7), "Land cover grid differs from 1/360 degree")
  layer <- crop(layer, ext(target), snap = "out")
  readStart(layer)
  on.exit(readStop(layer))
  for (first in seq.int(1L, nrow(layer), by = 128L)) {
    values <- readValues(layer, first, min(128L, nrow(layer) - first + 1L))
    require_ok(all(is.na(values) | (is.finite(values) & values >= 0)), "Negative or nonfinite predictor values")
    if (kind == "cover") require_ok(all(is.na(values) | values %in% c(0, lccs_codes)), "Unexpected LCCS code")
  }
  layer
}
land_counts <- function(cover, template, directory, prefix) {
  all_groups <- c(list(Total_grid = lccs_codes), groups)
  rasters <- lapply(names(all_groups), function(name) {
    codes <- as.integer(all_groups[[name]])
    binary <- classify(cover, rbind(cbind(codes, 1L), c(NA, 0)), others = 0L,
                       filename = tempfile("class-", tmpdir = directory, fileext = ".tif"),
                       wopt = list(datatype = "INT1U"))
    sum_to_grid(binary, template, file.path(directory, paste0(prefix, "_", name, ".tif")))
  })
  result <- do.call(c, rasters)
  names(result) <- names(all_groups)
  result
}
zonal <- function(layers, counties) {
  as.data.table(exactextractr::exact_extract(layers, counties, "sum", progress = FALSE, max_cells_in_memory = 2e6))
}
features_from_counts <- function(rows, year) {
  rows[, (names(groups)) := lapply(.SD, function(x) x / Total_grid), .SDcols = names(groups)]
  rows[, c("Year", "NTL_Pop") := .(year, fifelse(Pop_all > 0, NTL_all / pmax(Pop_all, .Machine$double.xmin), 0))]
  validate_features(rows)
  rows
}
prepare_predictors <- function(paths, spec, year, counties, geo, synthetic, directory) {
  scratch <- file.path(directory, "scratch")
  dir.create(scratch)
  on.exit(unlink(scratch, recursive = TRUE))
  terraOptions(tempdir = scratch, progress = 0)
  grid <- make_target(geo$extent, geo$resolution)
  coarse <- make_county_grid(geo$extent, geo$county_resolution)
  cover <- annual_layer(paths$cover, "cover", spec$cover, grid, year, synthetic)
  pop <- annual_layer(paths$population, "population", spec$population, grid, year, synthetic)
  light <- annual_layer(paths$light, "light", spec$light, grid, year, synthetic)
  coarse_counts <- land_counts(cover, coarse, scratch, "county")
  counts <- zonal(coarse_counts, counties)
  names(counts) <- names(coarse_counts)
  counties_xy <- sf::st_coordinates(suppressWarnings(sf::st_centroid(sf::st_geometry(counties))))
  rows <- cbind(data.table(PAC = counties$PAC, Province_code = counties$Province_code,
                           cenlon = counties_xy[, 1], cenlat = counties_xy[, 2]), counts)
  rows[, Pop_all := zonal(pop, counties)[[1L]]]
  rows[, NTL_all := zonal(light, counties)[[1L]]]
  require_ok(all(is.finite(rows$Pop_all) & rows$Pop_all >= 0 & is.finite(rows$NTL_all) &
                   rows$Total_grid > 0), "Annual data do not cover the configured counties")
  fwrite(features_from_counts(rows, year), file.path(directory, "county_features.csv"))

  counts <- land_counts(cover, grid, scratch, "grid")
  pop_grid <- sum_to_grid(pop, grid, file.path(scratch, "population.tif"))
  light_grid <- sum_to_grid(light, grid, file.path(scratch, "lights.tif"))
  names(pop_grid) <- "Pop_all"
  names(light_grid) <- "NTL_all"
  # Compare population over the same rectangular footprint even when native pixels
  # straddle its edges. Compare to source overlap fractions, not a snapped crop sum.
  if (!all(abs(as.vector(ext(pop)) - as.vector(ext(grid))) < 1e-10)) {
    footprint <- sf::st_as_sf(as.polygons(ext(grid), crs = crs(grid)))
    source_population <- zonal(pop, footprint)[[1L]]
  } else {
    source_population <- global(pop, "sum", na.rm = TRUE)[[1L]]
  }
  grid_population <- global(pop_grid, "sum", na.rm = TRUE)[[1L]]
  require_ok(is.finite(source_population) && source_population > 0 &&
               abs(grid_population / source_population - 1) <= 1e-6, "Population resampling fails conservation")
  writeRaster(c(counts, pop_grid, light_grid), file.path(directory, "grid_predictors.tif"),
              datatype = "FLT8S", gdal = "COMPRESS=DEFLATE")
  write_json(list(year = year, population_source_footprint = source_population,
                  population_target_footprint = grid_population,
                  grid_resolution = res(grid), extent = as.vector(ext(grid))),
             file.path(directory, "alignment.json"))
}
weighted_targets <- function(rows, keys, value, weight) {
  rows[, .(weighted = sum(get(weight) * get(value)) / sum(get(weight))), by = keys]
}
calibrate_counties <- function(rows, observed, province, model) {
  rows <- copy(rows)
  rows[observed, observed_gdp := i.observed_gdp, on = .(PAC, Province_code)]
  rows[, is_predicted := is.na(observed_gdp)]
  rows[, GDP_pc_before_calibration := observed_gdp]
  require_ok(any(!rows$is_predicted), "No positive same-year county GDP observations")
  if (any(rows$is_predicted)) rows[is_predicted == TRUE, GDP_pc_before_calibration := predict_gdp(model, .SD)]
  weights <- weighted_targets(rows, "Province_code", "GDP_pc_before_calibration", "Pop_all")
  require_ok(setequal(province$Province_code, weights$Province_code), "Missing same-year province benchmark")
  weights[province, benchmark_gdp_pc := i.benchmark_gdp_pc, on = "Province_code"]
  weights[, factor1 := benchmark_gdp_pc / weighted]
  require_ok(all(is.finite(weights$factor1) & weights$factor1 > 0), "Invalid province calibration")
  rows[weights, factor1 := i.factor1, on = "Province_code"]
  rows[, GDP_pc_from_CSMAR := GDP_pc_before_calibration * factor1]
  list(county = rows, province = weights)
}
predict_grid <- function(layers, coverage, model, year, path) {
  template <- rast(layers[[1]])
  names(template) <- "GDP_pc_raw"
  readStart(layers)
  on.exit(readStop(layers))
  writeStart(template, path, overwrite = FALSE, wopt = list(datatype = "FLT8S", gdal = "COMPRESS=DEFLATE"))
  for (first in seq.int(1L, nrow(layers), by = 25L)) {
    nr <- min(25L, nrow(layers) - first + 1L)
    cells <- seq.int((first - 1L) * ncol(layers) + 1L, length.out = nr * ncol(layers))
    data <- as.data.table(readValues(layers, row = first, nrows = nr, mat = TRUE))
    require_ok(identical(names(data), names(layers)), "Grid predictors lost layer names")
    valid <- which(coverage$sum_fraction[cells] > 0 & data$Total_grid > 0 &
                     is.finite(data$Pop_all) & is.finite(data$NTL_all))
    values <- rep(NA_real_, length(cells))
    if (length(valid)) {
      xy <- xyFromCell(layers, cells[valid])
      batch <- data[valid]
      batch[, c("cenlon", "cenlat") := .(round(xy[, 1], 3), round(xy[, 2], 3))]
      values[valid] <- predict_gdp(model, features_from_counts(batch, year))
    }
    writeValues(template, values, first, nr)
  }
  writeStop(template)
}
build_grid <- function(layers, counties, coverage, rows, model, year, tif, factors_path) {
  scratch <- tempfile("predictions-", tmpdir = dirname(tif), fileext = ".tif")
  on.exit(unlink(scratch))
  raw <- predict_grid(layers, coverage, model, year, scratch)
  population <- layers[["Pop_all"]]
  totals <- zonal(c(raw * population, population), counties)
  setnames(totals, c("GDP", "Pop"))
  target <- rows[match(counties$PAC, PAC), GDP_pc_from_CSMAR]
  require_ok(identical(coverage$PAC, counties$PAC) &&
               all(is.finite(target) & target > 0 & is.finite(totals$Pop) & totals$Pop >= 0) &&
               all(is.finite(totals$GDP[totals$Pop > 0]) & totals$GDP[totals$Pop > 0] > 0),
             "County raw grid totals fail calibration preflight")
  totals[, GDP_pc := fifelse(Pop > 0, GDP / Pop, 0)]
  totals[, factor2 := fifelse(Pop > 0, target / GDP_pc, 0)]
  weighted <- numeric(ncell(raw))
  for (i in seq_along(coverage$cells)) {
    part <- coverage$cells[[i]]
    weighted[part$cell] <- weighted[part$cell] + part$fraction * totals$factor2[i]
  }
  fraction <- coverage$sum_fraction
  factor <- setValues(rast(raw), ifelse(fraction > 0, weighted / fraction, NA_real_))
  mask_factor <- ifel(factor > 0 & is.finite(raw), factor, NA)
  product <- c(raw * mask_factor, mask(population, mask_factor), mask_factor)
  names(product) <- c("GDP_pc", "Pop_all", "factor2")
  writeRaster(product, tif, datatype = "FLT4S", gdal = "COMPRESS=DEFLATE")
  fwrite(cbind(rows[match(counties$PAC, PAC), .(PAC, Province_code, Year)],
               data.table(GDP_pc_county_value = target), totals), factors_path)
}
accept_grid <- function(path, county_path, province_path, counties, geo, thresholds, year,
                        aligned_population, reference = NULL) {
  grid <- rast(path)
  target <- make_target(geo$extent, geo$resolution)
  require_ok(compareGeom(grid, target, stopOnError = FALSE) &&
               identical(names(grid), c("GDP_pc", "Pop_all", "factor2")), "GeoTIFF geometry or layers changed")
  require_ok(nlyr(aligned_population) == 1L && compareGeom(grid, aligned_population, stopOnError = FALSE),
             "Aligned population grid differs from the output geometry")
  if (!is.null(reference)) {
    old <- rast(reference)
    require_ok(compareGeom(grid, old, stopOnError = FALSE) && identical(names(grid), names(old)),
               "Incompatible reference grid")
  }
  readStart(grid)
  reader_open <- TRUE
  on.exit(if (reader_open) readStop(grid))
  valid_count <- 0
  for (first in seq.int(1L, nrow(grid), by = 128L)) {
    values <- readValues(grid, row = first, nrows = min(128L, nrow(grid) - first + 1L), mat = TRUE)
    missing <- is.na(values)
    require_ok(all(rowSums(missing) %in% c(0L, 3L)), "Output layers disagree on NoData")
    kept <- values[!missing[, 1L], , drop = FALSE]
    require_ok(all(is.finite(kept)) && all(kept[, 1L] > 0 & kept[, 2L] >= 0 & kept[, 3L] > 0), "Invalid released pixels")
    valid_count <- valid_count + nrow(kept)
  }
  readStop(grid)
  reader_open <- FALSE
  require_ok(valid_count > 0L, "No useful grid cells")
  target_rows <- fread(county_path, colClasses = list(character = c("PAC", "Province_code")))
  province <- fread(province_path, colClasses = list(character = "Province_code"))
  unique_keys(target_rows, "PAC")
  unique_keys(province, "Province_code")
  require_ok(setequal(target_rows$PAC, counties$PAC) && all(target_rows$Year == year) &&
               setequal(province$Province_code, counties$Province_code), "Readback county or province keys incomplete")
  province_check <- weighted_targets(target_rows, "Province_code", "GDP_pc_from_CSMAR", "Pop_all")
  province_error <- max(abs(province_check$weighted / province$benchmark_gdp_pc[match(province_check$Province_code,
                                                                                      province$Province_code)] - 1))
  require_ok(is.finite(province_error) && province_error <= thresholds$province_max_rel, "Province calibration did not close")
  comparison <- c(grid[["GDP_pc"]] * grid[["Pop_all"]], grid[["Pop_all"]], aligned_population)
  names(comparison) <- c("GDP", "Pop", "aligned_pop")
  totals <- zonal(comparison, counties)
  setnames(totals, names(comparison))
  # NoData is permitted outside the study support and for zero-population cells.
  # A GDP mask must not remove population from the same-year aligned inputs.
  require_ok(all(is.finite(totals$aligned_pop) & totals$aligned_pop >= 0 & is.finite(totals$Pop)),
             "Missing county population in grid readback")
  population_error <- abs(totals$Pop - totals$aligned_pop) / pmax(1, totals$aligned_pop)
  require_ok(max(population_error) <= 1e-6, "Grid readback does not conserve aligned county population")
  official <- target_rows[match(counties$PAC, PAC)]
  if (is.null(reference)) reference_pop <- official$Pop_all
  else reference_pop <- zonal(old[["Pop_all"]], counties)[[1L]]
  positive <- is.finite(totals$Pop) & totals$Pop > 0
  require_ok(identical(positive, is.finite(reference_pop) & reference_pop > 0) &&
               sum(positive) >= thresholds$min_positive_counties, "Grid omits positive-population counties")
  error <- rep(NA_real_, nrow(official))
  error[positive] <- abs(totals$GDP[positive] / totals$Pop[positive] / official$GDP_pc_from_CSMAR[positive] - 1)
  p95 <- unname(quantile(error[positive], .95))
  maximum <- max(error[positive])
  require_ok(is.finite(p95) && p95 <= thresholds$county_p95_rel && maximum <= thresholds$county_max_rel,
             "County grid readback exceeds tolerance")
  list(summary = list(year = year, valid_cells = valid_count, positive_counties = sum(positive),
                      provinces = nrow(province_check), province_max_rel = province_error,
                      county_population_max_rel = max(population_error),
                      county_median_rel = median(error[positive]), county_p95_rel = p95,
                      county_max_rel = maximum),
       readback = data.table(PAC = official$PAC, Year = year, Pop = totals$Pop,
                             GDP_pc = ifelse(positive, totals$GDP / totals$Pop, NA_real_),
                             absolute_relative_error = error))
}
