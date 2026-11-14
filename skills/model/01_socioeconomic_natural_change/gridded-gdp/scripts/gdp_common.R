# Shared schema, content-addressed checkpoints, and XGBoost helpers.
suppressPackageStartupMessages({
  library(data.table)
  library(terra)
})
setDTthreads(1L)

features <- c("Agriculture_grid", "Forest_grid", "Grassland_grid", "NTL_Pop",
              "Urban_grid", "Wetland_grid", "Year", "cenlat", "cenlon")
groups <- list(Agriculture_grid = c(10:12, 20, 30, 40),
               Forest_grid = c(50, 60:62, 70:72, 80:82, 90, 100, 160, 170),
               Grassland_grid = c(110, 130), Urban_grid = 190L, Wetland_grid = 180L)
lccs_codes <- c(unlist(groups), 120:122, 140, 150:153, 200:202, 210, 220)
release_folders <- c("Grid_interpolate_0.01g", "County_interpolate")

require_ok <- function(ok, message) {
  if (!isTRUE(ok)) stop(message, call. = FALSE)
}
file_hash <- function(path) digest::digest(path, algo = "sha256", file = TRUE)
check_county_source <- function(path) {
  type <- tolower(tools::file_ext(path))
  require_ok(type %in% c("rds", "gpkg"), "Use a self-contained sf RDS or single-layer GeoPackage for the county boundary")
  if (type == "gpkg") {
    require_ok(!any(file.exists(paste0(path, c("-wal", "-shm", "-journal")))),
               "Close active GeoPackage writers before using the county boundary")
    require_ok(nrow(sf::st_layers(path)) == 1L, "County GeoPackage must contain exactly one layer")
  }
}
hash_object <- function(object) digest::digest(object, algo = "sha256")
read_json <- function(path) jsonlite::read_json(path, simplifyVector = TRUE)
write_json <- function(value, path) jsonlite::write_json(value, path, auto_unbox = TRUE,
                                                        pretty = TRUE, digits = NA, na = "null")
