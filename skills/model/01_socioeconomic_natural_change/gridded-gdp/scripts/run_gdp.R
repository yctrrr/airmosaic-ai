# CLI for the gridded GDP skill. All intermediates and releases stay outside Git.
args <- commandArgs(trailingOnly = TRUE)
script <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
script_dir <- dirname(normalizePath(script, winslash = "/"))
repo <- normalizePath(file.path(script_dir, "../../../../.."), winslash = "/")
for (name in c("gdp_common.R", "grid_overlap_sum.R", "gdp_spatial.R")) source(file.path(script_dir, name))

normalize_observations <- function(path, county) {
  fields <- if (county) c("Sgnyea", "Prvcnm_id", "Ctnm_id", "Cmect07") else c("Sgnyea", "Prvcnm_id", "Gdp0116")
  tab <- read_table(path, fields)
  result <- data.table(Year = years_from(tab$Sgnyea), Province_code = key_clean(tab$Prvcnm_id))
  if (county) {
    result[, PAC := key_clean(tab$Ctnm_id)]
    result[, observed_gdp := numbers(tab$Cmect07, "Cmect07", missing = TRUE)]
    unique_keys(result, c("Year", "Province_code", "PAC"))
    result[!is.finite(observed_gdp) | observed_gdp <= 0, observed_gdp := NA_real_]
  } else {
    result[, benchmark_gdp_pc := numbers(tab$Gdp0116, "Gdp0116", missing = TRUE)]
    unique_keys(result, c("Year", "Province_code"))
  }
  result
}
read_history <- function(path, counties, years, tolerance) {
  columns <- c("PAC", "Province_code", features, "observed_gdp")
  history <- read_table(path, columns)
  history[, c("PAC", "Province_code") := lapply(.SD, key_clean), .SDcols = c("PAC", "Province_code")]
  history[, Year := years_from(Year)]
  for (field in setdiff(c(features, "observed_gdp"), "Year"))
    set(history, j = field, value = numbers(history[[field]], field))
  unique_keys(history, c("PAC", "Year"))
  validate_features(history)
  require_ok(all(history$observed_gdp > 0) && setequal(history$Year, years), "Invalid or incomplete historical panel")
  index <- match(history$PAC, counties$PAC)
  require_ok(!anyNA(index) && identical(history$Province_code, counties$Province_code[index]), "Historical county keys differ")
  xy <- sf::st_coordinates(suppressWarnings(sf::st_centroid(sf::st_geometry(counties))))
  require_ok(max(abs(c(history$cenlon - xy[index, 1], history$cenlat - xy[index, 2]))) <= tolerance,
             "Historical centroids differ from configured county boundary")
  history
}
paired_validate <- function(panel, recipe, historic_end, years, baseline, validation) {
  ids <- sort(unique(panel$PAC))
  set.seed(recipe$seed)
  withheld <- sample(ids, ceiling(length(ids) * validation$holdout_fraction))
  test <- panel[PAC %in% withheld & Year %in% years]
  updated_train <- panel[!PAC %in% withheld]
  legacy_train <- updated_train[Year <= historic_end]
  eligible <- legacy_train[, .N, by = PAC][N > validation$legacy_min_years, PAC]
  legacy_train <- legacy_train[PAC %in% eligible]
  require_ok(nrow(test) > 1L && setequal(test$Year, years) &&
               !any(test$PAC %in% updated_train$PAC) && !any(test$PAC %in% legacy_train$PAC),
             "Invalid county holdout")
  keys <- c("PAC", "Province_code", "Year", "observed_gdp")
  pair <- copy(test[, ..keys])
  pair[, c("old", "updated", "validation", "test_year") :=
         .(predict_gdp(fit_booster(legacy_train, recipe), test), predict_gdp(fit_booster(updated_train, recipe), test),
           "county_holdout", 0L)]
  old <- xgboost::xgb.load(baseline)
  result <- lapply(years, function(year) {
    test <- panel[Year == year]
    train <- panel[Year < year]
    require_ok(nrow(test) > 1L && max(train$Year) < year, "Invalid forward-year split")
    forward <- copy(test[, ..keys])
    forward[, c("old", "updated", "validation", "test_year") :=
              .(predict_gdp(old, test), predict_gdp(fit_booster(train, recipe), test), "forward_year", year)]
    forward
  })
  all_pairs <- rbindlist(c(list(pair), result))
  unique_keys(all_pairs, c("validation", "PAC", "Year"))
  metrics <- rbindlist(list(
    score_pair(all_pairs[, test_year := Year]),
    score_pair(all_pairs[, test_year := 0L])
  ))
  all_pairs[, test_year := fifelse(validation == "county_holdout", 0L, Year)]
  if (isTRUE(validation$require_nonworse)) {
    require_ok(all(metrics[test_year == 0L, new_log_rmse < old_log_rmse & new_median_ape < old_median_ape]), "Configured paired validation gate failed")
  }
  list(pair = all_pairs, metrics = metrics)
}

