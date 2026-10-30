# In-memory synthetic example only. No input files, downloads or model exports.
arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) > 1L || (length(arguments) && !identical(arguments, "--validate-only"))) {
  stop("unsupported_example_argument", call. = FALSE)
}
file_argument <- grep("^--file=", commandArgs(), value = TRUE)
if (length(file_argument) != 1L) stop("run_example_with_Rscript", call. = FALSE)
script_directory <- dirname(normalizePath(sub("^--file=", "", file_argument), mustWork = TRUE))
module <- new.env(parent = baseenv())
source(file.path(script_directory, "../../../../scripts/r/models/auto_tuning.R"), local = module)

set.seed(310)
development <- data.frame(x1 = rnorm(96), x2 = runif(96))
development$target <- sin(development$x1) + 2 * development$x2 + rnorm(96, sd = 0.15)
groups <- rep(sprintf("group_%02d", 1:24), each = 4)
folds <- rep(rep(1:3, length.out = 24), each = 4)
tree_arguments <- list(development = development, features = c("x1", "x2"), target = "target",
  fold_id = folds, group_id = groups, learner_id = "regr.rpart",
  search_bounds = list(cp = c(0.001, 0.05), minbucket = c(2, 8)),
  fixed_parameters = list(maxdepth = 6), evaluations = 4, max_model_fits = 13, seed = 310)
stopifnot(do.call(module$ml_tune_validate, tree_arguments)$max_model_fits == 13)
refuse <- function(changes, expected) {
  args <- tree_arguments
  args[names(changes)] <- changes
  message <- tryCatch({ do.call(module$ml_tune_validate, args); "no_error" },
                      error = function(error) conditionMessage(error))
  stopifnot(identical(message, expected))
}
refuse(list(fold_id = rep(1, 96)), "invalid_tuning_folds")
refuse(list(fold_id = rep(1:3, length.out = 96)), "tuning_group_crosses_folds")
refuse(list(features = c("x1", "target")), "invalid_tuning_columns")
bad <- development; bad$x1[[1]] <- NA_real_
refuse(list(development = bad), "tuning_requires_complete_numeric_values")
refuse(list(search_bounds = list(cp = c(-1, 0.2))), "invalid_tuning_search_bounds")
refuse(list(fixed_parameters = list(seed = 1)), "unsupported_tuning_parameter")
refuse(list(fixed_parameters = list(cp = 0.01)), "invalid_tuning_parameters")
refuse(list(max_model_fits = 12), "tuning_fit_budget_exceeded")
refuse(list(learner_id = "regr.ranger", search_bounds = list(mtry = c(1, 3)),
  fixed_parameters = list(num.trees = 32)), "invalid_tuning_search_bounds")
refuse(list(learner_id = "regr.ranger", search_bounds = list(mtry = c(1, 2)),
  fixed_parameters = list()), "tuning_forest_tree_count_required")
if (identical(arguments, "--validate-only")) {
  cat('{"status":"passed","scope":"base_r_contract_only","refusal_checks":10,"automatic_tuning_executed":false}\n')
  quit(status = 0L)
}
required <- unique(c(module$ml_tune_packages("regr.rpart"),
                     module$ml_tune_packages("regr.ranger")))
available <- vapply(required, requireNamespace, logical(1), quietly = TRUE)
if (!all(available)) {
  cat('{"status":"dependencies_unavailable","automatic_tuning_executed":false}\n')
  quit(status = 77L)
}
if (future::nbrOfWorkers() != 1L) stop("example_requires_sequential_plan", call. = FALSE)
# Every model is frozen before the holdout responses are constructed or scored.
tree <- do.call(module$ml_autotune_regression, tree_arguments)
forest_arguments <- tree_arguments
forest_arguments$learner_id <- "regr.ranger"
forest_arguments$search_bounds <- list(mtry = c(1, 2), min.node.size = c(2, 10),
                                      sample.fraction = c(0.5, 0.9))
forest_arguments$fixed_parameters <- list(num.trees = 32, max.depth = 6)
forest <- do.call(module$ml_autotune_regression, forest_arguments)
task <- mlr3::TaskRegr$new("synthetic_development", development, target = "target")
baseline <- mlr3::lrn("regr.featureless", robust = FALSE); baseline$train(task)
linear <- mlr3::lrn("regr.lm"); linear$train(task)
frozen <- list(baseline = baseline, linear = linear, tree = tree$learner, forest = forest$learner)
set.seed(311)
heldout <- data.frame(x1 = rnorm(24), x2 = runif(24))
truth <- sin(heldout$x1) + 2 * heldout$x2 + rnorm(24, sd = 0.15)
predictions <- lapply(frozen, function(learner) learner$predict_newdata(heldout)$response)
stopifnot(all(vapply(predictions, function(value) length(value) == 24L && all(is.finite(value)), logical(1))))
score <- function(predicted) {
  error <- predicted - truth
  c(rmse = sqrt(mean(error^2)), mae = mean(abs(error)),
    r_squared = 1 - sum(error^2) / sum((truth - mean(truth))^2))
}
scores <- lapply(predictions, score)
stopifnot(all(vapply(scores, function(values) all(is.finite(values)), logical(1))))
for (id in names(frozen)) {
  restored <- unserialize(serialize(frozen[[id]], NULL))
  stopifnot(isTRUE(all.equal(restored$predict_newdata(heldout)$response, predictions[[id]], tolerance = 1e-12)))
}
repeat_tree <- do.call(module$ml_autotune_regression, tree_arguments)
stopifnot(isTRUE(all.equal(repeat_tree$selected_parameters, tree$selected_parameters)),
  isTRUE(all.equal(repeat_tree$learner$predict_newdata(heldout)$response, predictions$tree)),
  !tree$final_test_used, !forest$final_test_used,
  nrow(tree$archive) <= 4L, nrow(forest$archive) <= 4L)
for (id in names(scores)) {
  values <- scores[[id]]
  cat(sprintf('{"model":"%s","test_rmse":%.10g,"test_mae":%.10g,"test_r_squared":%.10g}\n',
              id, values[["rmse"]], values[["mae"]], values[["r_squared"]]))
}
cat('{"status":"passed","scope":"in_memory_synthetic_tuning_and_holdout","refusal_checks":10,"models":4,"holdout_rows":24,"automatic_tuning_executed":true,"replay_and_serialization_checked":true}\n')
