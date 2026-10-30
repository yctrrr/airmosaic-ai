ml_fit <- function(context) {
  evalq({
    state$current <- "fit"
    suppressPackageStartupMessages(library(mlr3learners))
    task <- mlr3::TaskRegr$new("configured_regression", backend = subsets$train[, c(features, cfg$target), drop = FALSE],
                               target = cfg$target)
    candidates <- c(list(list(id = "baseline", learner = "regr.featureless", parameters = list(robust = FALSE))), cfg$models)
    fitted <- list()
    comparison <- list()
    for (index in seq_along(candidates)) {
      specification <- candidates[[index]]
      if (!specification$learner %in% c("regr.featureless", "regr.rpart", "regr.ranger")) fail("unsupported_learner")
      parameters <- specification$parameters
      if (specification$learner == "regr.ranger") {
        if (is.null(parameters$num.trees)) parameters$num.trees <- 100L
        parameters$num.threads <- 1L
        parameters$seed <- (as.double(cfg$seeds$model) + index) %% 2147483000 + 1
      }
      if (specification$learner == "regr.rpart") parameters$xval <- 0L
      seed(100 + index)
      learner <- do.call(mlr3::lrn, c(list(specification$learner), parameters))
      learner$train(task$clone(deep = TRUE))
      prediction <- learner$predict_newdata(subsets$val[, features, drop = FALSE])$response
      score <- metrics(subsets$val[[cfg$target]], prediction)
      comparison[[index]] <- data.frame(model_id = specification$id, learner = specification$learner,
                                        val_rmse = score$rmse, val_mae = score$mae, val_r_squared = score$r_squared)
      fitted[[specification$id]] <- learner
    }
    comparison <- do.call(rbind, comparison)
    best <- which.min(comparison[[paste0("val_", cfg$selection_metric)]])
    selected_id <- comparison$model_id[[best]]
    selected <- fitted[[selected_id]]
    write_csv(comparison, "candidates")
    model <- list(schema_version = 1, learner = selected, preprocessing = preprocessing,
                   target = cfg$target, features = features, categorical_features = categorical,
                   selected_model_id = selected_id, configuration = cfg)
    saveRDS(model, artifact_path("model"), version = 3)
    finish_step("fitted")


  }, envir = context)
}
