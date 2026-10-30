# Study-specific orchestration; not an additional registered run-tool adapter.
# Shared regression skill supplies the metric and bounded CV contracts. No original case code is used.
source(Sys.getenv("AIRMOSAIC_SKILL_IO"), local = TRUE)
source(Sys.getenv("AIRMOSAIC_REPRODUCTION_LIB"), local = TRUE)
suppressPackageStartupMessages(library(mlr3learners))

prepare_cohort <- function(raw, cfg) {
  features <- unique(unlist(cfg$feature_sets, use.names = FALSE))
  required <- unique(c(cfg$id_column, cfg$target, cfg$split_column,
                       cfg$country_column, cfg$climate_column, features))
  if (anyDuplicated(names(raw)) || !all(required %in% names(raw))) stop("invalid_columns")
  ids <- raw[[cfg$id_column]]
  if (anyNA(ids) || any(!nzchar(trimws(ids))) || anyDuplicated(ids)) stop("invalid_station_keys")
  labels <- c(unlist(cfg$development_labels), cfg$test_label)
  if (anyNA(raw[[cfg$split_column]]) || !all(raw[[cfg$split_column]] %in% labels)) stop("unknown_split")
  country <- raw[[cfg$country_column]]
  if (anyNA(country) || any(!nzchar(trimws(country)))) stop("missing_country")
  counts <- table(country)
  retain_country <- as.integer(counts[country]) > cfg$minimum_country_count_exclusive
  rows <- raw[retain_country, required, drop = FALSE]
  climate <- sub("^.*_", "", rows[[cfg$climate_column]])
  known <- !is.na(climate) & climate %in% unlist(cfg$climate_levels)
  climate_excluded <- sum(!known)
  rows <- rows[known, , drop = FALSE]
  rows[[cfg$climate_column]] <- factor(climate[known], levels = unlist(cfg$climate_levels))
  for (name in setdiff(c(features, cfg$target), cfg$climate_column)) {
    source_values <- rows[[name]]
    values <- suppressWarnings(as.numeric(source_values))
    blank <- is.na(source_values) | !nzchar(trimws(source_values))
    if (any(!blank & is.na(values))) stop("invalid_numeric_column")
    values[values %in% unlist(cfg$missing_sentinels)] <- NA_real_
    if (any(!is.na(values) & !is.finite(values))) stop("nonfinite_input")
    rows[[name]] <- values
  }
  complete <- stats::complete.cases(rows[, c(features, cfg$target), drop = FALSE])
  missing_excluded <- sum(!complete)
  rows <- rows[complete, , drop = FALSE]
  # Stable station order is independent of outcomes and original CSV ordering.
  rows <- rows[order(rows[[cfg$id_column]], method = "radix"), , drop = FALSE]
  rows$study_split <- ifelse(rows[[cfg$split_column]] %in% unlist(cfg$development_labels), "development", "test")
  development <- rows[rows$study_split == "development", , drop = FALSE]
  test <- rows[rows$study_split == "test", , drop = FALSE]
  if (nrow(development) != cfg$expected_counts$development || nrow(test) != cfg$expected_counts$test) stop("cohort_count_mismatch")
  if (length(intersect(development[[cfg$id_column]], test[[cfg$id_column]]))) stop("overlapping_stations")
  list(development = development, test = test, prepared = rows,
       audit = list(source_rows = nrow(raw), country_excluded = sum(!retain_country),
                    climate_excluded = climate_excluded, missing_excluded = missing_excluded,
                    development = nrow(development), test = nrow(test)))
}

# Study compatibility defaults are kept here, outside the reusable engine.
forest <- function(frame, features, target, parameters, cfg, model_seed) {
  categorical <- if (is.null(cfg$categorical_features)) cfg$climate_column else as.character(unlist(cfg$categorical_features, use.names = FALSE))
  reproduction_forest(frame, features, target, parameters, cfg, model_seed, categorical)
}

search_forest <- function(development, features, fold, cfg, model_index) {
  categorical <- if (is.null(cfg$categorical_features)) cfg$climate_column else as.character(unlist(cfg$categorical_features, use.names = FALSE))
  reproduction_search_forest(development, features, fold, cfg, model_index, categorical)
}

