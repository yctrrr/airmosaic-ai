# Small hand-calculated checks, without model training or original data.
args <- commandArgs(TRUE)
stopifnot(length(args) == 2L)
scripts <- normalizePath(args[1L], winslash = "/")
directory <- normalizePath(args[2L], winslash = "/")
for (name in c("gdp_common.R", "grid_overlap_sum.R", "gdp_spatial.R")) source(file.path(scripts, name))

# The shipped grid has 3,541 fine rows. Preserve its extent at both scales.
original_extent <- c(73.5, 134.8, 18.16, 53.57)
fine <- make_target(original_extent, .01)
coarse <- make_county_grid(original_extent, .1)
stopifnot(nrow(fine) == 3541L, ncol(fine) == 6130L, nrow(coarse) == 354L,
          ncol(coarse) == 613L, max(abs(as.vector(ext(coarse)) - original_extent)) < 1e-12)

# Two native count cells split across an offset two-cell target lattice.
native <- rast(nrows = 1, ncols = 2, xmin = 0, xmax = 2, ymin = 0, ymax = 1, crs = "EPSG:4326")
native <- setValues(native, c(10, 30))
target <- rast(nrows = 1, ncols = 2, xmin = .5, xmax = 2.5, ymin = 0, ymax = 1, crs = "EPSG:4326")
result <- sum_to_grid(native, target, file.path(directory, "overlap.tif"))
stopifnot(isTRUE(all.equal(as.vector(values(result)), c(20, 15))))

# Two aligned county cells: the first has zero population and must remain NoData.
template <- rast(nrows = 1, ncols = 2, xmin = 100, xmax = 100.02, ymin = 30, ymax = 30.01, crs = "EPSG:4326")
map <- sf::st_as_sf(as.polygons(setValues(template, 1:2)))
map$PAC <- c("110001", "110002")
map$Province_code <- c("110000", "110000")
gpkg <- file.path(directory, "county.gpkg")
sf::st_write(map, gpkg, layer = "county", quiet = TRUE)
stopifnot(nrow(load_counties(gpkg, "110000", c(100, 100.02, 30, 30.01))) == 2L)
sf::st_write(map, gpkg, layer = "another", quiet = TRUE)
stopifnot(identical(tryCatch(check_county_source(gpkg), error = conditionMessage),
                    "County GeoPackage must contain exactly one layer"))
layers <- setValues(template, c(0, 100))
names(layers) <- "Pop_all"
coverage <- county_coverage(layers, map)
rows <- data.table(PAC = map$PAC, Province_code = map$Province_code, Year = 2024L,
                   Pop_all = c(0, 100), GDP_pc_from_CSMAR = c(1000, 2000))
# Inject a known uncalibrated prediction to isolate the calibration arithmetic.
predict_grid <- function(layers, coverage, model, year, path) {
  prediction <- setValues(rast(layers[[1L]]), c(50, 100))
  names(prediction) <- "GDP_pc_raw"
  writeRaster(prediction, path)
}
tif <- file.path(directory, "calibration.tif")
build_grid(layers, map, coverage, rows, NULL, 2024L, tif, file.path(directory, "factors.csv"))
pixels <- values(rast(tif), mat = TRUE)
stopifnot(all(is.na(pixels[1L, ])), abs(pixels[2L, 1L] - 2000) < 1e-8,
          pixels[2L, 2L] == 100, pixels[2L, 3L] == 20)
fwrite(rows, file.path(directory, "county.csv"))
fwrite(data.table(Province_code = "110000", benchmark_gdp_pc = 2000), file.path(directory, "province.csv"))
check <- accept_grid(tif, file.path(directory, "county.csv"), file.path(directory, "province.csv"), map,
                     list(extent = c(100, 100.02, 30, 30.01), resolution = .01),
                     list(province_max_rel = 1e-10, min_positive_counties = 1L,
                          county_p95_rel = 1e-6, county_max_rel = 1e-6), 2024L, layers)
stopifnot(check$summary$positive_counties == 1L, check$summary$valid_cells == 1L)
reduced <- rast(tif)
reduced <- setValues(reduced, matrix(c(NA, 2000, NA, 1, NA, 20), ncol = 3))
reduced_path <- file.path(directory, "population_loss.tif")
writeRaster(reduced, reduced_path)
error <- tryCatch(
  accept_grid(reduced_path, file.path(directory, "county.csv"), file.path(directory, "province.csv"), map,
              list(extent = c(100, 100.02, 30, 30.01), resolution = .01),
              list(province_max_rel = 1e-10, min_positive_counties = 1L,
                   county_p95_rel = 1e-6, county_max_rel = 1e-6), 2024L, layers),
  error = conditionMessage)
stopifnot(identical(error, "Grid readback does not conserve aligned county population"))
write_json(list(overlap_sum = TRUE, zero_population_mask = TRUE, two_level_readback = check$summary),
           file.path(directory, "cases.json"))
cat("HAND-CALCULATED CASES PASS\n")
