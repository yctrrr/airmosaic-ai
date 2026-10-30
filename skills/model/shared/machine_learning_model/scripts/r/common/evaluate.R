ml_evaluate <- function(context) {
  evalq({
    state$current <- "evaluate"
    evaluation <- list(selected_model_id = selected_id, selection_metric = cfg$selection_metric,
                        training_scope = "train_only", test_used_for_selection = FALSE,
                        target_unit = if (is.null(cfg$target_unit)) "unspecified" else cfg$target_unit)
    predictions <- list()
    for (split in c("val", "test")) {
      response <- selected$predict_newdata(subsets[[split]][, features, drop = FALSE])$response
      baseline <- fitted$baseline$predict_newdata(subsets[[split]][, features, drop = FALSE])$response
      truth <- subsets[[split]][[cfg$target]]
      evaluation[[split]] <- metrics(truth, response)
      evaluation[[paste0("baseline_", split)]] <- metrics(truth, baseline)
      predictions[[split]] <- data.frame(sample_id = subsets[[split]][[cfg$id_column]], split = split,
                                         truth = truth, response = response, residual = truth - response)
    }
    reloaded <- readRDS(artifact_path("model"))
    repeated <- reloaded$learner$predict_newdata(subsets$test[, features, drop = FALSE])$response
    reload_equal <- isTRUE(all.equal(repeated, predictions$test$response, tolerance = 1e-12))
    if (!reload_equal) fail("reloaded_predictions_differ")
    write_csv(do.call(rbind, predictions), "predictions")
    write_json(evaluation, "metrics")
    finish_step("evaluated")


  }, envir = context)
}
