ml_explain <- function(context) {
  evalq({
    state$current <- "explain"
    methods <- unlist(cfg$explanation$methods,use.names=FALSE)
    seed(1000)
    background_rows <- sort(sample.int(nrow(subsets$train),min(nrow(subsets$train),cfg$explanation$background_rows)))
    background <- subsets$train[background_rows,features,drop=FALSE]
    validation_rows <- sort(sample.int(nrow(subsets$val),min(nrow(subsets$val),cfg$explanation$validation_rows)))
    validation <- subsets$val[validation_rows,features,drop=FALSE]
    validation_truth <- subsets$val[[cfg$target]][validation_rows]
    predict_values <- function(values) {
      response <- selected$predict_newdata(values)$response
      if (length(response)!=nrow(values) || any(!is.finite(response))) fail("invalid_explanation_predictions")
      response
    }
    if ("permutation" %in% methods) {
      score <- function(values) metrics(validation_truth,predict_values(values))[[cfg$selection_metric]]
      original <- score(validation)
      importance <- list()
      for (index in seq_along(explanation_features)) {
        feature <- explanation_features[[index]]
        increases <- numeric(cfg$explanation$permutation_repeats)
        for (repeat_id in seq_along(increases)) {
          seed(2000+index*100+repeat_id)
          permuted <- validation
          permuted[[feature]] <- permuted[[feature]][sample.int(nrow(permuted))]
          increases[[repeat_id]] <- score(permuted)-original
        }
        importance[[index]] <- data.frame(feature=feature,metric=cfg$selection_metric,
          mean_increase=mean(increases),sd_increase=if(length(increases)>1) stats::sd(increases) else 0,
          repeats=length(increases),validation_rows=nrow(validation))
      }
      importance <- do.call(rbind,importance)
      write_csv(importance,"permutation")
      grDevices::png(artifact_path("importance_plot"),width=1000,height=650)
      graphics::par(mar=c(5,14,3,2))
      graphics::barplot(importance$mean_increase,names.arg=importance$feature,horiz=TRUE,las=1,
        xlab=paste("Validation",cfg$selection_metric,"increase"))
      grDevices::dev.off()
    }
    if (any(c("pdp","ice") %in% methods)) {
      partial <- list(); individual <- list()
      for (feature in explanation_features) {
        training_values <- subsets$train[[feature]]
        grid <- if (feature %in% categorical) levels(training_values) else
          unique(as.numeric(stats::quantile(training_values,probs=seq(0.05,0.95,length.out=cfg$explanation$pdp_points),names=FALSE)))
        if (length(grid)>32L) fail("categorical_pdp_budget_exceeded")
        for (value in grid) {
          changed <- background
          changed[[feature]] <- if(feature %in% categorical)
            factor(rep(value,nrow(changed)),levels=levels(training_values)) else rep(as.numeric(value),nrow(changed))
          response <- predict_values(changed)
          partial[[length(partial)+1L]] <- data.frame(feature=feature,
            value_type=if(feature %in% categorical) "categorical" else "numeric",value=as.character(value),
            mean_prediction=mean(response),background_rows=nrow(background))
          individual[[length(individual)+1L]] <- data.frame(feature=feature,value=as.character(value),
            sample_id=subsets$train[[cfg$id_column]][background_rows],prediction=response)
        }
      }
      partial <- do.call(rbind,partial); individual <- do.call(rbind,individual)
      if ("pdp" %in% methods) write_csv(partial,"pdp")
      if ("ice" %in% methods) write_csv(individual,"ice")
      grDevices::png(artifact_path("dependence_plot"),width=1200,height=350*length(explanation_features))
      graphics::par(mfrow=c(length(explanation_features),1),mar=c(5,5,2,1))
      for (feature in explanation_features) {
        values <- partial[partial$feature==feature,,drop=FALSE]
        if (values$value_type[[1]]=="numeric") {
          graphics::plot(as.numeric(values$value),values$mean_prediction,type="b",xlab=feature,ylab=cfg$target)
        } else graphics::barplot(values$mean_prediction,names.arg=values$value,xlab=feature,ylab=cfg$target)
      }
      grDevices::dev.off()
    }
    # Empirical-background permutation Shapley estimates, not TreeSHAP or causal SHAP.
    if ("shap" %in% methods) {
      rows <- seq_len(min(nrow(validation),cfg$explanation$shap_rows))
      baseline <- mean(predict_values(background))
      shap <- list()
      for (row in rows) {
        contributions <- stats::setNames(numeric(length(features)),features)
        for (permutation_id in seq_len(cfg$explanation$shap_permutations)) {
          seed(5000+row*100+permutation_id)
          order <- sample(features,length(features))
          changed <- background; previous <- baseline
          for (feature in order) {
            changed[[feature]] <- validation[[feature]][rep(row,nrow(background))]
            current <- mean(predict_values(changed))
            contributions[[feature]] <- contributions[[feature]]+current-previous
            previous <- current
          }
        }
        contributions <- contributions/cfg$explanation$shap_permutations
        response <- predict_values(validation[row,,drop=FALSE])
        if (abs(sum(contributions)+baseline-response)>1e-8*max(1,abs(response))) fail("shap_additivity_failed")
        shap[[row]] <- data.frame(sample_id=subsets$val[[cfg$id_column]][validation_rows[row]],feature=features,
          contribution=unname(contributions),baseline=baseline,prediction=response,
          permutations=cfg$explanation$shap_permutations,scope="empirical_background_predictive")
      }
      write_csv(do.call(rbind,shap),"shap")
    }
    finish_step("predictions_explained")
  },envir=context)
}
