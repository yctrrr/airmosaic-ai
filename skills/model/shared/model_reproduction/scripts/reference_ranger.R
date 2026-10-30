# Reusable recovery from explicitly authorized, frozen ranger model objects.
# The caller owns path/hash checks and the minimal R launch environment.
# No original training code is sourced and no model is trained or modified.
reference_ranger_model <- function(object) {
  model <- if (inherits(object, "ranger")) object else object$model
  if (!inherits(model, "ranger") || !identical(model$treetype, "Regression") ||
      is.null(model$forest) || !length(model$forest$independent.variable.names)) {
    stop("unsupported_saved_regression_forest", call. = FALSE)
  }
  model
}

reference_ranger_predict <- function(model, frame) {
  features <- model$forest$independent.variable.names
  if (anyDuplicated(features) || anyDuplicated(names(frame)) ||
      !all(features %in% names(frame))) stop("saved_forest_feature_mismatch", call. = FALSE)
  values <- as.data.frame(frame[, features, drop = FALSE])
  vocabulary <- model$forest$covariate.levels
  for (name in intersect(names(vocabulary), features)) {
    levels <- vocabulary[[name]]
    if (is.null(levels) || !length(levels)) next
    if (anyNA(values[[name]]) || !all(as.character(values[[name]]) %in% levels)) {
      stop("saved_forest_unseen_category", call. = FALSE)
    }
    values[[name]] <- factor(as.character(values[[name]]), levels = levels)
  }
  if (anyNA(values) || any(vapply(values, function(x) is.numeric(x) && any(!is.finite(x)), logical(1)))) {
    stop("saved_forest_invalid_predictors", call. = FALSE)
  }
  response <- stats::predict(model, data = values, num.threads = 1L)$predictions
  if (length(response) != nrow(values) || any(!is.finite(response))) stop("invalid_saved_forest_predictions", call. = FALSE)
  as.numeric(response)
}

reference_ranger_metadata <- function(model) {
  # Do not export calls, environments, task objects, paths or user identities.
  selected <- c("num.trees", "mtry", "min.node.size", "splitrule", "replace", "num.samples", "importance.mode")
  list(parameters = model[intersect(selected, names(model))],
       features = as.list(model$forest$independent.variable.names),
       category_levels = model$forest$covariate.levels,
       split_encoding_is_ordered = as.list(model$forest$is.ordered),
       prediction_origin = "recovered_from_saved_model", training_performed = FALSE)
}
