# File roles are resolved from a normalized, validated task snapshot.
state <- new.env(parent=emptyenv())
state$out <- NULL
state$cfg <- NULL
state$completed <- character()
state$current <- "target"
fail <- function(code) stop(structure(list(message=code, call=NULL, code=code), class=c("workflow_error","error","condition")))
artifact_path <- function(role) {
  value <- state$cfg$output_files[[role]]
  if (is.null(value) || grepl("[\\\\:]", value) || startsWith(value,"/") || any(strsplit(value,"/",fixed=TRUE)[[1]] %in% c("..",".",".git",".airmosaic","auth","secrets","credentials"))) fail("invalid_artifact_relative_path")
  path <- file.path(state$out,value)
  dir.create(dirname(path),recursive=TRUE,showWarnings=FALSE)
  path
}
write_json <- function(value,role) {
  path <- artifact_path(role)
  if (role != "status" && file.exists(path)) fail("artifact_already_exists")
  jsonlite::write_json(value,path,auto_unbox=TRUE,pretty=TRUE,digits=16,na="null",null="null")
}
write_csv <- function(value,role) {
  path <- artifact_path(role)
  if (file.exists(path)) fail("artifact_already_exists")
  utils::write.csv(value,path,row.names=FALSE,na="",fileEncoding="UTF-8")
}
write_status <- function(status,error_code=NULL) {
  write_json(list(schema_version=1,capability_id="ml_regression",version="2.0.0",analysis=state$cfg$analysis,
    status=status,current_step=state$current,steps=as.list(state$completed),error_code=error_code),"status")
}
finish_step <- function(name) { state$completed <- c(state$completed,name); write_status("running") }
required_roles <- function(cfg) {
  roles <- c("target_contract","prepared_data","preprocessing","feature_selection","provenance","reproducibility","status")
  if (cfg$analysis=="causal_plr") return(c(roles,"dag","dag_plot","causal_effect","causal_residuals","causal_folds","causal_models"))
  roles <- c(roles,"candidates","model","predictions","metrics")
  methods <- unlist(cfg$explanation$methods,use.names=FALSE)
  if ("permutation" %in% methods) roles <- c(roles,"permutation","importance_plot")
  if (any(c("pdp","ice") %in% methods)) roles <- c(roles,"dependence_plot")
  unique(c(roles,intersect(methods,c("pdp","ice","shap"))))
}
metrics <- function(truth, response) {
  if (length(truth) < 5L || length(response) != length(truth) ||
      any(!is.finite(truth)) || any(!is.finite(response))) fail("invalid_predictions")
  residual <- truth - response
  denominator <- sum((truth - mean(truth))^2)
  list(n = length(truth), rmse = sqrt(mean(residual^2)), mae = mean(abs(residual)),
       r_squared = if (denominator > 0) 1 - sum(residual^2) / denominator else NA_real_)
}
