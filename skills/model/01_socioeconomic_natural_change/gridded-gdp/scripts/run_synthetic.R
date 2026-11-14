# Generate an invented country fragment, with one boundary crossing target cells.
args <- commandArgs(TRUE)
stopifnot(length(args) == 1L)
script_dir <- dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))))
source(file.path(script_dir, "gdp_common.R"))
repo <- normalizePath(file.path(script_dir, "../../../../.."), winslash = "/")
root <- args[1L]
outside_repo(root, repo)
require_ok(!file.exists(root) && !dir.exists(root), "Use a new synthetic directory")
stopifnot(dir.create(root, recursive = TRUE))
root <- normalizePath(root, winslash = "/")
data <- file.path(root, "inputs")
dir.create(data)
bounds <- c(100, 100.4, 30, 30.2)
pacs <- c("110001", "110002", "110003", "120001", "120002", "120003", "120004", "120005")
provinces <- c(rep("110000", 3), rep("120000", 5))
shape <- function(left, right, bottom, top)
  sf::st_polygon(list(rbind(c(left, bottom), c(right, bottom), c(right, top), c(left, top), c(left, bottom))))
x <- c(100, 100.095, 100.2, 100.3, 100.4)
polygons <- lapply(seq_along(pacs), function(i) {
  j <- (i - 1L) %% 4L + 1L
  bottom <- if (i <= 4L) 30.0 else 30.1
  shape(x[j], x[j + 1L], bottom, bottom + .1)
})
counties <- sf::st_sf(PAC = pacs, Province_code = provinces, geometry = sf::st_sfc(polygons, crs = 4326))
saveRDS(counties, file.path(data, "counties.rds"))
centers <- sf::st_coordinates(suppressWarnings(sf::st_centroid(sf::st_geometry(counties))))
past <- rbindlist(lapply(2000:2020, function(year) {
  ordinal <- seq_along(pacs)
  data.table(PAC = pacs, Province_code = provinces, Agriculture_grid = ordinal / 20,
             Forest_grid = .12, Grassland_grid = .1, NTL_Pop = (ordinal + year - 2000) / 40,
             Urban_grid = .15, Wetland_grid = .07, Year = year,
             cenlat = centers[, 2], cenlon = centers[, 1],
             observed_gdp = 4500 + 240 * ordinal + 95 * (year - 2000))
}))
fwrite(past, file.path(data, "history.csv"))
recipe <- read_json(file.path(script_dir, "../config/model.json"))
recipe$rounds <- 12L
recipe$params$max_depth <- 3L
recipe$params$alpha <- 0
recipe$params$colsample_bylevel <- 1
xgboost::xgb.save(fit_booster(past, recipe), file.path(data, "legacy.json"))
years <- 2021:2023
fwrite(rbindlist(lapply(years, function(year) {
  records <- data.table(Sgnyea = year, Prvcnm_id = provinces, Ctnm_id = pacs,
                        Cmect07 = 6200 + 120 * seq_along(pacs) + (year - 2020) * 120)
  records[8L, Cmect07 := NA_real_]
  records
})), file.path(data, "county.csv"))
fwrite(rbindlist(lapply(years, function(year)
  data.table(Sgnyea = year, Prvcnm_id = unique(provinces), Gdp0116 = c(7200, 7900) + 100 * (year - 2021)))),
  file.path(data, "province.csv"))
annual <- setNames(lapply(years, function(year) {
  specification <- list()
  template <- rast(nrows = 40, ncols = 80, xmin = bounds[1], xmax = bounds[2],
                   ymin = bounds[3], ymax = bounds[4], crs = "EPSG:4326")
  idx <- seq_len(ncell(template))
  datasets <- list(light = 5 + (idx + year) %% 29, population = 30 + idx %% 23,
                   cover = rep(c(10, 50, 110, 190, 180, 200, 210, 0), length.out = length(idx)))
  for (name in names(datasets)) {
    path <- paste0(name, "-", year, ".tif")
    layer <- setValues(rast(template), datasets[[name]])
    names(layer) <- name
    writeRaster(layer, file.path(data, path))
    specification[[name]] <- list(path = path, year = year, version = "invented-1", product = "synthetic",
                                  sha256 = file_hash(file.path(data, path)))
  }
  specification
}), as.character(years))
cfg <- list(mode = "synthetic", data_root = data, work_root = file.path(root, "work"),
            release_root = file.path(root, "releases"),
            inputs = list(boundary = "counties.rds", history = "history.csv", county_gdp = "county.csv",
                          province_gdp = "province.csv", legacy_booster = "legacy.json"),
            history_first = 2000L, history_last = 2020L, synthetic_rounds = 12L,
            training_years = c(2021L, 2022L), validation_years = c(2021L, 2022L), output_years = 2022L,
            annual = annual, province_codes = unique(provinces), gdp_unit = "synthetic CNY/person",
            geo = list(extent = bounds, resolution = .01, county_resolution = .1, centroid_tolerance = 1e-8),
            validation = list(holdout_fraction = .25, legacy_min_years = 10L, require_nonworse = FALSE),
            acceptance = list(province_max_rel = 1e-10, county_p95_rel = .01, county_max_rel = .015, min_positive_counties = 8L))
if (identical(Sys.getenv("AIRMOSAIC_GDP_FIXTURE_ARCHIVE"), "1")) {
  # The workflow controller packages these TIFFs with the same source metadata
  # contract as Dataverse before the intake step.
  for (year in names(cfg$annual)) {
    cfg$annual[[year]]$light$provider <- "dataverse"
    cfg$annual[[year]]$light$fixture_source <- cfg$annual[[year]]$light$path
    cfg$annual[[year]]$light$path <- NULL
    cfg$annual[[year]]$light$version <- "1.0"
    cfg$annual[[year]]$light$fixture_catalog <- "fixture-catalog.json"
  }
}
write_json(cfg, file.path(root, "initial.json"))
cfg$output_years <- 2023L
write_json(cfg, file.path(root, "increment.json"))
cfg$output_years <- 2022L
cfg$acceptance$county_max_rel <- 1e-20
cfg$acceptance$county_p95_rel <- 1e-20
write_json(cfg, file.path(root, "reject.json"))
cfg$output_years <- 2023L
cfg$annual[["2023"]]$population$year <- 2022L
write_json(cfg, file.path(root, "wrong-year.json"))
