# Bounded development-only ranger CV; source io.R first for metrics().
# The caller owns cohort definitions, splits, scientific categories and output I/O.
reproduction_integer <- function(x, lower, upper) {
  is.numeric(x) && length(x) == 1L && is.finite(x) && x == floor(x) && x >= lower && x <= upper
}

reproduction_validate_parameters <- function(parameters, feature_count) {
  if (!reproduction_integer(parameters$mtry, 1, feature_count) ||
      !reproduction_integer(parameters$min.node.size, 1, 100) ||
      !is.numeric(parameters$sample.fraction) || length(parameters$sample.fraction) != 1L ||
      !is.finite(parameters$sample.fraction) || parameters$sample.fraction < 0.1 ||
      parameters$sample.fraction > 1) stop("invalid_forest_parameters")
}

reproduction_validate <- function(frame, features, target, cfg, categorical_features) {
  if (!is.data.frame(frame) || nrow(frame) < 10L || nrow(frame) > 100000L ||
      anyDuplicated(names(frame)) || !is.character(features) || !length(features) ||
      length(features) > 64L || anyNA(features) || any(!nzchar(features)) || anyDuplicated(features) ||
      !is.character(target) || length(target) != 1L || is.na(target) || target %in% features ||
      !all(c(features, target) %in% names(frame)) || !is.character(categorical_features) ||
      anyNA(categorical_features) || anyDuplicated(categorical_features) ||
      !all(categorical_features %in% features)) stop("invalid_regression_columns")
  numeric_names <- setdiff(c(features, target), categorical_features)
  if (any(!vapply(frame[numeric_names], function(x) is.numeric(x) && all(is.finite(x)), logical(1))) ||
      any(!vapply(frame[categorical_features], function(x) (is.factor(x) || is.character(x)) &&
        !anyNA(x) && all(nzchar(as.character(x))), logical(1)))) stop("invalid_regression_values")
  nodes <- unlist(cfg$min_node_sizes, use.names = FALSE)
  fractions <- unlist(cfg$sample_fractions, use.names = FALSE)
  if (!reproduction_integer(cfg$num_trees, 1, 1000) ||
      !reproduction_integer(cfg$seed, 1, 2147450000) || !reproduction_integer(cfg$folds, 2, 10) ||
      !reproduction_integer(cfg$candidate_count, 1, 20) ||
      !length(nodes) || !all(vapply(as.list(nodes), reproduction_integer, logical(1), 1, 100)) ||
      !is.numeric(fractions) || !length(fractions) || any(!is.finite(fractions)) ||
      any(fractions < 0.1 | fractions > 1) ||
      cfg$candidate_count > length(features) * length(nodes) * length(fractions) ||
      !is.logical(cfg$replace) || length(cfg$replace) != 1L || is.na(cfg$replace) ||
      !identical(cfg$respect_unordered_factors, "partition")) stop("invalid_search_configuration")
}

reproduction_forest <- function(frame, features, target, parameters, cfg, model_seed, categorical_features = character(),
                                task_id = "regression_reproduction") {
  reproduction_validate(frame, features, target, cfg, categorical_features)
  reproduction_validate_parameters(parameters, length(features))
  if (!reproduction_integer(model_seed, 1, .Machine$integer.max)) stop("invalid_model_seed")
  for (name in categorical_features) {
    observed <- unique(as.character(frame[[name]]))
    vocabulary <- if (is.factor(frame[[name]])) levels(frame[[name]]) else sort(observed)
    vocabulary <- vocabulary[vocabulary %in% observed]
    if (!is.factor(frame[[name]]) || !identical(levels(frame[[name]]), vocabulary)) {
      frame[[name]] <- factor(as.character(frame[[name]]), levels = vocabulary,
                             ordered = is.ordered(frame[[name]]))
    }
  }
  learner <- mlr3::lrn("regr.ranger", num.trees = as.integer(cfg$num_trees),
    mtry = as.integer(parameters$mtry), min.node.size = as.integer(parameters$min.node.size),
    sample.fraction = parameters$sample.fraction, replace = cfg$replace,
    respect.unordered.factors = cfg$respect_unordered_factors,
    num.threads = 1L, seed = as.integer(model_seed), importance = "impurity")
  task <- mlr3::TaskRegr$new(task_id, frame[, c(features, target), drop = FALSE], target)
  learner$train(task)
  learner
}

