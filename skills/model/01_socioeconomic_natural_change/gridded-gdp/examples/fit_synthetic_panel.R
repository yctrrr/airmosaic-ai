# Show the GDP model fit directly in R on the completed synthetic panel.
# Run from the repository root: Rscript --vanilla <this-script> <resolved-config> <new-external-directory>
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Pass a resolved synthetic configuration and a fresh external output directory.")
repo <- normalizePath(".", winslash = "/", mustWork = TRUE)
recipe_path <- file.path(repo, "skills/model/01_socioeconomic_natural_change/gridded-gdp/config/model.json")
if (!file.exists(recipe_path)) stop("Run from the repository root.")
read_json <- function(path) jsonlite::read_json(path, simplifyVector = TRUE)
config <- normalizePath(args[1], winslash = "/", mustWork = TRUE)
cfg <- read_json(config)
if (!identical(cfg$mode, "synthetic")) stop("Use a resolved synthetic configuration.")
work <- normalizePath(cfg$work_root, winslash = "/", mustWork = TRUE)
parent <- normalizePath(dirname(args[2]), winslash = "/", mustWork = TRUE)
output <- file.path(parent, basename(args[2]))
contains <- function(root, path) startsWith(paste0(tolower(path), "/"), paste0(tolower(root), "/"))
if (contains(repo, output) || contains(work, output) || file.exists(output))
  stop("Choose a fresh external output directory outside the GDP work root.")

# Retain the exact order and base parameters from the workflow's recipe.
recipe <- read_json(recipe_path)
feature_names <- recipe$features
params <- recipe$params
params$nthread <- 1L
params$max_depth <- 3L
params$alpha <- 0
params$colsample_bylevel <- 1
rounds <- cfg$synthetic_rounds

panels <- list.files(file.path(work, "checkpoints/panel"), "^county_gdp_model_panel[.]csv$",
                     full.names = TRUE, recursive = TRUE)
if (length(panels) != 1L) stop("Expected one panel. Use the dedicated synthetic demo run.")
columns <- c("PAC", "Province_code", feature_names, "observed_gdp")
panel <- data.table::fread(panels[1], select = columns,
                         colClasses = list(character = c("PAC", "Province_code")))
stopifnot(!anyDuplicated(panel, by = c("PAC", "Year")),
          all(is.finite(panel$observed_gdp) & panel$observed_gdp > 0))
feature_matrix <- function(rows) as.matrix(rows[, feature_names, with = FALSE])
stopifnot(all(is.finite(feature_matrix(panel))))

# This is the model fit. GDP is on the log scale in the training loss.
fit_model <- function(rows) {
  set.seed(recipe$seed)
  training_data <- xgboost::xgb.DMatrix(feature_matrix(rows), label = log(rows$observed_gdp), nthread = 1L)
  xgboost::xgb.train(params = params, data = training_data, nrounds = rounds, verbose = 0)
}
predict_gdp <- function(model, x) {
  value <- exp(predict(model, x))
  stopifnot(all(is.finite(value) & value > 0))
  value
}

# Last forward year. Both models predict the same held-out county-year rows.
test_year <- max(cfg$validation_years)
history <- panel[Year < test_year]
test <- panel[Year == test_year]
stopifnot(nrow(history) >= 2L, nrow(test) >= 2L, max(history$Year) < test_year)
x_test <- feature_matrix(test)
old <- xgboost::xgb.load(file.path(cfg$data_root, cfg$inputs$legacy_booster))
forward <- fit_model(history)
pairs <- test[, .(PAC, Province_code, Year, observed_gdp)]
pairs[, legacy_gdp := predict_gdp(old, x_test)]
pairs[, updated_gdp := predict_gdp(forward, x_test)]
log_observed <- log(pairs$observed_gdp)
variance <- sum((log_observed - mean(log_observed))^2)
stopifnot(variance > 0)
score <- function(name, prediction) {
  error <- log(prediction) - log_observed
  data.table::data.table(model = name, test_year = test_year, n = length(prediction),
    log_rmse = sqrt(mean(error^2)), log_r2 = 1 - sum(error^2) / variance,
    median_ape = median(abs(prediction / pairs$observed_gdp - 1)))
}
metrics <- data.table::rbindlist(list(score("legacy", pairs$legacy_gdp), score("updated", pairs$updated_gdp)))

# Fit the full synthetic panel and check reload independently of the forward-year metrics.
final <- fit_model(panel)
if (!dir.create(output)) stop("Cannot create the output directory.")
model_path <- file.path(output, "gdp-booster.json")
xgboost::xgb.save(final, model_path)
restored <- xgboost::xgb.load(model_path)
probe <- feature_matrix(panel[seq_len(min(100L, nrow(panel)))])
stopifnot(isTRUE(all.equal(predict_gdp(final, probe), predict_gdp(restored, probe), tolerance = 1e-12)))
data.table::fwrite(pairs, file.path(output, "forward-predictions.csv"))
data.table::fwrite(metrics, file.path(output, "forward-metrics.csv"))
jsonlite::write_json(list(mode = "synthetic", rows = nrow(panel), features = feature_names,
  first_year = min(panel$Year), last_year = max(panel$Year), rounds = rounds,
  forward_training_last = max(history$Year), forward_test_year = test_year, reloaded = TRUE),
  file.path(output, "fit-summary.json"), auto_unbox = TRUE, pretty = TRUE)
print(metrics)
cat("Saved to", output, "\n")