run <- function(config, action) {
  require_ok(action %in% c("preflight", "prepare", "panel", "validate", "fit", "grid", "accept"),
             "Unknown workflow stage")
  config <- normalizePath(config, winslash = "/", mustWork = TRUE)
  cfg <- read_json(config)
  synthetic <- identical(cfg$mode, "synthetic")
  require_ok(synthetic || identical(cfg$mode, "authorized"), "Explicit synthetic or authorized mode required")
  if (!synthetic) outside_repo(config, repo)
  root <- normalizePath(cfg$data_root, winslash = "/", mustWork = TRUE)
  for (path in c(root, cfg$work_root)) outside_repo(path, repo)
  require_ok(!is.null(cfg$work_root) && nzchar(cfg$work_root), "External work_root required")
  dir.create(cfg$work_root, recursive = TRUE, showWarnings = FALSE)
  out <- normalizePath(cfg$work_root, winslash = "/", mustWork = TRUE)
  require_ok(!startsWith(paste0(tolower(root), "/"), paste0(tolower(out), "/")) &&
               !startsWith(paste0(tolower(out), "/"), paste0(tolower(root), "/")),
             "Use separate data and work roots without nesting")
  annual_names <- names(cfg$annual)
  all_years <- sort(years_from(annual_names))
  append <- !is.null(cfg$accepted_model)
  require_ok(!append || action %in% c("preflight", "prepare", "grid", "accept"), "Append uses an accepted model")
  if (!synthetic && !append)
    require_ok(isTRUE(cfg$validation$require_nonworse), "Authorized model refresh requires the paired improvement gate")
  training <- sort(years_from(cfg$training_years))
  validation <- sort(years_from(cfg$validation_years))
  years <- sort(years_from(cfg$output_years))
  historic <- seq.int(cfg$history_first, cfg$history_last)
  require_ok(length(training) > 0L && length(validation) > 0L && length(years) > 0L &&
               !anyDuplicated(c(training, historic)) && !anyDuplicated(years) && !anyDuplicated(validation) &&
               all(training > max(historic)) && all((if (append) years else c(training, years)) %in% all_years) && all(validation %in% training),
             "Invalid study, training, validation or output years")
  provinces <- key_clean(cfg$province_codes)
  mainland <- as.character(c(11:15, 21:23, 31:37, 41:46, 50:54, 61:65) * 10000)
  require_ok(!anyDuplicated(provinces) && length(provinces) >= 1L, "Duplicate or absent province scope")
  if (!synthetic) require_ok(setequal(provinces, mainland) && identical(as.numeric(cfg$geo$resolution), .01) &&
                               identical(as.numeric(cfg$geo$county_resolution), .1) &&
                               identical(cfg$gdp_unit, "CNY/person current prices"), "China production scope or units differ")
  require_ok(cfg$history_first <= cfg$history_last && cfg$validation$holdout_fraction > 0 &&
               cfg$validation$holdout_fraction < 1 && cfg$validation$legacy_min_years >= 0 &&
               cfg$geo$centroid_tolerance >= 0 && all(is.finite(unlist(cfg$acceptance))) &&
               all(unlist(cfg$acceptance) >= 0) &&
               cfg$acceptance$county_p95_rel <= cfg$acceptance$county_max_rel &&
               cfg$acceptance$min_positive_counties >= 1, "Invalid validation settings")
  grid <- make_target(cfg$geo$extent, cfg$geo$resolution)
  require_ok(length(cfg$geo$county_resolution) == 1L && is.finite(cfg$geo$county_resolution) &&
               cfg$geo$county_resolution > 0 && min(diff(cfg$geo$extent[1:2]), diff(cfg$geo$extent[3:4])) >=
               cfg$geo$county_resolution, "Invalid county feature resolution")
  fields <- c("boundary", "county_gdp", "province_gdp", if (!append) c("history", "legacy_booster"))
  project_paths <- setNames(lapply(fields, function(field) resolve_input(root, cfg$inputs[[field]])), fields)
  for (path in project_paths) outside_repo(path, repo)
  map <- load_counties(project_paths$boundary, provinces, cfg$geo$extent)
  observations <- normalize_observations(project_paths$county_gdp, TRUE)
  benchmarks <- normalize_observations(project_paths$province_gdp, FALSE)
  benchmarks <- benchmarks[Province_code %in% provinces]
  keys <- as.data.table(sf::st_drop_geometry(map))[, .(PAC, Province_code)]
  same_counties <- observations[keys, on = .(PAC, Province_code), nomatch = 0L]
  unique_keys(same_counties, c("PAC", "Year"))
  source_audit <- observations[Year %in% unique(c(training, years)), .(rows = .N, invalid_or_missing = sum(is.na(observed_gdp))), by = Year]
  matched <- same_counties[, .(matched = .N, positive = sum(!is.na(observed_gdp))), by = Year]
  source_audit[matched, c("matched", "positive") := .(i.matched, i.positive), on = "Year"]
  require_ok(all((if (append) years else c(training, years)) %in% same_counties[!is.na(observed_gdp), unique(Year)]), "County GDP unavailable for required year")
  for (year in years) {
    province <- benchmarks[Year == year]
    require_ok(setequal(province$Province_code, provinces) && all(is.finite(province$benchmark_gdp_pc) &
                                                                  province$benchmark_gdp_pc > 0), "Incomplete positive province targets")
  }
  project_hash <- lapply(project_paths, file_hash)
  recipe <- read_json(file.path(script_dir, "../config/model.json"))
  if (synthetic) {
    recipe$rounds <- cfg$synthetic_rounds
    recipe$params$nthread <- 1L
    recipe$params$max_depth <- 3L
    recipe$params$alpha <- 0
    recipe$params$colsample_bylevel <- 1
  } else {
    require_ok(isTRUE(cfg$threads >= 1L && cfg$threads == as.integer(cfg$threads)), "Invalid thread budget")
    recipe$params$nthread <- cfg$threads
  }
  require_ok(identical(recipe$features, features) && recipe$rounds >= 1L, "Invalid model recipe")
  code <- lapply(c(file.path(script_dir, c("run_gdp.R", "gdp_common.R", "grid_overlap_sum.R", "gdp_spatial.R")),
                   file.path(script_dir, "../config/model.json")), file_hash)
  versions <- lapply(c("xgboost", "terra", "sf", "data.table", "exactextractr", "Matrix", "digest", "jsonlite"),
                     function(pkg) as.character(packageVersion(pkg)))
  runtime <- list(R = as.character(getRversion()), packages = versions, spatial = sf::sf_extSoftVersion())
  hashes <- new.env(parent = emptyenv())
  source_hash <- function(path) {
    if (!exists(path, hashes, inherits = FALSE)) assign(path, file_hash(path), hashes)
    get(path, hashes, inherits = FALSE)
  }
  required_years <- if (append) years else unique(c(training, years))
  input_paths <- lapply(required_years, function(year) {
    specification <- cfg$annual[[as.character(year)]]
    paths <- lapply(c("light", "population", "cover"), function(name) {
      spec <- specification[[name]]
      path <- resolve_input(root, spec$path)
      outside_repo(path, repo)
      require_ok(identical(source_hash(path), spec$sha256), paste("Annual input hash mismatch", year, name))
      require_ok(isTRUE(spec$year == year), paste("Annual input year mismatch", year, name))
      path
    })
    setNames(paths, c("light", "population", "cover"))
  })
  names(input_paths) <- as.character(required_years)
  if (append) {
    id <- cfg$accepted_model
    require_ok(is.character(id) && length(id) == 1L && grepl("^[0-9a-f]{64}$", id), "Expected accepted candidate ID")
    candidate_root <- if (is.null(cfg$accepted_model_root)) file.path(out, "candidates") else cfg$accepted_model_root
    outside_repo(candidate_root, repo)
    prior <- file.path(candidate_root, id)
    old_receipt <- read_json(file.path(prior, "receipt.json"))
    require_ok(identical(old_receipt$status, "accepted") && identical(old_receipt$mode, cfg$mode) &&
                 identical(old_receipt$boundary_sha256, project_hash$boundary) &&
                 identical(old_receipt$features, features) && identical(old_receipt$unit, cfg$gdp_unit) &&
                 old_receipt$training_first == min(historic) && old_receipt$training_last == max(training) &&
                 all(years > old_receipt$training_last) && all(years > max(old_receipt$years)) &&
                 isTRUE(all.equal(old_receipt$geo, cfg$geo)), "Accepted model is incompatible with the appended years or geometry")
    model_name <- old_receipt$model_file
    require_ok(length(model_name) == 1L && grepl("^Xgboost_GDP_model_[0-9]{4}-[0-9]{4}[.]json$", model_name),
               "Invalid accepted model filename")
    booster <- file.path(prior, release_folders[2], model_name)
    validation_metrics <- file.path(prior, "validation_metrics.csv")
    require_ok(identical(file_hash(booster), old_receipt$file_hashes[[paste0(release_folders[2], "/", model_name)]]) &&
                 identical(file_hash(validation_metrics), old_receipt$file_hashes[["validation_metrics.csv"]]),
               "Accepted model or validation metrics changed")
    if (!synthetic) {
      require_ok(identical(file_hash(file.path(prior, "receipt.json")), cfg$accepted_receipt_sha256),
                 "Provide the verified accepted model receipt checksum")
    }
    model_signature <- old_receipt$model_signature
    validation_signature <- old_receipt$validation_signature
  }
  if (action == "preflight") {
    for (year in names(input_paths)) {
      for (name in names(input_paths[[year]]))
        invisible(annual_layer(input_paths[[year]][[name]], name, cfg$annual[[year]][[name]],
                               grid, as.integer(year), synthetic))
    }
    if (!append) invisible(read_history(project_paths$history, map, historic, cfg$geo$centroid_tolerance))
    invisible(xgboost::xgb.load(if (append) booster else project_paths$legacy_booster))
    print(source_audit)
    cat("PREFLIGHT PASS\n")
    return(invisible(NULL))
  }

  cache <- file.path(out, "checkpoints")
  spatial_context <- list(code, runtime, cfg$mode, cfg$geo, project_hash$boundary, provinces)
  prepared <- lapply(names(input_paths), function(year) {
    spec <- cfg$annual[[year]]
    fingerprint <- lapply(spec, function(x) x[setdiff(names(x), "path")])
    checkpoint(cache, paste0("predictors-", year), list(spatial_context, fingerprint), function(path) {
      prepare_predictors(input_paths[[year]], spec, as.integer(year), map, cfg$geo, synthetic, path)
    })
  })
  names(prepared) <- names(input_paths)
  receipt_id <- function(path) basename(path)
  if (action == "prepare") return(invisible(NULL))
  read_features <- function(year) {
    fread(file.path(prepared[[as.character(year)]], "county_features.csv"),
          colClasses = list(character = c("PAC", "Province_code")))
  }
  if (!append) {
    panel_path <- checkpoint(cache, "panel",
                            list(code, runtime, project_hash[c("history", "boundary", "county_gdp")], training,
                                 historic, cfg$geo$centroid_tolerance, lapply(prepared[as.character(training)], receipt_id)),
                            function(path) {
      history <- read_history(project_paths$history, map, historic, cfg$geo$centroid_tolerance)
      updates <- rbindlist(lapply(training, read_features))
      seen <- same_counties[Year %in% training & !is.na(observed_gdp)]
      updates[seen, observed_gdp := i.observed_gdp, on = .(PAC, Province_code, Year)]
      panel <- rbindlist(list(history, updates[!is.na(observed_gdp), names(history), with = FALSE]))
      setorder(panel, Year, PAC)
      unique_keys(panel, c("PAC", "Year"))
      validate_features(panel)
      fwrite(panel, file.path(path, "county_gdp_model_panel.csv"))
      fwrite(panel[, .(observed_counties = .N), by = Year], file.path(path, "panel_counts.csv"))
    })
    if (action == "panel") return(invisible(NULL))
    panel <- fread(file.path(panel_path, "county_gdp_model_panel.csv"),
                   colClasses = list(character = c("PAC", "Province_code")))
    paired <- checkpoint(cache, "validation",
                         list(receipt_id(panel_path), project_hash$legacy_booster, recipe, validation, cfg$validation),
                         function(path) {
      pair <- paired_validate(panel, recipe, max(historic), validation, project_paths$legacy_booster, cfg$validation)
      fwrite(pair$pair, file.path(path, "paired_before_calibration.csv"))
      fwrite(pair$metrics, file.path(path, "validation_metrics.csv"))
    })
    if (action == "validate") return(invisible(NULL))
    model_path <- checkpoint(cache, "fit", list(receipt_id(paired), receipt_id(panel_path), recipe), function(path) {
      model <- fit_booster(panel, recipe)
      file <- file.path(path, "booster.json")
      xgboost::xgb.save(model, file)
      restored <- xgboost::xgb.load(file)
      check <- panel[seq_len(min(100L, nrow(panel)))]
      require_ok(isTRUE(all.equal(predict_gdp(model, check), predict_gdp(restored, check), tolerance = 1e-12)),
                 "Reloaded booster predictions differ")
      write_json(list(training_rows = nrow(panel), first_year = min(panel$Year), last_year = max(panel$Year),
                      rounds = recipe$rounds, reloaded = TRUE), file.path(path, "training.json"))
    })
    if (action == "fit") return(invisible(NULL))
    booster <- file.path(model_path, "booster.json")
    model_name <- sprintf("Xgboost_GDP_model_%d-%d.json", min(panel$Year), max(panel$Year))
    validation_metrics <- file.path(paired, "validation_metrics.csv")
    model_signature <- receipt_id(model_path)
    validation_signature <- receipt_id(paired)
  } else {
    cat("REUSED accepted_model\n")
  }
  model <- xgboost::xgb.load(booster)

  coverage_path <- checkpoint(cache, "coverage", spatial_context, function(path)
    saveRDS(county_coverage(rast(file.path(prepared[[1L]], "grid_predictors.tif"))[[1L]], map),
            file.path(path, "coverage.rds"), compress = FALSE))
  coverage <- readRDS(file.path(coverage_path, "coverage.rds"))
  reference <- function(year) {
    name <- as.character(year)
    if (is.null(cfg$reference_grids[[name]])) return(NULL)
    path <- resolve_input(root, cfg$reference_grids[[name]])
    outside_repo(path, repo)
    path
  }
  entries <- lapply(years, function(year) {
    names <- c(grid = sprintf("Grid_XGBoost_GDP_pc_0.01g_%d.tif", year),
               factors = sprintf("Grid_to_county_XGBoost_GDP_pc_%d.csv", year),
               county = sprintf("County_XGBoost_GDP_pc_%d.csv", year),
               province = sprintf("Province_GDP_pc_calibration_%d.csv", year))
    prepared_year <- prepared[[as.character(year)]]
    seen <- same_counties[Year == year & !is.na(observed_gdp), .(PAC, Province_code, observed_gdp)]
    province <- benchmarks[Year == year]
    setorder(seen, PAC)
    setorder(province, Province_code)
    stage <- checkpoint(cache, paste0("grid-", year),
                       list(receipt_id(prepared_year), receipt_id(coverage_path), model_signature, seen, province),
                       function(path) {
      calibrated <- calibrate_counties(read_features(year), seen, province, model)
      calibrated$province[, Year := year]
      fwrite(calibrated$county, file.path(path, names["county"]))
      fwrite(calibrated$province, file.path(path, names["province"]))
      layers <- rast(file.path(prepared_year, "grid_predictors.tif"))
      build_grid(layers, map, coverage, calibrated$county, model, year,
                 file.path(path, names["grid"]), file.path(path, names["factors"]))
    })
    if (action == "grid") return(invisible(NULL))
    reference_path <- reference(year)
    ref_hash <- if (is.null(reference_path)) NULL else source_hash(reference_path)
    accepted <- checkpoint(cache, paste0("accept-", year),
                           list(receipt_id(stage), cfg$acceptance, ref_hash), function(path) {
      population <- rast(file.path(prepared_year, "grid_predictors.tif"))[["Pop_all"]]
      checks <- accept_grid(file.path(stage, names["grid"]), file.path(stage, names["county"]),
                            file.path(stage, names["province"]), map, cfg$geo, cfg$acceptance, year,
                            population, reference_path)
      write_json(checks$summary, file.path(path, "acceptance.json"))
      fwrite(checks$readback, file.path(path, "county_readback.csv"))
    })
    list(year = year, paths = names, stage = stage, accepted = accepted)
  })
  if (action == "grid") return(invisible(NULL))
  candidate_deps <- list(code, cfg$mode, cfg$geo, cfg$gdp_unit, model_signature, project_hash$boundary,
                         project_hash[c("county_gdp", "province_gdp")],
                         lapply(entries, function(e) c(receipt_id(e$stage), receipt_id(e$accepted))))
  candidate <- file.path(out, "candidates", hash_object(candidate_deps))
  if (!dir.exists(candidate)) {
    dir.create(dirname(candidate), recursive = TRUE, showWarnings = FALSE)
    pending <- tempfile(".pending-", tmpdir = dirname(candidate))
    require_ok(dir.create(pending), "Cannot stage accepted candidate")
    on.exit(unlink(pending, recursive = TRUE), add = TRUE)
    for (folder in release_folders) dir.create(file.path(pending, folder))
    tables <- lapply(entries, function(entry) {
      destinations <- file.path(pending, release_folders[c(1, 1, 2, 2)], unname(entry$paths))
      require_ok(all(file.copy(file.path(entry$stage, entry$paths), destinations)), "Candidate copy failed")
      read_json(file.path(entry$accepted, "acceptance.json"))
    })
    fwrite(rbindlist(tables), file.path(pending, "grid_acceptance.csv"))
    require_ok(file.copy(validation_metrics, pending), "Cannot copy validation metrics")
    require_ok(file.copy(booster, file.path(pending, release_folders[2], model_name)),
               "Cannot copy model")
    files <- list.files(pending, recursive = TRUE)
    write_json(list(status = "accepted", mode = cfg$mode, years = years, unit = cfg$gdp_unit,
                    crs = "EPSG:4326", resolution = cfg$geo$resolution, boundary_sha256 = project_hash$boundary,
                    validation_signature = validation_signature, model_signature = model_signature,
                    model_file = model_name, features = features, geo = cfg$geo,
                    training_first = min(historic), training_last = max(training),
                    annual_signatures = setNames(lapply(entries, function(e) receipt_id(e$accepted)), years),
                    file_hashes = setNames(lapply(file.path(pending, files), file_hash), files)),
               file.path(pending, "receipt.json"))
    require_ok(file.rename(pending, candidate), "Cannot promote accepted candidate")
  }
  receipt <- read_json(file.path(candidate, "receipt.json"))
  require_ok(identical(receipt$status, "accepted") && identical(receipt$mode, cfg$mode), "Invalid candidate receipt")
  verify_files(candidate, receipt$file_hashes, recursive = TRUE)
  cat("ACCEPTED", candidate, "\n")
}

if (length(args) != 2L) stop("Usage: Rscript run_gdp.R config.json preflight|prepare|panel|validate|fit|grid|accept")
run(args[1L], args[2L])