reproduction_search_forest <- function(development, features, fold, cfg, model_index,
                                       categorical_features = character(),
                                       task_id = "regression_reproduction") {
  reproduction_validate(development, features, cfg$target, cfg, categorical_features)
  if (!reproduction_integer(model_index, 1, 1000) ||
      cfg$seed + 1000 * model_index + cfg$folds > .Machine$integer.max) stop("invalid_model_index")
  if (length(fold) != nrow(development) || anyNA(fold) ||
      !is.numeric(fold) || any(!is.finite(fold)) || any(fold != as.integer(fold)) ||
      !setequal(fold, seq_len(cfg$folds)) || any(table(fold) < 5L)) stop("invalid_folds")
  # No test frame is accepted by this function. The fixed grid is sampled once.
  grid <- expand.grid(mtry = seq_along(features), min.node.size = unlist(cfg$min_node_sizes),
                       sample.fraction = unlist(cfg$sample_fractions), KEEP.OUT.ATTRS = FALSE)
  set.seed(cfg$seed + 100L + model_index)
  grid <- grid[sample.int(nrow(grid), cfg$candidate_count), , drop = FALSE]
  grid$candidate_id <- seq_len(nrow(grid))
  records <- vector("list", nrow(grid))
  fold_records <- vector("list", nrow(grid))
  oof <- vector("list", nrow(grid))
  for (candidate in seq_len(nrow(grid))) {
    response <- rep(NA_real_, nrow(development))
    fold_rmse <- numeric(cfg$folds)
    for (k in seq_len(cfg$folds)) {
      training <- development[fold != k, , drop = FALSE]
      validation <- development[fold == k, , drop = FALSE]
      # Vocabulary is learned on this training fold; no held-out values or
      # outcomes may determine encoding. Explicit factor order is retained.
      for (name in categorical_features) {
        observed <- unique(as.character(training[[name]]))
        if (!all(as.character(validation[[name]]) %in% observed)) stop("unseen_fold_category")
        vocabulary <- if (is.factor(training[[name]])) levels(training[[name]]) else sort(observed)
        vocabulary <- vocabulary[vocabulary %in% observed]
        ordered <- is.ordered(training[[name]])
        training[[name]] <- factor(as.character(training[[name]]), levels = vocabulary, ordered = ordered)
        validation[[name]] <- factor(as.character(validation[[name]]), levels = vocabulary, ordered = ordered)
      }
      learner <- reproduction_forest(training, features, cfg$target, as.list(grid[candidate, ]), cfg,
                        cfg$seed + 1000L * model_index + k, categorical_features, task_id)
      response[fold == k] <- learner$predict_newdata(validation[, features, drop = FALSE])$response
      fold_rmse[k] <- metrics(validation[[cfg$target]], response[fold == k])$rmse
    }
    pooled <- metrics(development[[cfg$target]], response)
    records[[candidate]] <- data.frame(candidate_id = candidate, grid[candidate, c("mtry", "min.node.size", "sample.fraction")],
      mean_fold_rmse = mean(fold_rmse), sd_fold_rmse = stats::sd(fold_rmse),
      oof_rmse = pooled$rmse, oof_mae = pooled$mae, oof_r_squared = pooled$r_squared)
    fold_records[[candidate]] <- data.frame(candidate_id = candidate, fold = seq_len(cfg$folds), rmse = fold_rmse)
    oof[[candidate]] <- response
    cat(sprintf("CV model_%d candidate %d/%d completed\n", model_index, candidate, nrow(grid)))
    flush.console()
  }
  comparison <- do.call(rbind, records)
  selected <- which.min(comparison$mean_fold_rmse)
  list(comparison = comparison, fold_scores = do.call(rbind, fold_records),
       parameters = as.list(grid[selected, c("mtry", "min.node.size", "sample.fraction")]),
       candidate_id = selected, response = oof[[selected]])
}
