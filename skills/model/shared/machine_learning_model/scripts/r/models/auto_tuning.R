# Development-only mlr3 automatic tuning. Sourcing defines functions only.
# The caller owns approved data access, spatial groups, final test and output I/O.
ml_tune_fail <- function(code) stop(code, call. = FALSE)

ml_tune_integer <- function(value, lower, upper) {
  is.numeric(value) && length(value) == 1L && !is.na(value) &&
    is.finite(value) && value == floor(value) && value >= lower && value <= upper
}

ml_tune_validate <- function(development, features, target, fold_id, group_id,
                             learner_id, search_bounds, fixed_parameters,
                             evaluations, max_model_fits, seed) {
  if (!is.data.frame(development) || nrow(development) < 4L ||
      nrow(development) > 100000L || anyDuplicated(names(development)) ||
      !is.character(features) || !length(features) || length(features) > 64L ||
      anyNA(features) || any(!nzchar(features)) || anyDuplicated(features) ||
      !is.character(target) || length(target) != 1L || is.na(target) ||
      target %in% features || !all(c(features, target) %in% names(development))) {
    ml_tune_fail("invalid_tuning_columns")
  }
  if (!all(vapply(development[c(features, target)], function(values) {
    is.numeric(values) && all(is.finite(values))
  }, logical(1)))) ml_tune_fail("tuning_requires_complete_numeric_values")
  n <- nrow(development)
  if (!is.numeric(fold_id) || length(fold_id) != n || anyNA(fold_id) ||
      any(!is.finite(fold_id)) || any(fold_id != floor(fold_id))) {
    ml_tune_fail("invalid_tuning_folds")
  }
  folds <- sort(unique(fold_id))
  if (length(folds) < 2L || length(folds) > 10L ||
      !identical(as.integer(folds), seq_along(folds))) ml_tune_fail("invalid_tuning_folds")
  if (!(is.character(group_id) || is.factor(group_id)) || length(group_id) != n ||
      anyNA(group_id) || any(!nzchar(trimws(as.character(group_id))))) {
    ml_tune_fail("invalid_tuning_groups")
  }
  if (any(vapply(split(fold_id, as.character(group_id)), function(values) {
    length(unique(values)) != 1L
  }, logical(1)))) ml_tune_fail("tuning_group_crosses_folds")
  if (any(vapply(folds, function(fold) sum(fold_id != fold) < 2L, logical(1)))) {
    ml_tune_fail("insufficient_tuning_training_rows")
  }
  if (!is.character(learner_id) || length(learner_id) != 1L ||
      !learner_id %in% c("regr.rpart", "regr.ranger")) ml_tune_fail("unsupported_tuning_learner")
  if (!is.list(search_bounds) || !length(search_bounds) || is.null(names(search_bounds)) ||
      anyNA(names(search_bounds)) || any(!nzchar(names(search_bounds))) ||
      anyDuplicated(names(search_bounds)) || !is.list(fixed_parameters) ||
      (length(fixed_parameters) && (is.null(names(fixed_parameters)) ||
        anyNA(names(fixed_parameters)) || any(!nzchar(names(fixed_parameters))) ||
        anyDuplicated(names(fixed_parameters)))) ||
      length(intersect(names(search_bounds), names(fixed_parameters)))) {
    ml_tune_fail("invalid_tuning_parameters")
  }
  domains <- if (learner_id == "regr.rpart") list(
    cp = c(0, 1, 0), maxdepth = c(1, 30, 1),
    minbucket = c(1, n, 1), minsplit = c(2, n, 1)
  ) else list(
    mtry = c(1, length(features), 1), min.node.size = c(1, n, 1),
    max.depth = c(1, 30, 1), num.trees = c(1, 512, 1),
    sample.fraction = c(0.1, 1, 0)
  )
  parameters <- c(names(search_bounds), names(fixed_parameters))
  if (any(!parameters %in% names(domains))) ml_tune_fail("unsupported_tuning_parameter")
  for (id in names(search_bounds)) {
    bound <- search_bounds[[id]]
    domain <- domains[[id]]
    if (!is.numeric(bound) || length(bound) != 2L || any(!is.finite(bound)) ||
        bound[[1L]] >= bound[[2L]] || bound[[1L]] < domain[[1L]] ||
        bound[[2L]] > domain[[2L]] ||
        (domain[[3L]] == 1 && any(bound != floor(bound)))) {
      ml_tune_fail("invalid_tuning_search_bounds")
    }
  }
  for (id in names(fixed_parameters)) {
    value <- fixed_parameters[[id]]
    domain <- domains[[id]]
    if (!is.numeric(value) || length(value) != 1L || !is.finite(value) ||
        value < domain[[1L]] || value > domain[[2L]] ||
        (domain[[3L]] == 1 && value != floor(value))) ml_tune_fail("invalid_tuning_fixed_parameter")
  }
  if (learner_id == "regr.ranger" && !"num.trees" %in% parameters) {
    ml_tune_fail("tuning_forest_tree_count_required")
  }
  if (!ml_tune_integer(evaluations, 1, 64) ||
      !ml_tune_integer(max_model_fits, 1, 641) ||
      !ml_tune_integer(seed, 1, 2147483000)) ml_tune_fail("invalid_tuning_budget_or_seed")
  fit_count <- evaluations * length(folds) + 1L
  if (fit_count > max_model_fits) ml_tune_fail("tuning_fit_budget_exceeded")
  list(folds = as.integer(folds), domains = domains, max_model_fits = fit_count)
}