main <- function() {
  args <- commandArgs(TRUE)
  if (length(args) != 6L || !identical(args[c(1, 3, 5)], c("--input-csv", "--protocol", "--out-dir"))) stop("invalid_arguments")
  cfg <- jsonlite::fromJSON(args[[4]], simplifyVector = FALSE)
  output <- args[[6]]
  save_json <- function(value, name) {
    path <- file.path(output, name)
    if (file.exists(path)) stop("output_exists")
    jsonlite::write_json(value, path, auto_unbox = TRUE, pretty = TRUE, digits = 16, na = "null")
  }
  save_csv <- function(value, name) {
    path <- file.path(output, name)
    if (file.exists(path)) stop("output_exists")
    utils::write.csv(value, path, row.names = FALSE, fileEncoding = "UTF-8")
  }
  # One raw read per process; frames are shared by both models and all folds.
  raw <- utils::read.csv(args[[2]], check.names = FALSE, colClasses = "character", na.strings = "", nrows = 100001L)
  if (nrow(raw) > 100000L) stop("input_too_large")
  cohort <- prepare_cohort(raw, cfg)
  development <- cohort$development
  test <- cohort$test
  save_json(cohort$audit, "cohort.json")
  save_csv(cohort$prepared, "prepared_cohort.csv")
  set.seed(cfg$seed)
  fold <- sample(rep(seq_len(cfg$folds), length.out = nrow(development)))
  save_csv(data.frame(sample_id = development[[cfg$id_column]], fold = fold), "development_folds.csv")
  fold_means <- vapply(seq_len(cfg$folds), function(k) mean(development[[cfg$target]][fold != k]), numeric(1))
  baseline_oof <- fold_means[fold]
  searches <- list()
  selections <- list()
  for (index in seq_along(cfg$feature_sets)) {
    name <- names(cfg$feature_sets)[index]
    features <- unlist(cfg$feature_sets[[name]])
    searches[[name]] <- search_forest(development, features, fold, cfg, index)
    save_csv(searches[[name]]$comparison, paste0(name, "_candidates.csv"))
    save_csv(searches[[name]]$fold_scores, paste0(name, "_fold_scores.csv"))
    selections[[name]] <- list(features = as.list(features), parameters = searches[[name]]$parameters,
                              candidate_id = searches[[name]]$candidate_id)
  }
  # Freeze both models' choices before any final fit or test prediction.
  save_json(list(selection_metric = cfg$selection_metric, models = selections,
                 test_used_for_selection = FALSE), "selected_models.json")
  save_csv(data.frame(sample_id = development[[cfg$id_column]], truth = development[[cfg$target]],
                      baseline = baseline_oof, model_1 = searches$model_1$response,
                      model_2 = searches$model_2$response), "development_oof_predictions.csv")
  baseline_test <- rep(mean(development[[cfg$target]]), nrow(test))
  predictions <- data.frame(sample_id = test[[cfg$id_column]], truth = test[[cfg$target]], baseline = baseline_test)
  scores <- list(baseline = list(development_oof = metrics(development[[cfg$target]], baseline_oof),
                                 test = metrics(test[[cfg$target]], baseline_test)))
  reload_checks <- list()
  grDevices::png(file.path(output, "prediction_validation.png"), width = 1500, height = 720, res = 125)
  graphics::par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3, 1))
  for (index in seq_along(cfg$feature_sets)) {
    name <- names(cfg$feature_sets)[index]
    features <- unlist(cfg$feature_sets[[name]])
    learner <- forest(development, features, cfg$target, searches[[name]]$parameters, cfg,
                       cfg$seed + 10000L + index)
    response <- learner$predict_newdata(test[, features, drop = FALSE])$response
    predictions[[name]] <- response
    scores[[name]] <- list(development_oof = metrics(development[[cfg$target]], searches[[name]]$response),
                            test = metrics(test[[cfg$target]], response))
    model_path <- file.path(output, paste0(name, ".rds"))
    saveRDS(list(learner = learner, features = features, target = cfg$target,
                 climate_levels = cfg$climate_levels, protocol = cfg), model_path, version = 3)
    repeated <- readRDS(model_path)$learner$predict_newdata(test[, features, drop = FALSE])$response
    reload_checks[[name]] <- isTRUE(all.equal(response, repeated, tolerance = 1e-12))
    if (!reload_checks[[name]]) stop("reloaded_predictions_differ")
    importance <- learner$importance()
    save_csv(data.frame(feature = names(importance), impurity_importance = as.numeric(importance)), paste0(name, "_importance.csv"))
    limits <- range(test[[cfg$target]], response)
    graphics::plot(test[[cfg$target]], response, xlim = limits, ylim = limits, pch = 16,
      col = grDevices::adjustcolor("#336699", alpha.f = 0.35), xlab = "Observed ozone (ppb)",
      ylab = "Predicted ozone (ppb)", main = paste(name, "-", length(features), "predictors"))
    graphics::abline(0, 1, col = "#B44747", lty = 2, lwd = 2)
    graphics::legend("topleft", legend = sprintf("n = %d\nRMSE = %.3f ppb\nR-squared = %.3f", nrow(test), scores[[name]]$test$rmse, scores[[name]]$test$r_squared), bty = "n")
  }
  grDevices::dev.off()
  save_csv(predictions, "test_predictions.csv")
  save_json(list(target = cfg$target, unit = cfg$target_unit, metrics = scores,
    r_squared_definition = "1 - sum((truth - prediction)^2) / sum((truth - mean(truth))^2)",
    oof_scope = "development scores after hyperparameter selection; not an unbiased final estimate",
    final_training_scope = "all_development", test_used_for_selection = FALSE), "metrics.json")
  packages <- sort(loadedNamespaces())
  versions <- as.list(stats::setNames(vapply(packages, function(p) as.character(utils::packageVersion(p)), character(1)), packages))
  save_json(list(status = "completed", R = as.character(getRversion()), packages = versions,
    threads = 1, seed = cfg$seed, folds = cfg$folds, candidates_per_model = cfg$candidate_count,
    reload_predictions_equal = reload_checks, scientific_review = "pending",
    original_code_result_comparison = "awaiting_user_materials"), "reproducibility.json")
  cat("EXPERIMENT completed\n")
}

if (!identical(Sys.getenv("AIRMOSAIC_PROJECT_SELF_TEST"), "1")) main()
