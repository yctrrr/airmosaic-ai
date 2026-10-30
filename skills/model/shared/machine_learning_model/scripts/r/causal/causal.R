# Cross-fitted partially linear score. Identification remains a declared design.
ml_causal <- function(context) {
  evalq({
    state$current <- "causal"
    suppressPackageStartupMessages(library(mlr3learners))
    design <- cfg$causal
    data <- rbind(subsets$train,subsets$val)
    data <- data[order(data[[cfg$id_column]],method="radix"),,drop=FALSE]
    n <- nrow(data); k <- design$folds
    if (n<max(30L,k*10L)) fail("insufficient_causal_rows")
    data[[design$treatment]] <- data[[design$treatment]]/design$treatment_scale
    seed(7100)
    if (design$resampling$mode=="group") {
      group <- as.character(data[[design$resampling$group_column]])
      if (anyNA(group) || any(!nzchar(trimws(group)))) fail("invalid_causal_groups")
      groups <- sort(unique(group))
      if (length(groups)<max(5L,k)) fail("insufficient_causal_groups")
      group_folds <- stats::setNames(sample(rep(seq_len(k),length.out=length(groups))),groups)
      folds <- unname(group_folds[group])
    } else {
      group <- data[[cfg$id_column]]
      folds <- sample(rep(seq_len(k),length.out=n))
    }
    outcome_hat <- treatment_hat <- rep(NA_real_,n)
    fitted_nuisance <- list()
    fold_audit <- list()
    for (fold in seq_len(k)) {
      train_ids <- which(folds!=fold); test_ids <- which(folds==fold)
      if (length(train_ids)<10L || !length(test_ids)) fail("invalid_causal_fold")
      training <- data[train_ids,,drop=FALSE]; testing <- data[test_ids,,drop=FALSE]
      # Category vocabulary and unknown-level treatment are fitted within fold.
      categorical_state <- list()
      for (feature in categorical) {
        counts <- table(training[[feature]])
        if (!length(counts)) fail("empty_causal_training_feature")
        levels <- sort(names(counts))
        mode <- sort(names(counts)[counts==max(counts)])[[1]]
        unknown <- !testing[[feature]] %in% levels
        if (any(unknown)) {
          if (is.null(cfg$unseen_categories) || cfg$unseen_categories!="train_mode") fail("unseen_causal_fold_category")
          testing[[feature]][unknown] <- mode
        }
        training[[feature]] <- factor(training[[feature]],levels=levels)
        testing[[feature]] <- factor(testing[[feature]],levels=levels)
        categorical_state[[feature]] <- list(levels=as.list(levels),mode=mode,replaced=sum(unknown))
      }
      learners <- list()
      for (response_name in c(cfg$target,design$treatment)) {
        specification <- cfg$models[[1]]
        parameters <- specification$parameters
        offset <- fold*2+as.integer(response_name==design$treatment)
        if (specification$learner=="regr.ranger") {
          if (is.null(parameters$num.trees)) parameters$num.trees <- 100L
          parameters$num.threads <- 1L
          parameters$seed <- (as.double(cfg$seeds$causal)+offset) %% 2147483000+1
        } else parameters$xval <- 0L
        seed(7200+offset)
        learner <- do.call(mlr3::lrn,c(list(specification$learner),parameters))
        task <- mlr3::TaskRegr$new(paste0("nuisance_",fold,"_",offset),
          backend=training[,c(features,response_name),drop=FALSE],target=response_name)
        learner$train(task)
        predicted <- learner$predict_newdata(testing[,features,drop=FALSE])$response
        if (length(predicted)!=length(test_ids) || any(!is.finite(predicted))) fail("invalid_causal_nuisance_prediction")
        if (response_name==cfg$target) outcome_hat[test_ids] <- predicted else treatment_hat[test_ids] <- predicted
        learners[[response_name]] <- learner
      }
      fitted_nuisance[[fold]] <- list(learners=learners,categorical_preprocessing=categorical_state,
        training_keys=training[[cfg$id_column]],held_out_keys=testing[[cfg$id_column]])
      fold_audit[[fold]] <- data.frame(sample_id=testing[[cfg$id_column]],fold=fold,
        group_id=group[test_ids],role="out_of_fold")
    }
    outcome_residual <- data[[cfg$target]]-outcome_hat
    treatment_residual <- data[[design$treatment]]-treatment_hat
    jacobian <- mean(treatment_residual^2)
    if (!is.finite(jacobian) || jacobian<=1e-10) fail("insufficient_residual_treatment_variation")
    coefficient <- mean(treatment_residual*outcome_residual)/jacobian
    influence <- treatment_residual*(outcome_residual-coefficient*treatment_residual)/jacobian
    if (design$resampling$mode=="group") {
      sums <- rowsum(matrix(influence,ncol=1),group,reorder=FALSE)
      g <- nrow(sums)
      variance <- g/(g-1)*sum(sums^2)/n^2
      variance_method <- "independent_cluster_influence_score"
    } else {
      g <- n
      variance <- stats::var(influence)/n
      variance_method <- "independent_unit_influence_score"
    }
    standard_error <- sqrt(variance)
    if (!is.finite(coefficient) || !is.finite(standard_error) || standard_error<=0) fail("degenerate_causal_inference")
    write_json(list(estimator="cross_fitted_PLR_partialling_out",estimand=design$estimand,
      coefficient=coefficient,std_error=standard_error,
      confidence_interval_95=c(coefficient-1.959963984540054*standard_error,coefficient+1.959963984540054*standard_error),
      n=n,folds=k,clusters=g,cross_fitted=TRUE,variance_method=variance_method,
      outcome_unit=cfg$target_unit,treatment_unit=design$treatment_unit,treatment_scale=design$treatment_scale,
      residual_treatment_variance=jacobian,adjustment_set=as.list(features),sample_scope="train_and_val_only",
      assumptions_status="declared_not_verified",scientific_review="pending"),"causal_effect")
    write_csv(data.frame(sample_id=data[[cfg$id_column]],fold=folds,group_id=group,
      outcome=data[[cfg$target]],treatment=data[[design$treatment]],outcome_hat=outcome_hat,treatment_hat=treatment_hat,
      outcome_residual=outcome_residual,treatment_residual=treatment_residual,influence=influence),"causal_residuals")
    write_csv(do.call(rbind,fold_audit),"causal_folds")
    saveRDS(list(nuisance=fitted_nuisance,configuration=cfg),artifact_path("causal_models"),version=3)
    finish_step("causal_effect_estimated")
  },envir=context)
}