ml_tune_packages <- function(learner_id) {
  c("mlr3", "mlr3tuning", "paradox", "future",
    if (learner_id == "regr.ranger") c("mlr3learners", "ranger") else "rpart")
}

ml_autotune_regression <- function(development, features, target, fold_id, group_id,
                                  learner_id, search_bounds, fixed_parameters,
                                  evaluations, max_model_fits, seed) {
  contract <- ml_tune_validate(development, features, target, fold_id, group_id,
    learner_id, search_bounds, fixed_parameters, evaluations, max_model_fits, seed)
  packages <- ml_tune_packages(learner_id)
  available <- vapply(packages, requireNamespace, logical(1), quietly = TRUE)
  if (!all(available)) ml_tune_fail("required_automatic_tuning_dependency_unavailable")
  if (future::nbrOfWorkers() != 1L) ml_tune_fail("tuning_requires_sequential_plan")
  task <- mlr3::TaskRegr$new("reviewed_development_tuning",
    backend = development[, c(features, target), drop = FALSE], target = target)
  resampling <- mlr3::rsmp("custom")
  train_sets <- lapply(contract$folds, function(fold) task$row_ids[fold_id != fold])
  test_sets <- lapply(contract$folds, function(fold) task$row_ids[fold_id == fold])
  resampling$instantiate(task, train_sets = train_sets, test_sets = test_sets)
  parameters <- fixed_parameters
  if (learner_id == "regr.ranger") {
    parameters$num.threads <- 1L
    parameters$seed <- as.integer(seed)
  } else parameters$xval <- 0L
  learner <- do.call(mlr3::lrn, c(list(learner_id), parameters))
  ranges <- lapply(names(search_bounds), function(id) {
    bounds <- search_bounds[[id]]
    constructor <- if (contract$domains[[id]][[3L]] == 1) paradox::p_int else paradox::p_dbl
    constructor(lower = bounds[[1L]], upper = bounds[[2L]])
  })
  names(ranges) <- names(search_bounds)
  space <- do.call(paradox::ps, ranges)
  set.seed(seed)
  tuned <- mlr3tuning::auto_tuner(
    tuner = mlr3tuning::tnr("random_search", batch_size = 1L),
    learner = learner, resampling = resampling, measure = mlr3::msr("regr.rmse"),
    search_space = space, term_evals = as.integer(evaluations),
    store_tuning_instance = TRUE, store_benchmark_result = FALSE,
    store_models = FALSE, check_values = TRUE)
  tryCatch(tuned$train(task), error = function(error) ml_tune_fail("automatic_tuning_failed"))
  archive <- as.data.frame(tuned$tuning_instance$archive$data)
  if (!"regr.rmse" %in% names(archive) || nrow(archive) < 1L ||
      nrow(archive) > evaluations || any(!is.finite(archive[["regr.rmse"]]))) {
    ml_tune_fail("invalid_or_incomplete_tuning_archive")
  }
  list(learner = tuned, selected_parameters = tuned$learner$param_set$values,
       archive = archive,
       fold_assignment = data.frame(row_id = task$row_ids, fold_id = fold_id,
                                    group_id = as.character(group_id)),
       budget = list(evaluations = evaluations, observed_evaluations = nrow(archive),
                     max_model_fits = contract$max_model_fits, threads = 1L),
       selection_metric = "mean_development_fold_rmse", final_test_used = FALSE,
       versions = vapply(packages, function(package) as.character(utils::packageVersion(package)), character(1)))
}
