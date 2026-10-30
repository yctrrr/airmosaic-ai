ml_select_features <- function(context) {
  evalq({
    training <- frame[frame[[cfg$split$column]]==cfg$split$train,,drop=FALSE]
    if (nrow(training)<10L) fail("insufficient_selection_training_rows")
    selection <- cfg$feature_selection
    numeric_features <- setdiff(features,categorical)
    correlations <- if (length(numeric_features)>1L)
      suppressWarnings(stats::cor(training[,numeric_features,drop=FALSE],use="pairwise.complete.obs")) else NULL
    vifs <- stats::setNames(rep(NA_real_,length(numeric_features)),numeric_features)
    if (!is.null(correlations) && all(is.finite(correlations))) {
      vifs <- tryCatch(diag(solve(correlations)),error=function(error) vifs)
    }
    kept <- character()
    records <- list()
    for (feature in features) {
      values <- training[[feature]]
      missing <- mean(is.na(values))
      unique_n <- length(unique(values[!is.na(values)]))
      reason <- "retained"
      if (selection$mode=="train_filter") {
        threshold <- if (is.null(selection$max_missing_fraction)) 0.5 else selection$max_missing_fraction
        minimum <- if (is.null(selection$min_unique)) 2L else selection$min_unique
        correlation_limit <- if (is.null(selection$max_abs_correlation)) 0.95 else selection$max_abs_correlation
        if (missing>threshold) reason <- "training_missingness"
        else if (unique_n<minimum) reason <- "training_near_constant"
        else if (!feature %in% categorical && !is.null(correlations)) {
          previous <- intersect(kept,numeric_features)
          if (length(previous) && any(abs(correlations[feature,previous])>correlation_limit,na.rm=TRUE)) reason <- "training_collinearity"
        }
      }
      if (reason=="retained") kept <- c(kept,feature)
      records[[length(records)+1L]] <- data.frame(feature=feature,training_rows=nrow(training),
        missing_fraction=missing,unique_values=unique_n,vif=if (feature %in% numeric_features) vifs[[feature]] else NA_real_,
        retained=reason=="retained",reason=reason)
    }
    if (!length(kept)) fail("no_features_after_selection")
    features <- kept
    categorical <- intersect(categorical,features)
    if (cfg$analysis=="prediction") {
      explanation_features <- intersect(explanation_features,features)
      if (!length(explanation_features)) fail("no_requested_explanation_feature_retained")
    }
    write_csv(do.call(rbind,records),"feature_selection")
    finish_step("features_selected")
  }, envir=context)
}