read_table <- function(path, columns) {
  value <- withCallingHandlers(
    tryCatch(fread(path, select = columns, colClasses = "character", showProgress = FALSE),
             error = function(e) stop("Input CSV could not be read", call. = FALSE)),
    warning = function(w) stop("Input CSV parsing warning", call. = FALSE)
  )
  require_ok(all(columns %in% names(value)) && nrow(value) > 0L, "Missing CSV fields or rows")
  value
}
numbers <- function(values, label, missing = FALSE) {
  blank <- is.na(values) | !nzchar(trimws(values))
  parsed <- suppressWarnings(as.numeric(values))
  require_ok(all(is.finite(parsed) | (missing & blank)), paste("Invalid numeric field", label))
  parsed
}
years_from <- function(values) {
  year <- numbers(values, "year")
  require_ok(all(year == trunc(year) & year >= 1900 & year < 2200), "Invalid statistical year")
  as.integer(year)
}
key_clean <- function(values) {
  require_ok(all(!is.na(values) & grepl("^[0-9]{6}$", values)), "Expected six-character administrative codes")
  as.character(values)
}
unique_keys <- function(table, keys) require_ok(!anyDuplicated(table, by = keys), "Duplicate administrative-year key")
validate_features <- function(table) {
  require_ok(all(vapply(table[, ..features], function(x) all(is.finite(x)), logical(1))), "Nonfinite model features")
  ratios <- as.matrix(table[, names(groups), with = FALSE])
  require_ok(all(ratios >= 0 & ratios <= 1 + 1e-8) && all(rowSums(ratios) <= 1 + 1e-8) &&
               all(table$NTL_Pop >= 0 & abs(table$cenlon) <= 180 & abs(table$cenlat) <= 90), "Invalid feature range")
}
outside_repo <- function(path, repo) {
  parent <- path
  while (!dir.exists(parent) && !file.exists(parent)) {
    next_parent <- dirname(parent)
    require_ok(parent != next_parent, "External path needs a resolvable ancestor")
    parent <- next_parent
  }
  normalized <- tolower(normalizePath(parent, winslash = "/", mustWork = TRUE))
  require_ok(!startsWith(paste0(normalized, "/"), paste0(tolower(repo), "/")), "Use an external data or output directory")
}
resolve_input <- function(root, path) {
  require_ok(length(path) == 1L && is.character(path) && nzchar(path), "Missing configured input")
  if (!grepl("^(?:[A-Za-z]:[/\\\\]|/|\\\\\\\\)", path, perl = TRUE)) path <- file.path(root, path)
  require_ok(file.exists(path) && !dir.exists(path), "Required input file is unavailable")
  normalizePath(path, winslash = "/", mustWork = TRUE)
}
verify_files <- function(path, files, recursive = FALSE) {
  actual <- list.files(path, all.files = TRUE, no.. = TRUE, recursive = recursive)
  require_ok(setequal(actual, c(names(files), "receipt.json")), "Checkpoint file inventory changed")
  for (name in names(files)) {
    require_ok(identical(file_hash(file.path(path, name)), files[[name]]), "Checkpoint checksum mismatch")
  }
}
checkpoint <- function(cache, name, dependencies, task) {
  signature <- hash_object(dependencies)
  target <- file.path(cache, name, signature)
  if (dir.exists(target)) {
    receipt <- read_json(file.path(target, "receipt.json"))
    require_ok(identical(receipt$signature, signature), "Checkpoint signature mismatch")
    verify_files(target, receipt$files)
    cat("REUSED", name, "\n")
    return(target)
  }
  dir.create(dirname(target), recursive = TRUE, showWarnings = FALSE)
  pending <- tempfile(".pending-", tmpdir = dirname(target))
  require_ok(dir.create(pending), "Cannot create checkpoint staging directory")
  on.exit(unlink(pending, recursive = TRUE), add = TRUE)
  task(pending)
  files <- list.files(pending, all.files = TRUE, no.. = TRUE)
  require_ok(length(files) > 0L && !any(dir.exists(file.path(pending, files))), "Invalid checkpoint outputs")
  hashes <- setNames(lapply(file.path(pending, files), file_hash), files)
  write_json(list(signature = signature, files = hashes), file.path(pending, "receipt.json"))
  require_ok(file.rename(pending, target), "Checkpoint promotion failed")
  cat("COMPLETE", name, "\n")
  target
}

fit_booster <- function(rows, recipe) {
  require_ok(nrow(rows) >= 2 && all(rows$observed_gdp > 0), "No valid training rows")
  set.seed(recipe$seed)
  dm <- xgboost::xgb.DMatrix(as.matrix(rows[, ..features]), label = log(rows$observed_gdp),
                             nthread = recipe$params$nthread)
  xgboost::xgb.train(params = recipe$params, data = dm, nrounds = recipe$rounds, verbose = 0)
}
predict_gdp <- function(model, rows) {
  value <- exp(predict(model, as.matrix(rows[, ..features])))
  require_ok(all(is.finite(value) & value > 0), "Invalid GDP prediction")
  value
}
score_pair <- function(edges) {
  measure <- function(observed, predicted) {
    require_ok(all(is.finite(predicted) & predicted > 0), "Invalid paired prediction")
    y <- log(observed)
    error <- log(predicted) - y
    variance <- sum((y - mean(y))^2)
    require_ok(variance > 0, "Degenerate validation target")
    list(log_rmse = sqrt(mean(error^2)), log_r2 = 1 - sum(error^2) / variance,
         median_ape = median(abs(predicted / observed - 1)))
  }
  edges[, c(list(n = .N, counties = uniqueN(PAC)), setNames(measure(observed_gdp, old), c("old_log_rmse", "old_log_r2", "old_median_ape")),
            setNames(measure(observed_gdp, updated), c("new_log_rmse", "new_log_r2", "new_median_ape"))),
        by = .(validation, test_year)]
}
