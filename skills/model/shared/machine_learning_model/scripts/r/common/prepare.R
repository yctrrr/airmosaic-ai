ml_prepare <- function(context) {
  evalq({
    # Read once as character so numeric category codes and keys are not guessed.
    raw <- utils::read.csv(input, check.names = FALSE, colClasses = "character",
                           na.strings = "", nrows = 100001L, stringsAsFactors = FALSE)
    extra <- if (cfg$analysis == "causal_plr") c(cfg$causal$treatment, cfg$causal$resampling$group_column) else character()
    required <- unique(c(cfg$id_column, cfg$split$column, cfg$target, features, extra))
    if (nrow(raw) > 100000L || anyDuplicated(names(raw)) ||
        !all(required %in% names(raw))) fail("invalid_input_columns_or_size")
    ids <- raw[[cfg$id_column]]
    if (anyNA(ids) || any(!nzchar(trimws(ids))) || anyDuplicated(ids)) fail("invalid_sample_keys")
    split_labels <- unlist(cfg$split[c("train", "val", "test")], use.names = FALSE)
    splits <- raw[[cfg$split$column]]
    if (anyNA(splits) || !all(splits %in% split_labels)) fail("unknown_split_labels")
    frame <- raw[, required, drop = FALSE]
    sentinels <- as.numeric(unlist(cfg$missing$sentinels, use.names = FALSE))
    for (name in unique(c(cfg$target, features, if (cfg$analysis == "causal_plr") cfg$causal$treatment else character()))) {
      values <- frame[[name]]
      blank <- is.na(values) | !nzchar(trimws(values))
      numeric_values <- suppressWarnings(as.numeric(values))
      missing <- blank | (!is.na(numeric_values) & numeric_values %in% sentinels)
      if (name %in% categorical) {
        values[missing] <- NA_character_
        frame[[name]] <- values
      } else {
        if (any(!missing & !is.finite(numeric_values))) fail("invalid_numeric_values")
        numeric_values[missing] <- NA_real_
        frame[[name]] <- numeric_values
      }
    }
    state$current <- "select"
    ml_select_features(context)
    state$current <- "prepare"
    required <- unique(c(cfg$id_column, cfg$split$column, cfg$target, features, extra))
    frame <- frame[, required, drop = FALSE]
    cohort <- list()
    subsets <- list()
    for (index in seq_along(split_labels)) {
      split <- c("train", "val", "test")[[index]]
      rows <- frame[frame[[cfg$split$column]] == split_labels[[index]], , drop = FALSE]
      original_n <- nrow(rows)
      rows <- rows[!is.na(rows[[cfg$target]]), , drop = FALSE]
      target_valid_n <- nrow(rows)
      if (cfg$missing$policy == "drop") rows <- rows[stats::complete.cases(rows[, unique(c(features, if (cfg$analysis == "causal_plr") cfg$causal$treatment else character())), drop = FALSE]), , drop = FALSE]
      valid_n <- nrow(rows)
      if (valid_n < if (split == "train") 10L else if (cfg$analysis == "causal_plr") 0L else 5L) fail("insufficient_split_rows")
      rows <- rows[order(rows[[cfg$id_column]], method = "radix"), , drop = FALSE]
      seed(index)
      chosen <- if (nrow(rows)) sort(sample.int(nrow(rows), min(nrow(rows), cfg$row_limits[[split]]))) else integer()
      subsets[[split]] <- rows[chosen, , drop = FALSE]
      cohort[[split]] <- list(source_rows = original_n, valid_target_rows = target_valid_n,
                              valid_feature_rows = valid_n, selected_rows = length(chosen))
    }
    preprocessing <- list(policy = cfg$missing$policy, numeric_fill = list(),
                           categorical_fill = list(), categorical_levels = list(),
                           unseen_categories = if (is.null(cfg$unseen_categories)) "error" else cfg$unseen_categories,
                           unseen_category_counts = list(train = list(), val = list(), test = list()))
    if (cfg$analysis == "prediction") {
    for (feature in features) {
      train_values <- subsets$train[[feature]]
      if (feature %in% categorical) {
        observed <- train_values[!is.na(train_values)]
        if (!length(observed)) fail("empty_training_feature")
        counts <- table(observed)
        mode <- sort(names(counts)[counts == max(counts)])[[1]]
        levels <- sort(unique(observed))
        preprocessing$categorical_fill[[feature]] <- mode
        preprocessing$categorical_levels[[feature]] <- as.list(levels)
        for (split in names(subsets)) {
          values <- subsets[[split]][[feature]]
          if (cfg$missing$policy == "train_median_mode") values[is.na(values)] <- mode
          unknown <- !is.na(values) & !values %in% levels
          preprocessing$unseen_category_counts[[split]][[feature]] <- sum(unknown)
          if (any(unknown)) {
            if (preprocessing$unseen_categories != "train_mode") fail("unseen_categorical_level")
            values[unknown] <- mode
          }
          subsets[[split]][[feature]] <- factor(values, levels = levels)
        }
      } else {
        observed <- train_values[!is.na(train_values)]
        if (!length(observed)) fail("empty_training_feature")
        fill <- stats::median(observed)
        preprocessing$numeric_fill[[feature]] <- fill
        if (cfg$missing$policy == "train_median_mode") {
          for (split in names(subsets)) {
            missing <- is.na(subsets[[split]][[feature]])
            subsets[[split]][[feature]][missing] <- fill
          }
        }
      }
    }
    } else { preprocessing <- list(policy="complete_case", fitted_transforms="within_cross_fitting_only") }
    prepared <- do.call(rbind, subsets)
    write_csv(prepared, "prepared_data")
    write_json(list(id_column = cfg$id_column, target = cfg$target, features = as.list(features),
                    split = cfg$split, cohort = cohort, preprocessing = preprocessing),
               "preprocessing")
    finish_step("prepared")


  }, envir = context)
}
