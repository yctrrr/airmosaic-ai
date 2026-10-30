ml_target <- function(context) {
  evalq({
    features <- unlist(cfg$features, use.names=FALSE)
    categorical <- unlist(cfg$categorical_features, use.names=FALSE)
    explanation_features <- unlist(cfg$explanation$features, use.names=FALSE)
    if (!identical(cfg$task_type,"regression") || anyDuplicated(features) ||
        cfg$target %in% features || !all(categorical %in% features)) fail("invalid_target_contract")
    write_json(list(analysis=cfg$analysis,target=cfg$target,unit=cfg$target_unit,
      definition=cfg$target_definition,configured_features=as.list(features),
      excluded_features=cfg$excluded_features,id_column=cfg$id_column,split=cfg$split,
      interpretation_scope=if (cfg$analysis=="prediction") "predictive_association" else "PLR_slope_under_declared_assumptions"),"target_contract")
    finish_step("target_defined")
  }, envir=context)
}
