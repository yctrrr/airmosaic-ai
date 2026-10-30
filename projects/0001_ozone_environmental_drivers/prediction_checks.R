# Synthetic checks run before the independent real-data experiment.
Sys.setenv(AIRMOSAIC_PROJECT_SELF_TEST = "1")
base <- dirname(Sys.getenv("AIRMOSAIC_R_ENTRYPOINT"))
source(file.path(base, "prediction.R"), local = TRUE)
cfg <- jsonlite::fromJSON(file.path(base, "prediction.json"), simplifyVector = FALSE)
cfg$feature_sets <- list(model_1 = list("climatic_zone", "alt", "population_density"),
                         model_2 = list("climatic_zone", "alt"))
cfg$expected_counts <- list(development = 89L, test = 30L)
cfg$candidate_count <- 2L
cfg$num_trees <- 8L
cfg$folds <- 3L
set.seed(1)
raw <- data.frame(id = sprintf("station_%03d", seq_len(125)),
  o3_average_values = as.character(seq_len(125) * 0.3 + stats::rnorm(125)),
  dataset = c(rep("train", 90), rep("test", 30), rep("train", 5)),
  country = c(rep("A", 121), rep("B", 4)),
  climatic_zone = rep(c("cool_dry", "warm_moist", "tropical_wet"), length.out = 125),
  alt = as.character(seq_len(125)), population_density = as.character(seq_len(125) %% 11),
  stringsAsFactors = FALSE)
raw$climatic_zone[121] <- "unknown"
raw$alt[1] <- "-999"
prepared <- prepare_cohort(raw, cfg)
stopifnot(prepared$audit$country_excluded == 4, prepared$audit$climate_excluded == 1,
          prepared$audit$missing_excluded == 1, nrow(prepared$development) == 89,
          nrow(prepared$test) == 30)
reversed <- prepare_cohort(raw[nrow(raw):1, ], cfg)
stopifnot(identical(prepared$prepared, reversed$prepared))
duplicated <- raw
duplicated$id[2] <- duplicated$id[1]
stopifnot(inherits(try(prepare_cohort(duplicated, cfg), silent = TRUE), "try-error"))
bad <- raw
bad$alt[2] <- "invalid"
stopifnot(inherits(try(prepare_cohort(bad, cfg), silent = TRUE), "try-error"))
known_score <- metrics(1:5, rep(0, 5))
stopifnot(abs(known_score$rmse - sqrt(11)) < 1e-12, known_score$mae == 3,
          abs(known_score$r_squared + 4.5) < 1e-12)
set.seed(cfg$seed)
fold <- sample(rep(1:3, length.out = 89))
features <- unlist(cfg$feature_sets$model_1)
# Explicit new configuration also supports protocols predating this field.
cfg$categorical_features <- list(cfg$climate_column)
search <- search_forest(prepared$development, features, fold, cfg, 1L)
stopifnot(length(search$response) == 89, all(is.finite(search$response)),
          nrow(search$fold_scores) == 6, nrow(search$comparison) == 2)
changed <- raw
changed$o3_average_values[changed$dataset == "test"] <- "999999"
changed <- prepare_cohort(changed, cfg)
repeated <- search_forest(changed$development, features, fold, cfg, 1L)
stopifnot(identical(search$parameters, repeated$parameters), identical(search$response, repeated$response))
cat("EXPERIMENT completed\n")
